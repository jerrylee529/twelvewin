# -*- coding: utf-8 -*-

"""Technical analysis result service backed by generated CSV artifacts."""

from app.services.csv_store import CsvReadResult, read_rows


TECHNICAL_ANALYSIS_FILES = {
    'highest': 'highest_in_history.csv',
    'lowest': 'lowest_in_history.csv',
    'ma_long': 'ma_long.csv',
    'break_ma': 'break_ma.csv',
    'above_ma': 'above_ma.csv',
}

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
    return read_rows(
        config['RESULT_PATH'],
        csv_filename,
        add_id=True,
        add_update_time=True,
        max_rows=max_rows,
    )


def get_price_change_rows(config, *, days=u'近一周', low=-30, high=0) -> CsvReadResult:
    days = "".join((days or u'近一周').split())
    period = PRICE_CHANGE_PERIODS.get(days, 7)
    rate_field = 'rate' + str(period)

    result = read_rows(config['RESULT_PATH'], 'price_change.csv')
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
