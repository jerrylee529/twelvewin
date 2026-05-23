# coding=utf8

"""计算个股区间涨跌幅和振幅报表。

compute_all_instruments() 根据多个 PriceChangePeriod 统计每只股票在指定区间内的涨跌幅，
输出 price_change_<date>.csv 和 price_change.csv。compute_all_instruments_amplitude()
统计指定天数窗口内的振幅，输出 price_amplitude_<date>.csv 和 price_amplitude.csv。
"""

import pandas as pd
import os
import sys
from config import config
import numpy as np
import datetime
from instruments import get_all_instrument_codes_before

_ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, _ANALYSIS_DIR)

from compat import set_display_precision
from day_data import day_data_available, load_day_dataframe, load_instruments_dataframe
from csv_output import atomic_export_pair, get_result_path
from result_export import export_price_change_report

set_display_precision(2)


class PriceChangePeriod(object):
    """
    涨跌幅计算的一个时间段
    """
    def __init__(self):
        self.begin_date = ""
        self.end_date = ""
        self.title = ""


def price_change(df, begin_date, end_date):

    df = df[(df['date'] >= begin_date) & (df['date'] <= end_date)]

    rate = -9999
    update_date = None
    close = -9999
    if df.shape[0] > 0:
        first_row = df.iloc[0]
        last_row = df.iloc[-1]
        rate = (last_row['close'] - first_row['close'])*100/first_row['close']
        close = first_row['close']
        update_date = last_row['date']

    return rate, close, update_date


def price_amplitude(df, begin_date, end_date):
    result = df[(df['date'] >= begin_date) & (df['date'] <= end_date)]

    result['amplitude'] = (result['high'] - result['low'])*100 / result['low']

    return result


def compute_all_instruments(instrument_filename, day_file_path, result_file_path, periods):
    instruments = load_instruments_dataframe()

    if instruments is None or instruments.empty:
        print("Could not find any instruments, exit")
        return

    instruments = instruments.copy()
    instruments['code'] = instruments['code'].astype(str)
    instruments['close'] = None
    instruments['update_time'] = None

    for period in periods:
        instruments[period.title] = -9999

    for code in instruments['code']:
        try:
            if not day_data_available(code):
                continue
            df = load_day_dataframe(code)

            for period in periods:
                rate, close, update_time = price_change(df, period.begin_date, period.end_date)

                instruments.loc[instruments['code'] == code, period.title] = rate
                instruments.loc[instruments['code'] == code, 'close'] = close
                instruments.loc[instruments['code'] == code, 'update_time'] = update_time
        except Exception as e:
            print(str(e))
            continue

    export_price_change_report(instruments)

    return instruments


def compute_all_instruments_amplitude(period):
    instruments = get_all_instrument_codes_before(20190101)

    if instruments is None:
        print("Could not find any instruments, exit")
        return

    result = pd.DataFrame()
    result['close'] = None
    result['update_time'] = None
    result[period.title] = -9999
    result['amp_std'] = None
    result['code'] = instruments

    for code in instruments:
        try:
            if not day_data_available(code):
                continue
            df = load_day_dataframe(code)

            df_amp = price_amplitude(df, period.begin_date, period.end_date)

            result.loc[result['code'] == code, 'close'] = df.iloc[df.shape[0]-1, 2]
            result.loc[result['code'] == code, 'update_time'] = df.iloc[df.shape[0]-1, 0]
            result.loc[result['code'] == code, period.title] = df_amp['amplitude'].mean()
            result.loc[result['code'] == code, 'amp_std'] = df_amp['amplitude'].std()
        except Exception as e:
            print(str(e))
            continue

    atomic_export_pair(
        result,
        get_result_path(config),
        "price_amplitude",
        date_suffix=datetime.date.today().strftime('%Y-%m-%d'),
        index=False,
        float_format='%.2f',
    )

    return result


if __name__ == '__main__':
    today = datetime.date.today()

    # 计算的周期, 近七天、一个月、三个月、六个月和一年
    days_list = [7, 30, 30*3, 30*6, 30*12]

    periods = []
    for days in days_list:
        period = PriceChangePeriod()
        period.begin_date = (datetime.date.today() + datetime.timedelta(days=-days)).strftime('%Y-%m-%d')
        period.end_date = today.strftime('%Y-%m-%d')
        period.title = 'rate' + str(days)
        periods.append(period)

    result = compute_all_instruments(config.INSTRUMENT_FILENAME, config.DAY_FILE_PATH, config.RESULT_PATH, periods)

    print(result)
