# -*- coding: utf-8 -*-

"""Read daily OHLCV bars from Postgres for chart endpoints."""

from flask import has_app_context
from sqlalchemy.exc import SQLAlchemyError

from app.models import DailyBar
from app.services.csv_store import CsvReadResult


def get_daily_bars_from_db(code):
    """Return candlestick rows as [date, open, close, low, high] ordered by trade_date."""
    if not has_app_context():
        return None

    try:
        bars = (
            DailyBar.query.filter_by(code=str(code).strip())
            .order_by(DailyBar.trade_date.asc())
            .all()
        )
    except SQLAlchemyError:
        return None

    if not bars:
        return CsvReadResult(rows=[], path='', missing=True, error='no daily bars in database')

    rows = []
    update_time = None
    for bar in bars:
        if bar.open is None or bar.close is None or bar.low is None or bar.high is None:
            continue
        trade_date = bar.trade_date.strftime('%Y-%m-%d')
        update_time = trade_date
        rows.append([
            trade_date,
            float(bar.open),
            float(bar.close),
            float(bar.low),
            float(bar.high),
        ])

    return CsvReadResult(
        rows=rows,
        path='daily_bars:{}'.format(code),
        update_time=update_time,
        missing=not rows,
        error=None if rows else 'no daily bars in database',
    )
