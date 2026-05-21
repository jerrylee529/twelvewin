# -*- coding: utf-8 -*-

"""AkShare-backed dividend and spot quote data (replaces legacy tushare/163)."""

import datetime
import os

from providers.base import normalize_stock_code


def default_dividend_report_date():
    """Report period for ``stock_fhps_em`` (YYYYMMDD)."""
    explicit = os.environ.get('TW_DIVIDEND_REPORT_DATE', '').strip()
    if explicit:
        return explicit

    today = datetime.date.today()
    # 5 月前上年报可能尚未披露完整，优先再上一年
    report_year = today.year - 1 if today.month >= 5 else today.year - 2
    return '{:04d}1231'.format(report_year)


def _fallback_dividend_dates(primary_date):
    today = datetime.date.today()
    candidates = [
        primary_date,
        '{:04d}1231'.format(today.year - 1),
        '{:04d}1231'.format(today.year - 2),
        '20241231',
        '20231231',
    ]
    ordered = []
    seen = set()
    for item in candidates:
        if not item or item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _load_fhps(report_date=None):
    import akshare as ak

    primary = report_date or default_dividend_report_date()
    required_columns = ('代码', '名称', '现金分红-现金分红比例')

    for date in _fallback_dividend_dates(primary):
        try:
            raw = ak.stock_fhps_em(date=date)
        except (TypeError, KeyError, ValueError) as exc:
            # akshare 在东财返回 result=null 时会触发 NoneType 下标访问
            print('akshare stock_fhps_em({}) failed: {}'.format(date, repr(exc)))
            continue
        except Exception as exc:
            print('akshare stock_fhps_em({}) failed: {}'.format(date, repr(exc)))
            continue

        if raw is None or raw.empty:
            print('akshare stock_fhps_em({}) returned empty'.format(date))
            continue

        missing = [name for name in required_columns if name not in raw.columns]
        if missing:
            print('akshare stock_fhps_em({}) missing columns: {}'.format(date, missing))
            continue

        raw = raw.copy()
        raw['code'] = raw['代码'].map(normalize_stock_code)
        return raw, date

    return None, None


def fetch_dividend_dataframe(report_date=None):
    """Dividend snapshot compatible with legacy ``profit_data`` (columns: code, name, divi, report_date)."""
    import pandas as pd

    raw, date = _load_fhps(report_date)
    if raw is None:
        return None
    if not date:
        date = default_dividend_report_date()

    divi = pd.to_numeric(raw['现金分红-现金分红比例'], errors='coerce')
    report_col = '最新公告日期' if '最新公告日期' in raw.columns else '预案公告日'
    report = pd.to_datetime(raw[report_col], errors='coerce')

    frame = pd.DataFrame({
        'code': raw['code'],
        'name': raw['名称'],
        'divi': divi,
        'report_date': report,
        'year': int(str(date)[:4]),
    })
    frame = frame.dropna(subset=['code'])
    frame = frame[frame['divi'].notna() & (frame['divi'] > 0)]
    if frame.empty:
        return None

    frame.attrs['provider'] = 'akshare'
    frame.attrs['report_date'] = date
    return frame.reset_index(drop=True)


def _normalize_em_spot(raw):
    import pandas as pd

    rename = {
        '代码': 'code',
        '名称': 'name',
        '最新价': 'trade',
        '昨收': 'settlement',
        '市盈率-动态': 'per',
        '市净率': 'pb',
        '总市值': 'mktcap_raw',
        '流通市值': 'nmc_raw',
        '换手率': 'turnoverratio',
    }
    frame = raw.rename(columns={k: v for k, v in rename.items() if k in raw.columns})
    if 'code' not in frame.columns:
        return None

    frame['code'] = frame['code'].map(normalize_stock_code)
    for col in ('trade', 'settlement', 'per', 'pb', 'mktcap_raw', 'nmc_raw', 'turnoverratio'):
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors='coerce')

    if 'mktcap_raw' in frame.columns:
        frame['mktcap'] = frame['mktcap_raw'] / 10000.0
    if 'nmc_raw' in frame.columns:
        frame['nmc'] = frame['nmc_raw'] / 10000.0

    return frame


def _normalize_sina_spot(raw):
    import pandas as pd

    rename = {
        '代码': 'code',
        '名称': 'name',
        '最新价': 'trade',
        '昨收': 'settlement',
    }
    frame = raw.rename(columns={k: v for k, v in rename.items() if k in raw.columns})
    if 'code' not in frame.columns:
        return None

    frame['code'] = frame['code'].map(normalize_stock_code)
    for col in ('trade', 'settlement'):
        frame[col] = pd.to_numeric(frame[col], errors='coerce')
    return frame


def _fetch_spot_em():
    import akshare as ak
    import pandas as pd

    parts = []
    for fn_name in ('stock_sh_a_spot_em', 'stock_sz_a_spot_em', 'stock_bj_a_spot_em'):
        fn = getattr(ak, fn_name, None)
        if fn is None:
            continue
        try:
            part = fn()
            if part is not None and not part.empty:
                parts.append(part)
        except Exception as exc:
            print('akshare {} failed: {}'.format(fn_name, repr(exc)))

    if parts:
        return pd.concat(parts, ignore_index=True)

    return ak.stock_zh_a_spot_em()


def _enrich_spot_from_fhps(spot, fhps):
    """Fill missing valuation fields using fhps fundamentals + last price."""
    import pandas as pd

    fund = fhps[['code', '每股收益', '每股净资产', '总股本']].copy()
    fund['esp'] = pd.to_numeric(fund['每股收益'], errors='coerce')
    fund['bvps'] = pd.to_numeric(fund['每股净资产'], errors='coerce')
    fund['shares'] = pd.to_numeric(fund['总股本'], errors='coerce')

    merged = spot.merge(fund[['code', 'esp', 'bvps', 'shares']], on='code', how='left')
    if 'per' not in merged.columns:
        merged['per'] = None
    if 'pb' not in merged.columns:
        merged['pb'] = None

    trade = pd.to_numeric(merged.get('trade'), errors='coerce')
    missing_per = merged['per'].isna() & merged['esp'].notna() & (merged['esp'] > 0)
    merged.loc[missing_per, 'per'] = trade[missing_per] / merged.loc[missing_per, 'esp']

    missing_pb = merged['pb'].isna() & merged['bvps'].notna() & (merged['bvps'] > 0)
    merged.loc[missing_pb, 'pb'] = trade[missing_pb] / merged.loc[missing_pb, 'bvps']

    if 'mktcap' not in merged.columns:
        merged['mktcap'] = None
    missing_mkt = merged['mktcap'].isna() & merged['shares'].notna() & trade.notna()
    merged.loc[missing_mkt, 'mktcap'] = (
        merged.loc[missing_mkt, 'shares'] * trade[missing_mkt] / 10000.0
    )

    if 'nmc' not in merged.columns:
        merged['nmc'] = merged['mktcap']

    return merged


def fetch_today_quotes_dataframe(*, enrich=True):
    """Spot quotes compatible with legacy ``get_today_all`` column names."""
    import akshare as ak

    frame = None

    try:
        raw = _fetch_spot_em()
        frame = _normalize_em_spot(raw)
    except Exception as exc:
        print('akshare eastmoney spot failed: {}'.format(repr(exc)))

    if frame is None or frame.empty:
        try:
            raw = ak.stock_zh_a_spot()
            frame = _normalize_sina_spot(raw)
        except Exception as exc:
            print('akshare sina spot failed: {}'.format(repr(exc)))
            return None

    if frame is None or frame.empty:
        return None

    if enrich:
        try:
            fhps, _date = _load_fhps()
            if fhps is not None:
                frame = _enrich_spot_from_fhps(frame, fhps)
        except Exception as exc:
            print('akshare fhps enrich skipped: {}'.format(repr(exc)))

    frame.attrs['provider'] = 'akshare'
    return frame.reset_index(drop=True)


def fetch_stock_basics_dataframe():
    """Fundamental snapshot roughly matching legacy ``get_stock_basics``."""
    import pandas as pd

    raw, _date = _load_fhps()
    if raw is None:
        return None

    esp = pd.to_numeric(raw.get('每股收益'), errors='coerce')
    bvps = pd.to_numeric(raw.get('每股净资产'), errors='coerce')
    shares = pd.to_numeric(raw.get('总股本'), errors='coerce')

    frame = pd.DataFrame({
        'code': raw['code'],
        'name': raw['名称'],
        'esp': esp,
        'bvps': bvps,
        'pe': None,
        'pb': None,
        'totals': shares / 1e8,
        'industry': None,
    })
    frame = frame.dropna(subset=['code'])
    if frame.empty:
        return None

    frame.attrs['provider'] = 'akshare'
    return frame.reset_index(drop=True)
