# -*- coding: utf-8 -*-

"""Offline stock clustering into stock_cluster / stock_cluster_item (Python 3)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

import pandas as pd

from app.models import Instrument, StockCluster, StockClusterItem
from core.db import session_scope

logger = logging.getLogger(__name__)

try:
    from sklearn.cluster import AffinityPropagation
except ImportError:
    AffinityPropagation = None

DEFAULT_RATE_BEGIN_DATE = '2018-01-01'


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
) -> ClusterGroups:
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
        return ClusterGroups()

    data = pd.concat(series_map, axis=1)
    data = data.ffill().fillna(0.01).astype('float64')

    matrix = data.T.values
    model = AffinityPropagation(affinity='euclidean')
    labels = model.fit_predict(matrix)

    groups = ClusterGroups()
    for index, label in enumerate(labels):
        code = str(data.columns[index])
        name = str(instruments.at[code, 'name']) if code in instruments.index else code
        cluster = groups.existed_cluster(int(label))
        if cluster is None:
            cluster = ClusterGroup(code=code, name=name, label=int(label))
            cluster.add(ClusterItem(code=code, name=name, corr=1.0))
            groups.add(cluster)
        else:
            cluster.add(ClusterItem(code=code, name=name, corr=1.0))

    return groups


def cluster_fundamentals(instruments: pd.DataFrame) -> ClusterGroups:
    """Cluster by numeric fundamentals (pe, pb, roe-style columns on Instrument)."""
    if AffinityPropagation is None:
        raise RuntimeError('scikit-learn is required for cluster_compute')

    numeric_cols = [
        'pe', 'pb', 'outstanding', 'totals', 'total_assets', 'liquid_assets',
        'fixed_assets', 'esp', 'bvps', 'gpr', 'npr',
    ]
    available = [col for col in numeric_cols if col in instruments.columns]
    if not available:
        return ClusterGroups()

    data = instruments[available].apply(pd.to_numeric, errors='coerce').fillna(0.0)
    matrix = data.values
    model = AffinityPropagation(affinity='euclidean')
    labels = model.fit_predict(matrix)

    groups = ClusterGroups()
    for index, label in enumerate(labels):
        code = str(instruments.index[index])
        name = str(instruments.iloc[index].get('name', code))
        cluster = groups.existed_cluster(int(label))
        if cluster is None:
            cluster = ClusterGroup(code=code, name=name, label=int(label))
            cluster.add(ClusterItem(code=code, name=name, corr=1.0))
            groups.add(cluster)
        else:
            cluster.add(ClusterItem(code=code, name=name, corr=1.0))

    return groups


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
            if cluster.code not in cluster.stocks:
                session.add(
                    StockClusterItem(
                        section=section,
                        parent_code=cluster.code,
                        code=cluster.code,
                        name=cluster.name,
                        corr=1.0,
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
    codes = frame[code_col].astype(str).str.zfill(6)
    names = frame[name_col].astype(str)
    return pd.DataFrame({'code': codes, 'name': names}).set_index('code')


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

    groups = cluster_by_price_series(
        instruments,
        day_file_path,
        index_file_path=index_file_path,
        index_code=index_symbol,
    )
    if not groups.items:
        return {'status': 'skipped', 'reason': 'insufficient price data', 'section': section}

    rows = write_clusters_to_db(groups, section)
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
    groups = cluster_fundamentals(frame)
    if not groups.items:
        return {'status': 'skipped', 'reason': 'clustering produced no groups', 'section': industry}

    count = write_clusters_to_db(groups, industry)
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
