# -*- coding: utf-8 -*-

"""Offline stock clustering into stock_cluster / stock_cluster_item (Python 3)."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from app.models import Instrument, StockCluster, StockClusterItem
from core.db import session_scope

logger = logging.getLogger(__name__)

try:
    from sklearn.cluster import AffinityPropagation
except ImportError:
    AffinityPropagation = None


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


def _read_rate_series(day_file_path: str, code: str, begin_date: str = '2018-01-01') -> Optional[pd.Series]:
    from day_data import day_data_available, load_day_dataframe

    if not day_data_available(code):
        return None

    frame = load_day_dataframe(code)
    if frame.empty or 'close' not in frame.columns:
        return None

    frame['date'] = pd.to_datetime(frame['date'], errors='coerce')
    frame = frame.set_index('date').sort_index()
    end_date = date.today().strftime('%Y-%m-%d')
    frame = frame.loc[begin_date:end_date]
    frame['close'] = pd.to_numeric(frame['close'], errors='coerce')
    frame = frame.ffill()

    value = frame['close'] - frame['close'].shift(1)
    value = value.ffill()
    rate = (value / frame['close']) * 100
    return rate


def cluster_by_price_series(
    instruments: pd.DataFrame,
    day_file_path: str,
    *,
    index_file_path: Optional[str] = None,
    index_code: Optional[str] = None,
) -> ClusterGroups:
    """Cluster instruments using daily return series (optional index-relative)."""
    if AffinityPropagation is None:
        raise RuntimeError('scikit-learn is required for cluster_compute (install requirements-analysis.txt)')

    data = pd.DataFrame()
    index_column = None

    if index_file_path and index_code:
        index_series = _read_rate_series(index_file_path, index_code)
        if index_series is not None:
            index_column = '9' + str(index_code)
            data[index_column] = index_series

    for code in instruments.index:
        series = _read_rate_series(day_file_path, str(code))
        if series is not None:
            data[str(code)] = series
            if index_column is not None:
                data[str(code)] = data[str(code)] - data[index_column]

    if data.empty or len(data.columns) < 2:
        return ClusterGroups()

    data = data.ffill().fillna(0.01).astype('float64')
    if index_column and index_column in data.columns:
        data = data.drop(columns=[index_column])

    matrix = data.T.values
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


def run_industry_section(industry: str) -> dict:
    with session_scope() as session:
        query = session.query(Instrument).filter(Instrument.industry == industry)
        records = query.all()

    if not records:
        return {'status': 'skipped', 'reason': 'no instruments', 'section': industry}

    rows = []
    for record in records:
        rows.append({
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
        })

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
