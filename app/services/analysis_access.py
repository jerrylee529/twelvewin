# -*- coding: utf-8 -*-

"""Shared rules for reading published analysis results in the web tier."""

from typing import Callable, Optional

from app.services.csv_store import CsvReadResult, read_rows


def read_analysis_from_db_enabled(config) -> bool:
    value = config.get('READ_ANALYSIS_FROM_DB', True)
    if isinstance(value, str):
        return value.lower() not in ('0', 'false', 'no', 'off')
    return bool(value)


def csv_dev_fallback_enabled(config) -> bool:
    """CSV fallback is opt-in via CSV_DEV_FALLBACK (migration aid only)."""
    value = config.get('CSV_DEV_FALLBACK')
    if isinstance(value, str):
        return value.lower() in ('1', 'true', 'yes', 'on')
    return value is True


def resolve_published_rows(
    config,
    *,
    db_fetch: Callable[[], Optional[CsvReadResult]],
    csv_filename: str = '',
    csv_kwargs=None,
) -> CsvReadResult:
    """Read published analysis rows from Postgres (web tier default)."""
    csv_kwargs = csv_kwargs or {}

    if read_analysis_from_db_enabled(config):
        db_result = db_fetch()
        if db_result is not None:
            if db_result.rows:
                return db_result
            if db_result.error:
                return db_result

    if csv_filename and csv_dev_fallback_enabled(config):
        return read_rows(config['RESULT_PATH'], csv_filename, **csv_kwargs)

    return CsvReadResult(
        rows=[],
        path='',
        missing=True,
        error='no published analysis data in database',
    )
