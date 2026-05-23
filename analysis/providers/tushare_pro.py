# -*- coding: utf-8 -*-

"""Tushare Pro API helpers (token-based; replaces legacy 0.8.x interfaces)."""

import datetime
import os
import time


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
        fields='ts_code,close,pre_close,pe,pe_ttm,pb,total_mv,circ_mv,turnover_rate,dv_ttm',
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
        'dividend_yield': pd.to_numeric(basics.get('dv_ttm'), errors='coerce'),
    })
    frame = frame.dropna(subset=['code'])
    frame.attrs['trade_date'] = trade_date
    return frame.reset_index(drop=True), trade_date


def _env_int(name, default):
    try:
        return int(os.environ.get(name, str(default)) or default)
    except (TypeError, ValueError):
        return default


def _env_float(name, default):
    try:
        return float(os.environ.get(name, str(default)) or default)
    except (TypeError, ValueError):
        return default


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def _financial_indicator_periods(years):
    today = datetime.date.today()
    latest_year = today.year - 1 if today.month >= 5 else today.year - 2
    return [
        (offset + 1, '{:04d}1231'.format(latest_year - offset))
        for offset in range(years)
    ]


def _fetch_financial_indicator_for_period(pro, period):
    return pro.fina_indicator(
        period=period,
        fields='ts_code,end_date,roe,or_yoy,netprofit_yoy',
    )


def _fetch_financial_indicator_for_codes(pro, periods, codes):
    import pandas as pd

    frames = []
    sleep_seconds = max(0.0, _env_float('TW_TUSHARE_FINANCIAL_SLEEP_SEC', 0.12))
    max_codes = _env_int('TW_TUSHARE_FINANCIAL_MAX_CODES', 0)
    if max_codes > 0:
        codes = codes[:max_codes]

    for code in codes:
        ts_code = code_to_ts_code(code)
        if not ts_code:
            continue
        for offset, period in periods:
            try:
                frame = pro.fina_indicator(
                    ts_code=ts_code,
                    period=period,
                    fields='ts_code,end_date,roe,or_yoy,netprofit_yoy',
                )
            except Exception as exc:
                print('tushare fina_indicator {} {} failed: {}'.format(ts_code, period, repr(exc)))
                continue
            if frame is not None and not frame.empty:
                frame = frame.copy()
                frame['year_offset'] = offset
                frames.append(frame)
            if sleep_seconds > 0:
                time.sleep(sleep_seconds)

    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)


def fetch_financial_indicator_snapshot(years=3, pro=None, codes=None):
    """Fetch latest annual financial indicators used by the screener."""
    import pandas as pd

    pro = pro or get_pro_client()
    periods = _financial_indicator_periods(years)
    frames = []

    for offset, period in periods:
        try:
            frame = _fetch_financial_indicator_for_period(pro, period)
        except Exception as exc:
            if 'ts_code' not in str(exc):
                raise
            frames = []
            break
        if frame is None or frame.empty:
            continue
        frame = frame.copy()
        frame['code'] = frame['ts_code'].map(ts_code_to_code)
        frame['year_offset'] = offset
        frames.append(frame)

    by_code_enabled = (
        _env_bool('TW_TUSHARE_FINANCIAL_BY_CODE')
        or _env_int('TW_TUSHARE_FINANCIAL_MAX_CODES', 0) > 0
    )
    if not frames and codes and by_code_enabled:
        data = _fetch_financial_indicator_for_codes(pro, periods, codes)
        if data is not None and not data.empty:
            data = data.copy()
            data['code'] = data['ts_code'].map(ts_code_to_code)
            frames = [data]
    elif not frames and codes:
        print(
            'tushare fina_indicator bulk query requires ts_code; '
            'set TW_TUSHARE_FINANCIAL_BY_CODE=true to enable per-code enrichment'
        )

    if not frames:
        return None

    data = pd.concat(frames, ignore_index=True)
    result = pd.DataFrame({'code': sorted(data['code'].dropna().unique())})

    for offset in range(1, years + 1):
        part = data[data['year_offset'] == offset].drop_duplicates(subset=['code'])
        part = part[['code', 'roe']].rename(columns={'roe': 'roe_y{}'.format(offset)})
        result = result.merge(part, on='code', how='left')

    latest = data[data['year_offset'] == 1].drop_duplicates(subset=['code'])
    latest = latest[['code', 'or_yoy', 'netprofit_yoy']].rename(
        columns={
            'or_yoy': 'revenue_growth',
            'netprofit_yoy': 'profit_growth',
        }
    )
    result = result.merge(latest, on='code', how='left')

    for column in ('roe_y1', 'roe_y2', 'roe_y3', 'revenue_growth', 'profit_growth'):
        if column in result.columns:
            result[column] = pd.to_numeric(result[column], errors='coerce')

    result.attrs['provider'] = 'tushare'
    return result.reset_index(drop=True)
