# -*- coding: utf-8 -*-

"""Market data service for chart endpoints."""

from app.services.csv_store import CsvReadResult, read_rows


def get_candlestick_data(config, code, quote_provider=None) -> CsvReadResult:
    """Read day-history CSV rows and append realtime quotation when available."""
    result = read_rows(config['DAY_FILE_PATH'], code + '.csv')
    data = []

    for row in result.rows:
        item = [row.get('date')]
        try:
            item.append(float(row['open']))
            item.append(float(row['close']))
            item.append(float(row['low']))
            item.append(float(row['high']))
        except (KeyError, TypeError, ValueError):
            continue
        data.append(item)

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

    return CsvReadResult(
        rows=data,
        path=result.path,
        update_time=result.update_time,
        missing=result.missing,
        error=result.error,
    )
