# -*- coding: utf-8 -*-

"""Import per-code day CSV files into daily_bars (migration bridge)."""

import logging
import os

import pandas as pd
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models import DailyBar
from core.db import session_scope
from core.day_bars import normalize_history_frame, replace_bars_from_dataframe
from core.schema import ensure_analysis_schema

logger = logging.getLogger(__name__)

_EXPORT_COLUMNS = (
    'code',
    'trade_date',
    'open',
    'high',
    'low',
    'close',
    'volume',
    'amount',
)

# Postgres extended query protocol allows at most 65535 bind parameters per statement.
_INSERT_BATCH_SIZE = 5000


def import_day_bars_from_csv(config, *, codes=None, max_codes=0):
    """Load ``DAY_FILE_PATH/<code>.csv`` files into ``daily_bars``."""
    day_path = (config.get('DAY_FILE_PATH') or '').rstrip(os.sep)
    if not day_path or not os.path.isdir(day_path):
        return {'status': 'skipped', 'reason': 'DAY_FILE_PATH not configured'}

    if codes is None:
        codes = []
        for name in os.listdir(day_path):
            if name.endswith('.csv') and name != 'instruments.csv':
                codes.append(name[:-4])
        codes.sort()

    if max_codes and max_codes > 0:
        codes = codes[: int(max_codes)]

    summary = {
        'status': 'ok',
        'imported_codes': 0,
        'skipped_codes': 0,
        'failed_codes': 0,
        'total_bars': 0,
    }

    with session_scope() as session:
        for code in codes:
            path = os.path.join(day_path, '{}.csv'.format(code))
            if not os.path.isfile(path):
                summary['skipped_codes'] += 1
                continue

            try:
                frame = pd.read_csv(path)
            except Exception:
                summary['failed_codes'] += 1
                continue

            frame = normalize_history_frame(frame)
            if frame.empty:
                summary['failed_codes'] += 1
                continue

            count = replace_bars_from_dataframe(session, code, frame)
            if count == 0:
                summary['failed_codes'] += 1
                continue

            summary['imported_codes'] += 1
            summary['total_bars'] += count

    return summary


def _chunk_to_records(chunk):
    frame = chunk.copy()
    for col in _EXPORT_COLUMNS:
        if col not in frame.columns:
            return []

    frame['code'] = frame['code'].astype(str).str.strip()
    frame['trade_date'] = pd.to_datetime(frame['trade_date'], errors='coerce').dt.date
    frame = frame.dropna(subset=['trade_date'])
    if frame.empty:
        return []

    return frame[list(_EXPORT_COLUMNS)].to_dict('records')


def _insert_records_postgres(session, records, *, on_conflict_skip=True):
    if not records:
        return 0

    inserted = 0
    for offset in range(0, len(records), _INSERT_BATCH_SIZE):
        batch = records[offset:offset + _INSERT_BATCH_SIZE]
        stmt = pg_insert(DailyBar).values(batch)
        if on_conflict_skip:
            stmt = stmt.on_conflict_do_nothing(index_elements=['code', 'trade_date'])
        result = session.execute(stmt)
        count = result.rowcount
        if count is None or count < 0:
            count = len(batch)
        inserted += count
    return inserted


def _insert_records_generic(session, records):
    if not records:
        return 0

    inserted = 0
    for offset in range(0, len(records), _INSERT_BATCH_SIZE):
        batch = records[offset:offset + _INSERT_BATCH_SIZE]
        session.bulk_insert_mappings(DailyBar, batch)
        inserted += len(batch)
    return inserted


def import_daily_bars_from_export_csv(
    csv_path,
    *,
    chunk_size=50000,
    truncate=False,
):
    """Import a consolidated ``daily_bars`` table export (code + trade_date columns)."""
    csv_path = os.path.abspath(csv_path)
    if not os.path.isfile(csv_path):
        return {'status': 'error', 'reason': 'file not found: {}'.format(csv_path)}

    ensure_analysis_schema()

    summary = {
        'status': 'ok',
        'csv_path': csv_path,
        'chunk_size': chunk_size,
        'truncate': truncate,
        'chunks': 0,
        'rows_read': 0,
        'rows_inserted': 0,
    }

    use_pg_upsert = False
    with session_scope() as session:
        bind = session.get_bind()
        use_pg_upsert = bind.dialect.name == 'postgresql'

        if truncate:
            deleted = session.query(DailyBar).delete()
            logger.info('truncated daily_bars (%s rows deleted)', deleted)
            summary['truncated_rows'] = deleted

        insert_fn = _insert_records_postgres if use_pg_upsert else _insert_records_generic

        for chunk in pd.read_csv(csv_path, chunksize=chunk_size, dtype={'code': str}):
            summary['chunks'] += 1
            summary['rows_read'] += len(chunk)

            records = _chunk_to_records(chunk)
            if not records:
                continue

            if use_pg_upsert and not truncate:
                inserted = insert_fn(session, records)
                if inserted < 0:
                    inserted = len(records)
            else:
                session.bulk_insert_mappings(DailyBar, records)
                inserted = len(records)

            summary['rows_inserted'] += inserted
            session.commit()

            logger.info(
                'chunk %s: read=%s cumulative_read=%s cumulative_inserted=%s',
                summary['chunks'],
                len(chunk),
                summary['rows_read'],
                summary['rows_inserted'],
            )

    return summary
