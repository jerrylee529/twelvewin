# -*- coding: utf-8 -*-

"""Daily OHLCV bar persistence (shared by compute and analysis)."""

import datetime

import pandas as pd

from app.models import DailyBar


def _parse_trade_date(value):
    if value is None:
        return None
    if isinstance(value, datetime.date):
        return value
    text = str(value).strip()[:10]
    try:
        return datetime.datetime.strptime(text, '%Y-%m-%d').date()
    except ValueError:
        return None


def normalize_history_frame(frame):
    """Normalize ``get_history_data`` / CSV frame to columns date, open, high, low, close, volume, amount."""
    if frame is None:
        return pd.DataFrame()
    if isinstance(frame, list):
        if not frame:
            return pd.DataFrame()
        frame = pd.DataFrame(frame)
    if frame.empty:
        return pd.DataFrame()

    df = frame.copy()
    if 'date' not in df.columns:
        if isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()
            if 'index' in df.columns and 'date' not in df.columns:
                df = df.rename(columns={'index': 'date'})
        elif df.index.name == 'date':
            df = df.reset_index()

    if 'trade_date' in df.columns and 'date' not in df.columns:
        df['date'] = df['trade_date'].astype(str).str.slice(0, 10)

    if 'date' in df.columns:
        df['date'] = df['date'].astype(str).str.slice(0, 10)

    return df


def get_last_trade_date(session, code):
    row = (
        session.query(DailyBar.trade_date)
        .filter_by(code=str(code).strip())
        .order_by(DailyBar.trade_date.desc())
        .first()
    )
    return row[0] if row else None


def load_bars_dataframe(session, code):
    """Return day bars as a CSV-compatible dataframe (date as YYYY-MM-DD strings)."""
    bars = (
        session.query(DailyBar)
        .filter_by(code=str(code).strip())
        .order_by(DailyBar.trade_date.asc())
        .all()
    )
    if not bars:
        return pd.DataFrame()

    rows = []
    for bar in bars:
        rows.append(
            {
                'date': bar.trade_date.strftime('%Y-%m-%d'),
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume,
                'amount': bar.amount,
            }
        )
    return pd.DataFrame(rows)


def upsert_bars_from_dataframe(session, code, frame):
    """Insert new daily bars after the latest stored trade_date for ``code``."""
    code = str(code).strip()
    df = normalize_history_frame(frame)
    if df.empty or 'date' not in df.columns:
        return 0

    last_date = get_last_trade_date(session, code)
    objects = []

    for _, row in df.iterrows():
        trade_date = _parse_trade_date(row.get('date'))
        if trade_date is None:
            continue
        if last_date is not None and trade_date <= last_date:
            continue
        objects.append(
            DailyBar(
                code,
                trade_date,
                open=row.get('open'),
                high=row.get('high'),
                low=row.get('low'),
                close=row.get('close'),
                volume=row.get('volume'),
                amount=row.get('amount'),
            )
        )

    if objects:
        session.bulk_save_objects(objects)

    return len(objects)


def replace_bars_from_dataframe(session, code, frame):
    """Replace all bars for ``code`` (used by CSV import bridge)."""
    code = str(code).strip()
    session.query(DailyBar).filter_by(code=code).delete()

    df = normalize_history_frame(frame)
    if df.empty:
        return 0

    objects = []
    for _, row in df.iterrows():
        trade_date = _parse_trade_date(row.get('date'))
        if trade_date is None:
            continue
        objects.append(
            DailyBar(
                code,
                trade_date,
                open=row.get('open'),
                high=row.get('high'),
                low=row.get('low'),
                close=row.get('close'),
                volume=row.get('volume'),
                amount=row.get('amount'),
            )
        )

    if objects:
        session.bulk_save_objects(objects)

    return len(objects)
