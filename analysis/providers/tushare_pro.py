# -*- coding: utf-8 -*-

"""Tushare Pro API helpers (token-based; replaces legacy 0.8.x interfaces)."""

import datetime
import os


class TushareProError(RuntimeError):
    pass


def get_tushare_token():
    return (
        os.environ.get('TUSHARE_TOKEN', '').strip()
        or os.environ.get('TW_TUSHARE_TOKEN', '').strip()
    )


def get_pro_client():
    """Return initialized ``pro_api`` client; raises if token missing."""
    token = get_tushare_token()
    if not token:
        raise TushareProError(
            'TUSHARE_TOKEN is not set. Register at https://tushare.pro and export the token.'
        )

    import tushare as ts

    ts.set_token(token)
    return ts.pro_api()


def code_to_ts_code(code):
    """Map 6-digit A-share code to Tushare ``ts_code`` (e.g. 600000 -> 600000.SH)."""
    from providers.base import normalize_stock_code

    normalized = normalize_stock_code(code)
    if not normalized:
        return None
    if normalized.startswith('92'):
        return normalized + '.BJ'
    if normalized.startswith(('83', '87', '88', '43')):
        return normalized + '.BJ'
    if normalized.startswith(('4', '8')):
        return normalized + '.BJ'
    if normalized.startswith(('6', '5')):
        return normalized + '.SH'
    if normalized.startswith(('0', '3')):
        return normalized + '.SZ'
    return normalized + '.SH'


def ts_code_to_code(ts_code):
    from providers.base import normalize_stock_code

    if not ts_code:
        return None
    return normalize_stock_code(str(ts_code).split('.')[0])


def normalize_trade_date(value):
    if value is None:
        return None
    text = str(value).strip().replace('-', '')
    if len(text) == 8:
        return text
    return None


def latest_open_trade_date(pro=None, *, lookback_days=15):
    """Most recent SSE trading day on or before today."""
    pro = pro or get_pro_client()
    end = datetime.date.today().strftime('%Y%m%d')
    start = (datetime.date.today() - datetime.timedelta(days=lookback_days)).strftime('%Y%m%d')
    cal = pro.trade_cal(
        exchange='SSE',
        start_date=start,
        end_date=end,
        is_open='1',
        fields='cal_date',
    )
    if cal is None or cal.empty:
        return None
    return str(cal['cal_date'].max())


def pro_bar_to_legacy_kline(frame):
    """Normalize ``pro_bar`` / ``daily`` frame to legacy ``get_k_data`` columns."""
    import pandas as pd

    if frame is None or frame.empty:
        return pd.DataFrame()

    result = frame.copy()
    rename = {
        'trade_date': 'date',
        'vol': 'volume',
        'amount': 'amount',
    }
    result.rename(columns={k: v for k, v in rename.items() if k in result.columns}, inplace=True)
    if 'date' in result.columns:
        result['date'] = pd.to_datetime(result['date'], errors='coerce').dt.strftime('%Y-%m-%d')
    for col in ('open', 'close', 'high', 'low', 'volume'):
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce')
    return result


def fetch_daily_basic_snapshot(trade_date=None, pro=None):
    """Fetch ``daily_basic`` for one trading day (replaces ``get_today_all``)."""
    import pandas as pd

    pro = pro or get_pro_client()
    trade_date = normalize_trade_date(trade_date) or latest_open_trade_date(pro)
    if not trade_date:
        return None, None

    basics = pro.daily_basic(
        trade_date=trade_date,
        fields='ts_code,close,pre_close,pe,pe_ttm,pb,total_mv,circ_mv,turnover_rate',
    )
    if basics is None or basics.empty:
        return None, trade_date

    names = pro.stock_basic(
        exchange='',
        list_status='L',
        fields='ts_code,name',
    )
    if names is not None and not names.empty:
        basics = basics.merge(names, on='ts_code', how='left')

    frame = pd.DataFrame({
        'code': basics['ts_code'].map(ts_code_to_code),
        'name': basics.get('name'),
        'trade': pd.to_numeric(basics.get('close'), errors='coerce'),
        'settlement': pd.to_numeric(basics.get('pre_close'), errors='coerce'),
        'per': pd.to_numeric(basics.get('pe_ttm', basics.get('pe')), errors='coerce'),
        'pb': pd.to_numeric(basics.get('pb'), errors='coerce'),
        'mktcap': pd.to_numeric(basics.get('total_mv'), errors='coerce'),
        'nmc': pd.to_numeric(basics.get('circ_mv'), errors='coerce'),
        'turnoverratio': pd.to_numeric(basics.get('turnover_rate'), errors='coerce'),
    })
    frame = frame.dropna(subset=['code'])
    frame.attrs['trade_date'] = trade_date
    return frame.reset_index(drop=True), trade_date
