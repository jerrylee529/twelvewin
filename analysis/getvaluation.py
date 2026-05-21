# -*- coding:utf-8 -*-

"""生成估值和股息率排名 CSV。

get_valuation_report() 基于股票基础数据和当日行情计算 ROE、PEG、估值和估值差。
get_profit_report() 使用分红数据和实时行情生成股息率、ROE、市盈率、市净率、市值等排名，
输出 stock_dividence、stock_roe、stock_pe、stock_pb、stock_value 等 CSV。

行情与分红数据经 ``providers.market_registry`` 拉取（默认 AkShare，可回退 tushare）。
"""

__author__ = 'jerry'

import os
import sys

import pandas as pd
import datetime
from config import config

_ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, _ANALYSIS_DIR)

from compat import apply_close_price, set_display_precision
from csv_output import atomic_export_pair, get_result_path
from providers.market_registry import (
    fetch_dividend_dataframe,
    fetch_stock_basics_dataframe,
    fetch_today_quotes_dataframe,
)

set_display_precision(2)

# 财务年度
YEAR = 2017

# 财务季度
SEASON = 4

key = ["code"]

today = datetime.date.today()


def export_report(dest, title):
    result_path = get_result_path(config)
    atomic_export_pair(
        dest,
        result_path,
        title,
        date_suffix=today.strftime("%Y%m%d"),
        encoding='utf-8',
        index=False,
        float_format='%.2f',
    )


def _prepare_quotes(df_quots):
    """Normalize quote frame to legacy tushare column names."""
    if 'name' not in df_quots.columns and '名称' in df_quots.columns:
        df_quots = df_quots.rename(columns={'名称': 'name'})

    if 'per' not in df_quots.columns and 'pe' in df_quots.columns:
        df_quots['per'] = df_quots['pe']

    if 'trade' not in df_quots.columns and 'close' in df_quots.columns:
        df_quots['trade'] = df_quots['close']

    if 'settlement' not in df_quots.columns:
        df_quots['settlement'] = df_quots.get('trade', 0)

    per = pd.to_numeric(df_quots.get('per'), errors='coerce')
    pb = pd.to_numeric(df_quots.get('pb'), errors='coerce')
    df_quots['roe'] = pb * 100 / per.replace(0, pd.NA)
    apply_close_price(df_quots)
    df_quots.reset_index(inplace=True)

    drop_cols = [
        'index', 'name', 'changepercent', 'trade', 'open', 'high', 'low',
        'settlement', 'volume', 'amount', 'mktcap_raw', 'nmc_raw', 'esp', 'bvps', 'shares',
    ]
    existing = [col for col in drop_cols if col in df_quots.columns]
    return df_quots.drop(existing, axis=1)


def get_valuation_report():
    df_basic = fetch_stock_basics_dataframe()
    if df_basic is None or df_basic.empty:
        raise RuntimeError('unable to load stock basics for valuation report')

    df_basic['roe'] = df_basic['esp'] * 100 / df_basic['bvps']
    if 'profit' in df_basic.columns:
        df_basic['peg'] = df_basic['pe'] / df_basic['profit']

    if 'index' in df_basic.columns:
        df_basic.reset_index(inplace=True)

    drop_cols = [
        'area', 'outstanding', 'totalAssets', 'liquidAssets', 'fixedAssets',
        'reserved', 'reservedPerShare', 'undp', 'perundp', 'rev', 'profit',
        'gpr', 'npr', 'holders',
    ]
    existing = [col for col in drop_cols if col in df_basic.columns]
    df_basic = df_basic.drop(existing, axis=1)

    df_quots = fetch_today_quotes_dataframe()
    if df_quots is None or df_quots.empty:
        raise RuntimeError('unable to load spot quotes for valuation report')

    df_quots = _prepare_quotes(df_quots.copy())
    df = pd.merge(df_basic, df_quots, how='left', on=key)
    df['value'] = df['esp'] / 0.08
    df['rate'] = (df['value'] - df['close']) * 100 / df['close']
    df = df.sort_values(["rate"], ascending=False)
    df.drop_duplicates(inplace=True)
    export_report(df, title="stockvaluation")


def get_stock_ma(code, ma):
    import akshare as ak

    end = datetime.date.today()
    start = end - datetime.timedelta(days=ma * 7 + 30)
    frame = ak.stock_zh_a_hist(
        symbol=code,
        period='weekly',
        adjust='qfq',
        start_date=start.strftime('%Y%m%d'),
        end_date=end.strftime('%Y%m%d'),
    )
    if frame is None or frame.empty:
        return None

    frame = frame.rename(columns={'收盘': 'close'})
    frame['ma' + str(ma)] = frame['close'].rolling(window=ma).mean()
    return frame


def get_profit_report():
    df = fetch_dividend_dataframe()
    if df is None or df.empty:
        raise RuntimeError(
            'unable to load dividend data (East Money / AkShare fhps). '
            'Try: export TW_DIVIDEND_REPORT_DATE=20241231 '
            'or TW_MARKET_DATA_PROVIDER=yahoo'
        )

    df = df.sort_values('divi', ascending=False)

    df_quots = fetch_today_quotes_dataframe()
    if df_quots is None or df_quots.empty:
        raise RuntimeError('unable to load spot quotes for profit report')

    if 'per' not in df_quots.columns:
        raise RuntimeError('spot quotes missing PE (per); check AkShare connectivity')

    df_quots = _prepare_quotes(df_quots.copy())

    df = pd.merge(df, df_quots, how='left', on=key)

    for col in ('close', 'per', 'pb', 'roe', 'divi'):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows that would cause div-by-zero (pb/per/close); legacy tushare rarely had pb==0.
    df = df[(df['close'] > 0) & (df['per'] > 0) & (df['pb'] > 0)]
    if df.empty:
        raise RuntimeError('no rows left after filtering invalid close/per/pb')

    df['rate'] = df['divi'] / 10 * 100 / df['close']
    df['valueprice'] = df['roe'] * (df['close'] / df['pb']) / 15
    df = df.sort_values('rate', ascending=False)
    df = df.sort_values('report_date', ascending=False)
    df = df.drop_duplicates(['name'])

    df = df.sort_values('rate', ascending=False)
    export_report(df, title="stock_dividence")

    df = df.sort_values('roe', ascending=False)
    export_report(df, title="stock_roe")

    df = df.sort_values('per', ascending=True)
    export_report(df, title="stock_pe")

    df = df.sort_values('pb', ascending=True)
    export_report(df, title="stock_pb")

    df = df.sort_values('mktcap', ascending=True)
    export_report(df, title="stock_value")


if __name__ == '__main__':
    get_profit_report()
