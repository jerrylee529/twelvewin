# -*- coding: utf-8 -*-

"""Offline stock clustering into stock_cluster / stock_cluster_item (Python 3)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd

from app.models import Instrument, StockCluster, StockClusterChart, StockClusterItem
from core.db import session_scope
from core.stock_codes import normalize_stock_code

logger = logging.getLogger(__name__)

try:
    from sklearn.cluster import AffinityPropagation
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
except ImportError:
    AffinityPropagation = None
    PCA = None
    TSNE = None

DEFAULT_RATE_BEGIN_DATE = '2018-01-01'
CHART_EDGE_THRESHOLD = 0.5
CHART_MAX_EDGES = 800
CHART_HEATMAP_MAX_STOCKS = 120


@dataclass
class ClusterItem:
    code: str
    name: str
    corr: float


@dataclass
class ClusterGroup:
    code: str
    name: str
    label: int
    stocks: Dict[str, ClusterItem] = field(default_factory=dict)

    def add(self, item: ClusterItem) -> None:
        self.stocks[item.code] = item


@dataclass
class ClusterGroups:
    items: List[ClusterGroup] = field(default_factory=list)

    def existed_cluster(self, label: int) -> Optional[ClusterGroup]:
        for cluster in self.items:
            if cluster.label == label:
                return cluster
        return None

    def add(self, cluster: ClusterGroup) -> None:
        self.items.append(cluster)


def assign_cluster_correlations(groups: ClusterGroups, corr_matrix: pd.DataFrame) -> None:
    """Set each member's ``corr`` to its Pearson correlation with the cluster center."""
    if corr_matrix.empty:
        return

    for cluster in groups.items:
        center = cluster.code
        if center not in corr_matrix.columns:
            continue

        center_corrs = corr_matrix[center]
        for code, item in cluster.stocks.items():
            if code not in center_corrs.index:
                continue
            value = center_corrs[code]
            item.corr = 1.0 if code == center else float(value if pd.notna(value) else 0.0)


def lookup_instrument_name(instruments: pd.DataFrame, code: str) -> str:
    """Return a single display name even when the index has duplicate codes."""
    if code not in instruments.index:
        return code

    value = instruments.at[code, 'name']
    if isinstance(value, pd.Series):
        value = value.iloc[0]

    name = str(value).strip()
    if not name or name.lower() in {'nan', 'none', 'nat'}:
        return code
    return name


def compute_rate_series(frame, *, begin_date: str, end_date: str) -> Optional[pd.Series]:
    """Build daily return series (percent) from a ``date``/``close`` bar frame."""
    if frame is None or frame.empty or 'close' not in frame.columns:
        return None

    working = frame.copy()
    working['date'] = pd.to_datetime(working['date'], errors='coerce')
    working = working.set_index('date').sort_index()
    working = working.loc[begin_date:end_date]
    working['close'] = pd.to_numeric(working['close'], errors='coerce')
    working = working.ffill()
    if working.empty:
        return None

    value = working['close'] - working['close'].shift(1)
    value = value.ffill()
    return (value / working['close']) * 100


def read_rate_series(
    code,
    session,
    *,
    end_date: str,
    begin_date: str = DEFAULT_RATE_BEGIN_DATE,
) -> Optional[pd.Series]:
    from day_data import load_day_since_dataframe

    frame = load_day_since_dataframe(
        code,
        session=session,
        since_date=begin_date,
        columns=('date', 'close'),
    )
    return compute_rate_series(frame, begin_date=begin_date, end_date=end_date)


def build_rate_series_map(
    instruments: pd.DataFrame,
    session,
    *,
    end_date: str,
    index_code: Optional[str] = None,
) -> Dict[str, pd.Series]:
    """Load return series for all instruments in one DB session."""
    index_series = None
    if index_code:
        index_series = read_rate_series(index_code, session, end_date=end_date)

    series_map: Dict[str, pd.Series] = {}
    total = len(instruments.index)
    for position, code in enumerate(instruments.index, start=1):
        if position % 100 == 0 or position == total:
            logger.info('cluster rate series: %d / %d', position, total)

        series = read_rate_series(str(code), session, end_date=end_date)
        if series is None:
            continue
        if index_series is not None:
            series = series - index_series
        series_map[str(code)] = series

    return series_map


def cluster_by_price_series(
    instruments: pd.DataFrame,
    day_file_path: str,
    *,
    index_file_path: Optional[str] = None,
    index_code: Optional[str] = None,
) -> Tuple[ClusterGroups, Optional[pd.DataFrame]]:
    """Cluster instruments using daily return series (optional index-relative)."""
    del day_file_path, index_file_path  # bars are loaded from Postgres via day_data

    if AffinityPropagation is None:
        raise RuntimeError('scikit-learn is required for cluster_compute (install requirements-analysis.txt)')

    from market_calendar import resolve_download_end_date

    with session_scope() as session:
        end_date, end_source = resolve_download_end_date(session)
        logger.info('cluster end_date=%s (source=%s)', end_date, end_source)
        series_map = build_rate_series_map(
            instruments,
            session,
            end_date=end_date,
            index_code=index_code,
        )

    if len(series_map) < 2:
        return ClusterGroups(), None

    data = pd.concat(series_map, axis=1)
    data = data.ffill().fillna(0.01).astype('float64')

    matrix = data.T.values
    model = AffinityPropagation(affinity='euclidean')
    labels = model.fit_predict(matrix)

    groups = ClusterGroups()
    for index, label in enumerate(labels):
        code = normalize_stock_code(str(data.columns[index]))
        name = lookup_instrument_name(instruments, code)
        cluster = groups.existed_cluster(int(label))
        if cluster is None:
            cluster = ClusterGroup(code=code, name=name, label=int(label))
            cluster.add(ClusterItem(code=code, name=name, corr=1.0))
            groups.add(cluster)
        else:
            cluster.add(ClusterItem(code=code, name=name, corr=1.0))

    assign_cluster_correlations(groups, data.corr())
    return groups, data


def cluster_fundamentals(instruments: pd.DataFrame) -> Tuple[ClusterGroups, Optional[pd.DataFrame]]:
    """Cluster by numeric fundamentals (pe, pb, roe-style columns on Instrument)."""
    if AffinityPropagation is None:
        raise RuntimeError('scikit-learn is required for cluster_compute')

    numeric_cols = [
        'pe', 'pb', 'outstanding', 'totals', 'total_assets', 'liquid_assets',
        'fixed_assets', 'esp', 'bvps', 'gpr', 'npr',
    ]
    available = [col for col in numeric_cols if col in instruments.columns]
    if not available:
        return ClusterGroups(), None

    data = instruments[available].apply(pd.to_numeric, errors='coerce').fillna(0.0)
    matrix = data.values
    model = AffinityPropagation(affinity='euclidean')
    labels = model.fit_predict(matrix)

    groups = ClusterGroups()
    for index, label in enumerate(labels):
        code = normalize_stock_code(str(instruments.index[index]))
        name = lookup_instrument_name(instruments, code)
        cluster = groups.existed_cluster(int(label))
        if cluster is None:
            cluster = ClusterGroup(code=code, name=name, label=int(label))
            cluster.add(ClusterItem(code=code, name=name, corr=1.0))
            groups.add(cluster)
        else:
            cluster.add(ClusterItem(code=code, name=name, corr=1.0))

    assign_cluster_correlations(groups, data.T.corr())
    return groups, data


def _compute_embedding(matrix) -> List[List[float]]:
    """Project high-dimensional stock features into 2D coordinates."""
    import numpy as np

    sample_count = matrix.shape[0]
    if sample_count == 0:
        return []
    if sample_count == 1:
        return [[0.0, 0.0]]

    working = matrix
    if PCA is not None and working.shape[1] > 30 and sample_count > 2:
        component_count = min(30, sample_count - 1, working.shape[1])
        working = PCA(n_components=component_count, random_state=42).fit_transform(working)

    if sample_count < 4 or TSNE is None:
        if PCA is None:
            return working[:, :2].tolist() if working.shape[1] >= 2 else [[float(working[0, 0]), 0.0]]
        reduced = PCA(n_components=min(2, sample_count, working.shape[1]), random_state=42).fit_transform(working)
        if reduced.shape[1] == 1:
            reduced = np.column_stack([reduced[:, 0], np.zeros(sample_count)])
        return reduced.tolist()

    perplexity = min(30, max(2, sample_count - 1))
    tsne = TSNE(
        n_components=2,
        random_state=42,
        perplexity=perplexity,
        init='pca',
        learning_rate='auto',
    )
    return tsne.fit_transform(working).tolist()


def _build_code_cluster_map(groups: ClusterGroups) -> Dict[str, dict]:
    mapping: Dict[str, dict] = {}
    for display_id, cluster in enumerate(groups.items, start=1):
        for code in cluster.stocks:
            mapping[code] = {
                'id': display_id,
                'centerCode': cluster.code,
                'centerName': cluster.name,
            }
    return mapping


def _select_heatmap_codes(codes: List[str], code_cluster_map: Dict[str, dict]) -> List[str]:
    if len(codes) <= CHART_HEATMAP_MAX_STOCKS:
        return codes

    cluster_sizes: Dict[int, int] = {}
    for meta in code_cluster_map.values():
        cluster_sizes[meta['id']] = cluster_sizes.get(meta['id'], 0) + 1

    ranked = sorted(
        codes,
        key=lambda code: (
            -cluster_sizes.get(code_cluster_map.get(code, {'id': 0})['id'], 0),
            code_cluster_map.get(code, {'id': 0})['id'],
            code,
        ),
    )
    return ranked[:CHART_HEATMAP_MAX_STOCKS]


def build_cluster_chart_payload(
    groups: ClusterGroups,
    data: pd.DataFrame,
    *,
    value_mode: str,
) -> dict:
    """Build scatter/network/heatmap payload for the cluster chart UI."""
    if data is None or data.empty or not groups.items:
        return {}

    if value_mode == 'returns':
        feature_frame = data
        corr_matrix = data.corr()
        embedding_matrix = data.T.values
    else:
        feature_frame = data
        corr_matrix = data.T.corr()
        embedding_matrix = data.values

    codes = [normalize_stock_code(str(code)) for code in feature_frame.columns]
    if value_mode == 'fundamentals':
        codes = [normalize_stock_code(str(code)) for code in feature_frame.index]

    code_cluster_map = _build_code_cluster_map(groups)
    coords = _compute_embedding(embedding_matrix)

    nodes = []
    for index, code in enumerate(codes):
        cluster_meta = code_cluster_map.get(code, {'id': 0, 'centerCode': code, 'centerName': code})
        cluster = next((item for item in groups.items if item.code == cluster_meta['centerCode']), None)
        point_x, point_y = coords[index] if index < len(coords) else [0.0, 0.0]
        nodes.append(
            {
                'code': code,
                'name': cluster.stocks[code].name if cluster and code in cluster.stocks else code,
                'clusterId': cluster_meta['id'],
                'clusterName': cluster_meta['centerName'],
                'x': round(float(point_x), 4),
                'y': round(float(point_y), 4),
            }
        )

    edges = []
    for row_index, source_code in enumerate(codes):
        for col_index in range(row_index + 1, len(codes)):
            target_code = codes[col_index]
            if source_code not in corr_matrix.index or target_code not in corr_matrix.columns:
                continue
            corr_value = corr_matrix.at[source_code, target_code]
            if pd.isna(corr_value) or float(corr_value) < CHART_EDGE_THRESHOLD:
                continue
            edges.append(
                {
                    'source': source_code,
                    'target': target_code,
                    'corr': round(float(corr_value), 4),
                }
            )

    edges.sort(key=lambda item: item['corr'], reverse=True)
    if len(edges) > CHART_MAX_EDGES:
        edges = edges[:CHART_MAX_EDGES]

    heatmap_codes = _select_heatmap_codes(codes, code_cluster_map)
    ordered_codes = sorted(
        heatmap_codes,
        key=lambda code: (code_cluster_map.get(code, {'id': 0})['id'], code),
    )
    heatmap_labels = [
        {
            'code': code,
            'name': next((node['name'] for node in nodes if node['code'] == code), code),
            'clusterId': code_cluster_map.get(code, {'id': 0})['id'],
        }
        for code in ordered_codes
    ]
    heatmap_values = []
    for row_code in ordered_codes:
        row_values = []
        for col_code in ordered_codes:
            if row_code in corr_matrix.index and col_code in corr_matrix.columns:
                value = corr_matrix.at[row_code, col_code]
                row_values.append(round(float(value), 4) if pd.notna(value) else 0.0)
            else:
                row_values.append(0.0)
        heatmap_values.append(row_values)

    clusters = [
        {
            'id': display_id,
            'code': cluster.code,
            'name': cluster.name,
            'size': len(cluster.stocks),
        }
        for display_id, cluster in enumerate(groups.items, start=1)
    ]

    return {
        'nodes': nodes,
        'edges': edges,
        'heatmap': {
            'labels': heatmap_labels,
            'values': heatmap_values,
        },
        'clusters': clusters,
        'meta': {
            'edgeThreshold': CHART_EDGE_THRESHOLD,
            'stockCount': len(codes),
            'valueMode': value_mode,
        },
    }


def write_cluster_chart_to_db(section: str, payload: dict) -> None:
    if not payload:
        return

    import datetime

    with session_scope() as session:
        existing = session.query(StockClusterChart).filter_by(section=section).one_or_none()
        encoded = json.dumps(payload, ensure_ascii=False)
        if existing is None:
            session.add(StockClusterChart(section=section, payload=encoded))
        else:
            existing.payload = encoded
            existing.update_time = datetime.datetime.now()


def write_clusters_to_db(groups: ClusterGroups, section: str) -> int:
    """Replace cluster rows for ``section`` and persist new clusters."""
    with session_scope() as session:
        session.query(StockClusterItem).filter(StockClusterItem.section == section).delete()
        session.query(StockCluster).filter(StockCluster.section == section).delete()

        count = 0
        for cluster in groups.items:
            session.add(StockCluster(section=section, code=cluster.code, name=cluster.name))
            for item in cluster.stocks.values():
                session.add(
                    StockClusterItem(
                        section=section,
                        parent_code=cluster.code,
                        code=item.code,
                        name=item.name,
                        corr=item.corr,
                    )
                )
                count += 1

    return count


def _instruments_frame(codes: Iterable[str], names: Dict[str, str]) -> pd.DataFrame:
    rows = [{'code': code, 'name': names.get(code, code)} for code in codes]
    frame = pd.DataFrame(rows).set_index('code')
    return frame


def _load_index_constituents(index_symbol: str) -> pd.DataFrame:
    try:
        import akshare as ak
    except ImportError:
        logger.warning('akshare not installed; skip index %s', index_symbol)
        return pd.DataFrame()

    try:
        frame = ak.index_stock_cons(symbol=index_symbol)
    except Exception as exc:
        logger.warning('failed to load index %s: %s', index_symbol, exc)
        return pd.DataFrame()

    if frame is None or frame.empty:
        return pd.DataFrame()

    code_col = '品种代码' if '品种代码' in frame.columns else frame.columns[0]
    name_col = '品种名称' if '品种名称' in frame.columns else (frame.columns[1] if len(frame.columns) > 1 else code_col)
    codes = frame[code_col].map(normalize_stock_code)
    names = frame[name_col].astype(str).str.strip()
    result = pd.DataFrame({'code': codes, 'name': names})
    result = result[result['code'] != ''].drop_duplicates(subset='code', keep='first')
    duplicate_count = len(codes) - len(result)
    if duplicate_count > 0:
        logger.warning(
            'index %s constituents contain %d duplicate codes; keeping first occurrence',
            index_symbol,
            duplicate_count,
        )
    return result.set_index('code')


def run_index_section(
    section: str,
    index_symbol: str,
    *,
    day_file_path: str,
    index_file_path: str,
) -> dict:
    instruments = _load_index_constituents(index_symbol)
    if instruments.empty:
        return {'status': 'skipped', 'reason': 'no index constituents', 'section': section}

    groups, data = cluster_by_price_series(
        instruments,
        day_file_path,
        index_file_path=index_file_path,
        index_code=index_symbol,
    )
    if not groups.items:
        return {'status': 'skipped', 'reason': 'insufficient price data', 'section': section}

    rows = write_clusters_to_db(groups, section)
    if data is not None:
        write_cluster_chart_to_db(
            section,
            build_cluster_chart_payload(groups, data, value_mode='returns'),
        )
    return {'status': 'ok', 'section': section, 'clusters': len(groups.items), 'items': rows}


def _load_industry_fundamental_rows(industry: str) -> List[dict]:
    """Load instrument fundamentals as plain dicts (safe outside SQLAlchemy session)."""
    with session_scope() as session:
        records = (
            session.query(Instrument)
            .filter(Instrument.industry == industry)
            .all()
        )
        return [
            {
                'code': record.code,
                'name': record.name,
                'pe': record.pe,
                'pb': record.pb,
                'outstanding': record.outstanding,
                'totals': record.totals,
                'total_assets': record.total_assets,
                'liquid_assets': record.liquid_assets,
                'fixed_assets': record.fixed_assets,
                'esp': record.esp,
                'bvps': record.bvps,
                'gpr': record.gpr,
                'npr': record.npr,
            }
            for record in records
        ]


def run_industry_section(industry: str) -> dict:
    rows = _load_industry_fundamental_rows(industry)
    if not rows:
        return {'status': 'skipped', 'reason': 'no instruments', 'section': industry}

    frame = pd.DataFrame(rows).set_index('code')
    groups, data = cluster_fundamentals(frame)
    if not groups.items:
        return {'status': 'skipped', 'reason': 'clustering produced no groups', 'section': industry}

    count = write_clusters_to_db(groups, industry)
    if data is not None:
        write_cluster_chart_to_db(
            industry,
            build_cluster_chart_payload(groups, data, value_mode='fundamentals'),
        )
    return {'status': 'ok', 'section': industry, 'clusters': len(groups.items), 'items': count}


def run_all_industry_sections() -> dict:
    with session_scope() as session:
        industries = [
            row[0]
            for row in session.query(Instrument.industry).distinct().all()
            if row[0]
        ]

    summary = {}
    for industry in industries:
        summary[industry] = run_industry_section(industry)
    return summary


def run_cluster_pipeline(*, day_file_path: str, index_file_path: str) -> dict:
    """Run index and industry clustering."""
    summary = {
        'sz50': run_index_section('sz50', '000016', day_file_path=day_file_path, index_file_path=index_file_path),
        'hs300': run_index_section('hs300', '000300', day_file_path=day_file_path, index_file_path=index_file_path),
        'zz500': run_index_section('zz500', '000905', day_file_path=day_file_path, index_file_path=index_file_path),
        'industries': run_all_industry_sections(),
    }
    return summary
