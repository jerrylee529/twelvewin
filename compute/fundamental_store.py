# -*- coding: utf-8 -*-

"""Persist normalized fundamental screener snapshots."""

import datetime
import math

from app.models import FundamentalSnapshot, IndustryFundamentalBenchmark
from core.db import session_scope
from core.schema import ensure_analysis_schema


def _clean_value(value):
    if value is None:
        return None
    try:
        import pandas as pd

        if pd.isna(value):
            return None
    except (ImportError, TypeError, ValueError):
        pass
    try:
        if math.isnan(value):
            return None
    except TypeError:
        pass
    return value


def _records(frame):
    if frame is None or frame.empty:
        return []
    return [
        {key: _clean_value(value) for key, value in row.items()}
        for row in frame.to_dict(orient='records')
    ]


def _trade_date_from_records(records):
    if not records:
        return datetime.date.today()
    value = records[0].get('trade_date')
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    return datetime.date.today()


def publish_fundamental_snapshot_frames(snapshot_frame, benchmark_frame):
    ensure_analysis_schema()

    snapshots = _records(snapshot_frame)
    benchmarks = _records(benchmark_frame)
    trade_date = _trade_date_from_records(snapshots or benchmarks)
    now = datetime.datetime.now()

    with session_scope() as session:
        session.query(FundamentalSnapshot).filter(
            FundamentalSnapshot.trade_date == trade_date
        ).delete(synchronize_session=False)
        session.query(IndustryFundamentalBenchmark).filter(
            IndustryFundamentalBenchmark.trade_date == trade_date
        ).delete(synchronize_session=False)

        snapshot_objects = []
        for row in snapshots:
            code = str(row.pop('code', '') or '').strip()
            if not code:
                continue
            row.pop('trade_date', None)
            row['create_time'] = now
            row['update_time'] = now
            snapshot_objects.append(FundamentalSnapshot(trade_date, code, **row))

        benchmark_objects = []
        for row in benchmarks:
            industry = str(row.pop('industry', '') or '').strip()
            if not industry:
                continue
            row.pop('trade_date', None)
            row['create_time'] = now
            row['update_time'] = now
            benchmark_objects.append(IndustryFundamentalBenchmark(trade_date, industry, **row))

        if snapshot_objects:
            session.bulk_save_objects(snapshot_objects)
        if benchmark_objects:
            session.bulk_save_objects(benchmark_objects)

    return {
        'status': 'published',
        'trade_date': trade_date.isoformat(),
        'snapshot_count': len(snapshot_objects),
        'benchmark_count': len(benchmark_objects),
    }
