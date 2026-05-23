# -*- coding: utf-8 -*-

"""Build normalized fundamental screener snapshots from configured providers."""

import datetime
import os
import sys

import pandas as pd

_ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, _ANALYSIS_DIR)

from providers.market_registry import (  # noqa: E402
    fetch_dividend_dataframe,
    fetch_financial_indicators_dataframe,
    fetch_stock_basics_dataframe,
    fetch_today_quotes_dataframe,
)


def _parse_trade_date(value):
    if value:
        text = str(value).strip().replace('-', '')
        if len(text) == 8:
            try:
                return datetime.datetime.strptime(text, '%Y%m%d').date()
            except ValueError:
                pass
    return datetime.date.today()


def _numeric(frame, column):
    if column not in frame.columns:
        return pd.Series([pd.NA] * len(frame), index=frame.index)
    return pd.to_numeric(frame[column], errors='coerce')


def _normalize_quotes(frame):
    result = frame.copy()
    if 'close' not in result.columns and 'trade' in result.columns:
        result['close'] = result['trade']
    if 'pe_ttm' not in result.columns and 'per' in result.columns:
        result['pe_ttm'] = result['per']
    if 'pb_lf' not in result.columns and 'pb' in result.columns:
        result['pb_lf'] = result['pb']
    if 'market_cap' not in result.columns and 'mktcap' in result.columns:
        result['market_cap'] = result['mktcap']
    if 'float_market_cap' not in result.columns and 'nmc' in result.columns:
        result['float_market_cap'] = result['nmc']

    for column in (
        'close',
        'pe_ttm',
        'pb_lf',
        'market_cap',
        'float_market_cap',
        'dividend_yield',
    ):
        if column in result.columns:
            result[column] = pd.to_numeric(result[column], errors='coerce')

    if 'name' in result.columns:
        result['is_st'] = result['name'].fillna('').astype(str).str.contains('ST', case=False)
    else:
        result['is_st'] = False

    return result


def _merge_industry(snapshot):
    basics = fetch_stock_basics_dataframe()
    if basics is None or basics.empty:
        if 'industry' not in snapshot.columns:
            snapshot['industry'] = None
        return snapshot

    columns = [column for column in ('code', 'industry', 'name') if column in basics.columns]
    basics = basics[columns].drop_duplicates(subset=['code'])
    rename = {}
    if 'name' in basics.columns and 'name' in snapshot.columns:
        rename['name'] = 'basic_name'
    if 'industry' in basics.columns and 'industry' in snapshot.columns:
        rename['industry'] = 'basic_industry'
    basics = basics.rename(columns=rename)
    snapshot = snapshot.merge(basics, how='left', on='code')
    if 'basic_name' in snapshot.columns:
        snapshot['name'] = snapshot['name'].fillna(snapshot['basic_name'])
        snapshot = snapshot.drop(columns=['basic_name'])
    if 'basic_industry' in snapshot.columns:
        snapshot['industry'] = snapshot['industry'].fillna(snapshot['basic_industry'])
        snapshot = snapshot.drop(columns=['basic_industry'])
    if 'industry' not in snapshot.columns:
        snapshot['industry'] = None
    return snapshot


def _merge_dividend_yield(snapshot):
    if 'dividend_yield' in snapshot.columns and snapshot['dividend_yield'].notna().any():
        return snapshot

    dividends = fetch_dividend_dataframe()
    if dividends is None or dividends.empty:
        snapshot['dividend_yield'] = snapshot.get('dividend_yield', pd.NA)
        return snapshot

    dividend_cols = dividends[['code', 'divi']].drop_duplicates(subset=['code'])
    snapshot = snapshot.merge(dividend_cols, how='left', on='code')
    close = _numeric(snapshot, 'close')
    divi = _numeric(snapshot, 'divi')
    snapshot['dividend_yield'] = divi / 10.0 * 100.0 / close
    snapshot = snapshot.drop(columns=['divi'])
    return snapshot


def _derive_roe(snapshot):
    pe_ttm = _numeric(snapshot, 'pe_ttm')
    pb_lf = _numeric(snapshot, 'pb_lf')
    snapshot['roe'] = pb_lf * 100.0 / pe_ttm.replace(0, pd.NA)
    return snapshot


def _merge_financial_indicators(snapshot):
    codes = snapshot['code'].dropna().astype(str).tolist() if 'code' in snapshot.columns else None
    indicators = fetch_financial_indicators_dataframe(codes=codes)
    if indicators is None or indicators.empty:
        return snapshot

    columns = [
        column
        for column in ('code', 'roe_y1', 'roe_y2', 'roe_y3', 'revenue_growth', 'profit_growth')
        if column in indicators.columns
    ]
    if len(columns) <= 1:
        return snapshot

    snapshot = snapshot.merge(
        indicators[columns].drop_duplicates(subset=['code']),
        how='left',
        on='code',
    )
    if 'roe_y1' in snapshot.columns:
        snapshot['roe'] = snapshot['roe_y1'].fillna(snapshot['roe'])
    return snapshot


def _build_benchmarks(snapshot, trade_date):
    grouped = snapshot.dropna(subset=['industry']).copy()
    grouped = grouped[grouped['industry'].astype(str).str.strip() != '']
    if grouped.empty:
        return pd.DataFrame(columns=[
            'trade_date',
            'industry',
            'stock_count',
            'median_pe_ttm',
            'median_pb_lf',
            'median_roe',
            'median_dividend_yield',
            'median_market_cap',
            'median_float_market_cap',
        ])

    benchmarks = grouped.groupby('industry').agg(
        stock_count=('code', 'count'),
        median_pe_ttm=('pe_ttm', 'median'),
        median_pb_lf=('pb_lf', 'median'),
        median_roe=('roe', 'median'),
        median_dividend_yield=('dividend_yield', 'median'),
        median_market_cap=('market_cap', 'median'),
        median_float_market_cap=('float_market_cap', 'median'),
    ).reset_index()
    benchmarks.insert(0, 'trade_date', trade_date)
    return benchmarks


def _merge_industry_discounts(snapshot, benchmarks):
    if benchmarks.empty:
        snapshot['pe_discount_to_industry'] = pd.NA
        snapshot['pb_discount_to_industry'] = pd.NA
        return snapshot

    merged = snapshot.merge(
        benchmarks[['industry', 'median_pe_ttm', 'median_pb_lf']],
        how='left',
        on='industry',
    )
    merged['pe_discount_to_industry'] = (
        _numeric(merged, 'pe_ttm') / _numeric(merged, 'median_pe_ttm').replace(0, pd.NA)
    )
    merged['pb_discount_to_industry'] = (
        _numeric(merged, 'pb_lf') / _numeric(merged, 'median_pb_lf').replace(0, pd.NA)
    )
    return merged.drop(columns=['median_pe_ttm', 'median_pb_lf'])


def build_fundamental_snapshot_frames():
    quotes = fetch_today_quotes_dataframe()
    if quotes is None or quotes.empty:
        raise RuntimeError('unable to load quote fundamentals for screener snapshot')

    trade_date = _parse_trade_date(quotes.attrs.get('trade_date'))
    source = quotes.attrs.get('provider')

    snapshot = _normalize_quotes(quotes)
    snapshot = _merge_industry(snapshot)
    snapshot = _merge_dividend_yield(snapshot)
    snapshot = _derive_roe(snapshot)
    snapshot = _merge_financial_indicators(snapshot)

    for column in ('roe_y1', 'roe_y2', 'roe_y3', 'revenue_growth', 'profit_growth'):
        if column not in snapshot.columns:
            snapshot[column] = pd.NA

    snapshot['trade_date'] = trade_date
    snapshot['source'] = source

    columns = [
        'trade_date',
        'code',
        'name',
        'industry',
        'is_st',
        'close',
        'pe_ttm',
        'pb_lf',
        'roe',
        'roe_y1',
        'roe_y2',
        'roe_y3',
        'dividend_yield',
        'market_cap',
        'float_market_cap',
        'revenue_growth',
        'profit_growth',
        'source',
    ]
    snapshot = snapshot[[column for column in columns if column in snapshot.columns]]
    snapshot = snapshot.dropna(subset=['code']).drop_duplicates(subset=['code'], keep='first')

    benchmarks = _build_benchmarks(snapshot, trade_date)
    snapshot = _merge_industry_discounts(snapshot, benchmarks)

    return snapshot.reset_index(drop=True), benchmarks.reset_index(drop=True)
