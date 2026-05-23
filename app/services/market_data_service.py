# -*- coding: utf-8 -*-

"""Market data service for chart endpoints (database only)."""

from app.services.csv_store import CsvReadResult
from app.services.daily_bar_service import get_daily_bars_from_db


def get_candlestick_data(config, code, quote_provider=None) -> CsvReadResult:
    """Read day-history bars from Postgres and append realtime quotation when available."""
    result = get_daily_bars_from_db(code)
    if result is None:
        result = CsvReadResult(
            rows=[],
            path='',
            missing=True,
            error='database unavailable',
        )

    data = list(result.rows)

    if quote_provider is not None:
        quot = quote_provider(code)
        if quot:
            quote_date = quot['update_time'].split()[0]

            if len(data) > 0 and data[-1][0] != quote_date:
                data.append([
                    quote_date,
                    float(quot['open']),
                    float(quot['trade']),
                    float(quot['low']),
                    float(quot['high']),
                ])
            elif len(data) == 0:
                data.append([
                    quote_date,
                    float(quot['open']),
                    float(quot['trade']),
                    float(quot['low']),
                    float(quot['high']),
                ])

    return CsvReadResult(
        rows=data,
        path=result.path,
        update_time=result.update_time,
        missing=result.missing and not data,
        error=result.error if not data else None,
    )
