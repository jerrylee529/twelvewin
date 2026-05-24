# -*- coding: utf-8 -*-

"""Daily OHLCV bar persistence (shared by compute and analysis)."""

import datetime

import pandas as pd
from sqlalchemy import text

from app.models import DailyBar

_BAR_SQL_COLUMNS = {
    'date': 'trade_date',
    'open': 'open',
    'high': 'high',
    'low': 'low',
    'close': 'close',
    'volume': 'volume',
    'amount': 'amount',
}

_DEFAULT_BAR_COLUMNS = ('date', 'open', 'high', 'low', 'close', 'volume', 'amount')


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


def get_last_trade_dates_bulk(session, codes=None):
    """Return ``{code: last_trade_date}`` for all or selected instrument codes."""
    from sqlalchemy import func

    query = session.query(
        DailyBar.code,
        func.max(DailyBar.trade_date).label('last_date'),
    )
    if codes is not None:
        normalized = [str(code).strip() for code in codes]
        if not normalized:
            return {}
        query = query.filter(DailyBar.code.in_(normalized))

    rows = query.group_by(DailyBar.code).all()
    return {str(code).strip(): last_date for code, last_date in rows if last_date is not None}


def get_global_max_trade_date(session):
    """Latest ``trade_date`` stored across all instruments."""
    from sqlalchemy import func

    return session.query(func.max(DailyBar.trade_date)).scalar()


def plan_incremental_downloads(codes, last_dates, default_start_date, end_date):
    """Split instruments into up-to-date skips and pending incremental downloads."""
    from datetime import timedelta

    pending = []
    skipped = 0

    for code in codes:
        code = str(code).strip()
        last_date = last_dates.get(code)
        if last_date is None:
            start_date = default_start_date
        else:
            start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')

        if start_date > end_date:
            skipped += 1
            continue

        pending.append((code, start_date, last_date))

    return pending, skipped


def _normalize_bar_columns(columns):
    if columns is None:
        return _DEFAULT_BAR_COLUMNS
    normalized = []
    for column in columns:
        if column not in _BAR_SQL_COLUMNS:
            raise ValueError('unsupported bar column: {}'.format(column))
        normalized.append(column)
    return tuple(normalized)


def _sql_select_list(columns):
    return ', '.join(
        '{} AS {}'.format(_BAR_SQL_COLUMNS[column], column)
        if column == 'date'
        else _BAR_SQL_COLUMNS[column]
        for column in columns
    )


def _rows_to_bars_dataframe(frame, columns):
    if frame is None or frame.empty:
        return pd.DataFrame()

    df = frame.copy()
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    return df[list(columns)]


def load_bars_dataframe(session, code, *, columns=None):
    """Return day bars as a CSV-compatible dataframe (date as YYYY-MM-DD strings)."""
    columns = _normalize_bar_columns(columns)
    code = str(code).strip()

    if columns == _DEFAULT_BAR_COLUMNS:
        bars = (
            session.query(DailyBar)
            .filter_by(code=code)
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

    sql_columns = _sql_select_list(columns)
    query = text(
        'SELECT {columns} FROM daily_bars '
        'WHERE code = :code ORDER BY trade_date ASC'.format(columns=sql_columns)
    )
    frame = pd.read_sql(query, session.connection(), params={'code': code})
    return _rows_to_bars_dataframe(frame, columns)


def load_bars_tail_dataframe(session, code, *, limit, columns=None):
    """Return the most recent ``limit`` bars in ascending date order."""
    if limit is None or int(limit) <= 0:
        raise ValueError('limit must be a positive integer')

    columns = _normalize_bar_columns(columns)
    code = str(code).strip()
    inner_columns = _sql_select_list(columns)
    outer_columns = ', '.join(columns)
    query = text(
        'SELECT {outer_columns} FROM ('
        'SELECT {inner_columns} FROM daily_bars '
        'WHERE code = :code ORDER BY trade_date DESC LIMIT :limit'
        ') recent ORDER BY date ASC'.format(
            outer_columns=outer_columns,
            inner_columns=inner_columns,
        )
    )
    frame = pd.read_sql(
        query,
        session.connection(),
        params={'code': code, 'limit': int(limit)},
    )
    return _rows_to_bars_dataframe(frame, columns)


def load_bars_since_dataframe(session, code, *, since_date, columns=None):
    """Return bars on or after ``since_date`` (YYYY-MM-DD or date)."""
    columns = _normalize_bar_columns(columns)
    code = str(code).strip()
    if isinstance(since_date, datetime.date):
        since_value = since_date.isoformat()
    else:
        since_value = str(since_date).strip()[:10]

    sql_columns = _sql_select_list(columns)
    query = text(
        'SELECT {columns} FROM daily_bars '
        'WHERE code = :code AND trade_date >= :since_date '
        'ORDER BY trade_date ASC'.format(columns=sql_columns)
    )
    frame = pd.read_sql(
        query,
        session.connection(),
        params={'code': code, 'since_date': since_value},
    )
    return _rows_to_bars_dataframe(frame, columns)


def scan_historic_extreme_codes(session, extreme):
    """Return ``{code: close}`` where the latest bar is a historic high/low."""
    if extreme not in ('high', 'low'):
        raise ValueError('extreme must be "high" or "low"')

    aggregate_fn = 'MAX' if extreme == 'high' else 'MIN'
    query = text(
        'SELECT db.code, db.close '
        'FROM daily_bars db '
        'INNER JOIN ('
        'SELECT code, MAX(trade_date) AS last_date '
        'FROM daily_bars GROUP BY code'
        ') latest ON db.code = latest.code AND db.trade_date = latest.last_date '
        'INNER JOIN ('
        'SELECT code, {aggregate_fn}(close) AS extreme_close '
        'FROM daily_bars GROUP BY code'
        ') extremes ON db.code = extremes.code AND db.close = extremes.extreme_close'.format(
            aggregate_fn=aggregate_fn
        )
    )
    rows = session.execute(query).fetchall()
    result = {}
    for code, close in rows:
        if close is None:
            continue
        result[str(code).strip()] = float(close)
    return result


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
