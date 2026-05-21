# -*- coding:utf-8 -*-

"""生成精选股票 stock_business 报表。

脚本获取当日全市场行情，按 ROE、换手率、流通市值、市价等条件筛选股票，
再计算 10/30/60 周均线并要求价格靠近 10 周线且处于 30/60 周线之上。
结果输出为 stock_business_<date>.csv 和 stock_business.csv。
"""

__author__ = 'jerry'

import os
import sys

import pandas as pd
import datetime
from config import config
import numpy as np
import time

_ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, _ANALYSIS_DIR)

from compat import apply_close_price, set_display_precision
from csv_output import atomic_export_pair, get_result_path
from getvaluation import _prepare_quotes
from providers.market_registry import fetch_today_quotes_dataframe

set_display_precision(2)

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


def _tushare_request_delay():
    try:
        return float(os.environ.get('TW_TUSHARE_SLEEP_SEC', '0.25'))
    except (TypeError, ValueError):
        return 0.25


def get_stock_ma(code, ma1, ma2, ma3):
    """Weekly MA via Tushare Pro ``pro_bar`` (replaces AkShare ``stock_zh_a_hist``)."""
    from quotation import get_history_data

    print("get data for " + code)

    now = datetime.datetime.now()
    lookback_days = max(ma1, ma2, ma3) * 7 + 14
    dt = now - datetime.timedelta(days=lookback_days)
    start = dt.strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')

    df = None
    for attempt in range(3):
        df = get_history_data(code, start, end, ktype='W', autype='qfq')
        if df is not None and not df.empty:
            break
        time.sleep(1.5 * (attempt + 1))

    if df is None or df.empty:
        return 0

    if 'close' not in df.columns:
        return 0

    df = df.sort_values('date' if 'date' in df.columns else df.columns[0])
    df.reset_index(drop=True, inplace=True)

    df['ma' + str(ma1)] = df['close'].rolling(window=ma1).mean()
    df['ma' + str(ma2)] = df['close'].rolling(window=ma2).mean()
    df['ma' + str(ma3)] = df['close'].rolling(window=ma3).mean()

    price = []
    if df.shape[0] > 0:
        ma1_value = df.iat[df.shape[0] - 1, df.columns.get_loc('ma' + str(ma1))]
        ma2_value = df.iat[df.shape[0] - 1, df.columns.get_loc('ma' + str(ma2))]
        ma3_value = df.iat[df.shape[0] - 1, df.columns.get_loc('ma' + str(ma3))]

        price.append(ma1_value)
        price.append(ma1_value if pd.isna(ma2_value) else ma2_value)
        price.append(ma1_value if pd.isna(ma3_value) else ma3_value)

    return price


def get_profit_report():
    df_quots = pd.DataFrame()

    for _attempt in range(0, 3):
        try:
            df_quots = fetch_today_quotes_dataframe()
            if df_quots is not None and not df_quots.empty:
                break
        except Exception:
            time.sleep(10 * 60)
            continue

    if df_quots is None or df_quots.empty:
        raise RuntimeError('unable to load spot quotes for business screen')

    df_quots = _prepare_quotes(df_quots.copy())

    if 'turnoverratio' not in df_quots.columns:
        df_quots['turnoverratio'] = 0
    if 'nmc' not in df_quots.columns:
        df_quots['nmc'] = df_quots.get('mktcap', 0)

    df_quots = df_quots[
        (df_quots['roe'] >= 5)
        & (df_quots['turnoverratio'] >= 2)
        & (df_quots['nmc'] >= 300000)
        & (df_quots['nmc'] <= 3000000)
        & (df_quots['close'] <= 50)
    ]

    temp1 = np.zeros(df_quots.shape[0])
    temp2 = np.zeros(df_quots.shape[0])
    temp3 = np.zeros(df_quots.shape[0])

    ma10 = 10
    ma30 = 30
    ma60 = 60

    index = 0
    delay = _tushare_request_delay()
    for code in df_quots['code']:
        price = get_stock_ma(code, ma1=ma10, ma2=ma30, ma3=ma60)
        if delay > 0:
            time.sleep(delay)
        if not price:
            index += 1
            continue

        temp1[index] = price[0]
        temp2[index] = price[1]
        temp3[index] = price[2]
        index += 1

    df_quots.insert(df_quots.shape[1], 'wma' + str(ma10), temp1)
    df_quots.insert(df_quots.shape[1], 'wma' + str(ma30), temp2)
    df_quots.insert(df_quots.shape[1], 'wma' + str(ma60), temp3)

    df_quots = df_quots.dropna(how='any')
    df_quots = df_quots[
        (df_quots['close'] > df_quots['wma10'])
        & (df_quots['close'] < df_quots['wma10'] * 1.1)
    ]
    df_quots = df_quots[
        (df_quots['close'] > df_quots['wma30'])
        & (df_quots['close'] > df_quots['wma60'])
        & (df_quots['wma10'] >= df_quots['wma30'])
    ]

    export_report(df_quots, title="stock_business")


if __name__ == '__main__':
    get_profit_report()
