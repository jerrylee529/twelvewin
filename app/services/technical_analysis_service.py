# -*- coding: utf-8 -*-

"""Technical analysis results: Postgres only (CSV fallback in local DEBUG)."""

from app.services.analysis_artifacts import TECHNICAL_ANALYSIS_FILES
from app.services.analysis_access import resolve_published_rows
from app.services.csv_store import CsvReadResult, read_rows
from app.services.result_store_service import (
    get_price_change_rows_from_db,
    get_technical_rows_from_db,
)

PRICE_CHANGE_PERIODS = {
    u'近一周': 7,
    u'近一月': 30,
    u'近三月': 30 * 3,
    u'近半年': 30 * 6,
    u'近一年': 30 * 12,
}


def get_technical_rows(config, screen_key, *, is_anonymous=False) -> CsvReadResult:
    csv_filename = TECHNICAL_ANALYSIS_FILES.get(screen_key)
    if csv_filename is None:
        return CsvReadResult(rows=[], path="", error="unknown technical analysis key")

    max_rows = 10 if is_anonymous else None

    return resolve_published_rows(
        config,
        db_fetch=lambda: get_technical_rows_from_db(screen_key, max_rows=max_rows),
        csv_filename=csv_filename,
        csv_kwargs={
            'add_id': True,
            'add_update_time': True,
            'max_rows': max_rows,
        },
    )


def get_price_change_rows(config, *, days=u'近一周', low=-30, high=0) -> CsvReadResult:
    days = "".join((days or u'近一周').split())
    period = PRICE_CHANGE_PERIODS.get(days, 7)
    rate_field = 'rate' + str(period)

    result = resolve_published_rows(
        config,
        db_fetch=get_price_change_rows_from_db,
        csv_filename='price_change.csv',
        csv_kwargs={'add_id': False, 'add_update_time': False},
    )

    rows = []

    try:
        low = float(low)
        high = float(high)
    except (TypeError, ValueError):
        low = -30.0
        high = 0.0

    for row in result.rows:
        try:
            rate = float(row[rate_field])
        except (KeyError, TypeError, ValueError):
            continue

        if (rate > -9999) and (rate >= low) and (rate <= high):
            row['id'] = len(rows) + 1
            row['rate'] = rate
            row['updateTime'] = result.update_time
            rows.append(row)

    return CsvReadResult(
        rows=rows,
        path=result.path,
        update_time=result.update_time,
        missing=result.missing,
        error=result.error,
    )
