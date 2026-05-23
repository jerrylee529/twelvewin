# -*- coding: utf-8 -*-

"""Tushare Pro market data (replaces legacy ``profit_data`` / ``get_today_all``)."""

import datetime
import os

from providers.tushare_pro import (
    TushareProError,
    fetch_daily_basic_snapshot,
    fetch_financial_indicator_snapshot,
    get_pro_client,
    latest_open_trade_date,
    normalize_trade_date,
    ts_code_to_code,
)


def _report_period_end(report_date=None):
    explicit = os.environ.get('TW_DIVIDEND_REPORT_DATE', '').strip()
    if explicit:
        return normalize_trade_date(explicit)
    if report_date:
        return normalize_trade_date(report_date)

    today = datetime.date.today()
    report_year = today.year - 1 if today.month >= 5 else today.year - 2
    return '{:04d}1231'.format(report_year)


def fetch_dividend_dataframe(report_date=None):
    """Dividend rows compatible with legacy ``profit_data`` (code, name, divi, report_date)."""
    import pandas as pd

    try:
        pro = get_pro_client()
    except TushareProError as exc:
        print('tushare pro dividend skipped: {}'.format(exc))
        return None

    period_end = _report_period_end(report_date)
    if not period_end:
        return None

    end_year = period_end[:4]
    fields = 'ts_code,end_date,ann_date,cash_div,div_proc,stk_div'
    frame = None
    try:
        frame = pro.dividend(end_date=period_end, fields=fields)
    except Exception:
        frame = None
    if frame is None or frame.empty:
        try:
            frame = pro.dividend(fields=fields)
        except Exception as exc:
            print('tushare pro dividend failed: {}'.format(repr(exc)))
            return None
    if frame is None or frame.empty:
        return None

    frame = frame.copy()
    frame['end_date'] = frame['end_date'].astype(str).str.replace('-', '', regex=False)
    exact = frame[frame['end_date'] == period_end]
    frame = exact if not exact.empty else frame[frame['end_date'].str.startswith(end_year)]

    cash = pd.to_numeric(frame.get('cash_div'), errors='coerce')
    divi = cash * 10.0
    report = pd.to_datetime(frame.get('ann_date'), errors='coerce')

    names = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
    if names is not None and not names.empty:
        frame = frame.merge(names, on='ts_code', how='left')
    else:
        frame['name'] = frame['ts_code'].map(ts_code_to_code)

    result = pd.DataFrame({
        'code': frame['ts_code'].map(ts_code_to_code),
        'name': frame.get('name', frame['ts_code'].map(ts_code_to_code)),
        'divi': divi,
        'report_date': report,
        'year': int(end_year),
    })
    result = result.dropna(subset=['code'])
    result = result[result['divi'].notna() & (result['divi'] > 0)]
    if result.empty:
        return None

    result = result.sort_values('report_date', ascending=False)
    result = result.drop_duplicates(subset=['code'], keep='first')
    result.attrs['provider'] = 'tushare'
    result.attrs['report_date'] = period_end
    return result.reset_index(drop=True)


def fetch_today_quotes_dataframe(*, enrich=True):
    """Spot quotes via ``daily_basic`` on the latest open trade date."""
    try:
        frame, trade_date = fetch_daily_basic_snapshot()
    except TushareProError as exc:
        print('tushare pro quotes skipped: {}'.format(exc))
        return None
    except Exception as exc:
        print('tushare pro quotes failed: {}'.format(repr(exc)))
        return None

    if frame is None or frame.empty:
        return None

    if enrich:
        missing_settlement = frame['settlement'].isna() | (frame['settlement'] <= 0)
        if missing_settlement.any():
            frame.loc[missing_settlement, 'settlement'] = frame.loc[missing_settlement, 'trade']

    frame.attrs['provider'] = 'tushare'
    frame.attrs['trade_date'] = trade_date
    return frame


def fetch_stock_basics_dataframe():
    """Stock list + valuation snapshot (``stock_basic`` + latest ``daily_basic``)."""
    import pandas as pd

    try:
        pro = get_pro_client()
    except TushareProError as exc:
        print('tushare pro basics skipped: {}'.format(exc))
        return None

    basics = pro.stock_basic(
        exchange='',
        list_status='L',
        fields='ts_code,symbol,name,area,industry,list_date,market',
    )
    if basics is None or basics.empty:
        return None

    trade_date = latest_open_trade_date(pro)
    daily = None
    if trade_date:
        daily, _ignored = fetch_daily_basic_snapshot(trade_date=trade_date, pro=pro)

    frame = pd.DataFrame({
        'code': basics['ts_code'].map(ts_code_to_code),
        'name': basics['name'],
        'industry': basics.get('industry'),
        'area': basics.get('area'),
        'timeToMarket': basics.get('list_date'),
        'totals': None,
        'esp': None,
        'bvps': None,
        'pe': None,
        'pb': None,
    })
    frame = frame.dropna(subset=['code'])

    if daily is not None and not daily.empty:
        daily = daily[['code', 'per', 'pb', 'mktcap']].rename(
            columns={'per': 'pe', 'mktcap': 'totals'}
        )
        frame = frame.merge(daily, on='code', how='left')

    if frame.empty:
        return None

    frame.attrs['provider'] = 'tushare'
    frame.attrs['trade_date'] = trade_date
    return frame.reset_index(drop=True)


def fetch_financial_indicators_dataframe(codes=None):
    """Annual ROE and growth metrics from Tushare ``fina_indicator``."""
    try:
        return fetch_financial_indicator_snapshot(codes=codes)
    except TushareProError as exc:
        print('tushare pro financial indicators skipped: {}'.format(exc))
        return None
    except Exception as exc:
        print('tushare pro financial indicators failed: {}'.format(repr(exc)))
        return None
