# coding=utf8

"""日终技术分析 CSV 生成服务。

提供历史新高、历史新低、均线多头、突破指定均线、站上指定均线、区间涨跌幅和振幅分析函数。
每个函数读取股票列表和本地日线 CSV，筛选符合条件的股票，并同时输出带日期和固定文件名的结果 CSV。
"""

__author__ = 'Administrator'

import pandas as pd
from datetime import timedelta, datetime, date
from config import config
import os
import time
from price_change_analysis import compute_all_instruments, PriceChangePeriod, compute_all_instruments_amplitude

from compat import set_display_precision
from day_data import day_data_available, load_day_dataframe, load_instruments_dataframe
from result_export import export_screen_report

set_display_precision(2)

SCREEN_RESULT_COLUMNS = ('code', 'name', 'close')


def _load_instruments():
    instruments = load_instruments_dataframe()
    if instruments is None or instruments.empty:
        print("Could not find any instruments, exit")
        return None
    instruments = instruments.copy()
    instruments['code'] = instruments['code'].astype(str)
    if 'name' not in instruments.columns:
        instruments['name'] = instruments['code']
    return instruments


def _write_screen_results(instruments, result_file_path, basename):
    instruments = instruments.copy()
    instruments['close'] = instruments['close'].astype('float64')
    return export_screen_report(
        instruments,
        basename,
        required_columns=SCREEN_RESULT_COLUMNS,
    )


# 技术分析基类
class Analysis:
    def __init__(self):
        pass

    def analyze(self, index, instruments, df):
        pass


# 历史新高分析
class HighestInHistory(Analysis):
    def analyze(self, index, instruments, df):
        idx_max = df['close'].idxmax()  # 最大值的索引

        print("index: %d, date: %s, max date: %s" % (idx_max, df.loc[idx_max]['date'], df['date'].max(),))

        t1 = time.strptime(df.loc[idx_max]['date'], "%Y-%m-%d")
        t2 = time.strptime(df['date'].max(), "%Y-%m-%d")

        if t1 == t2:
            instruments['close'][idx_max] = df['close'].max()

        return instruments


# 均线多头分析
class LongMA(Analysis):
    def analyze(self, index, instruments, df):
        pass


# 历史最高
def highest_in_history(instrument_filename, day_file_path, result_file_path):
    instruments = _load_instruments()
    if instruments is None:
        return

    instruments['close'] = None

    code_index = -1
    for code in instruments['code']:
        code_index += 1

        print("calculate %s" % code)

        if day_data_available(code):
            try:
                df = load_day_dataframe(code)
                index = df['close'].idxmax()  # 最大值的索引

                print("index: %d, date: %s, max date: %s" % (index, df.loc[index]['date'], df['date'].max(),))

                t1 = time.strptime(df.loc[index]['date'], "%Y-%m-%d")
                t2 = time.strptime(df['date'].max(), "%Y-%m-%d")

                if t1 == t2:
                    instruments['close'][code_index] = df['close'].max()
            except pd.errors.EmptyDataError as pderror:
                continue
            except Exception as e:
                print(repr(e))
                break

    instruments = instruments.dropna(axis=0, subset=['close'])

    if not instruments.empty:
        _write_screen_results(instruments, result_file_path, 'highest_in_history')
    else:
        print("No qualified data")


# 历史新低
def lowest_in_history(instrument_filename, day_file_path, result_file_path):
    instruments = _load_instruments()
    if instruments is None:
        return

    instruments['close'] = None

    code_index = -1
    for code in instruments['code']:
        code_index += 1

        print("calculate %s" % code)

        if day_data_available(code):
            try:
                df = load_day_dataframe(code)
                index = df['close'].idxmin()  # 最小值的索引

                print("index: %d, date: %s, min date: %s" % (index, df.loc[index]['date'], df['date'].max()))

                t1 = time.strptime(df.loc[index]['date'], "%Y-%m-%d")
                t2 = time.strptime(df['date'].max(), "%Y-%m-%d")

                # 如果最小值出现的日期和数据最大日期相同，则为历史新低
                if t1 == t2:
                    instruments['close'][code_index] = df['close'].min()
            except pd.errors.EmptyDataError:
                continue
            except Exception as e:
                print(repr(e))
                break

    instruments = instruments.dropna(axis=0, subset=['close'])

    if not instruments.empty:
        _write_screen_results(instruments, result_file_path, 'lowest_in_history')
    else:
        print("No qualified data")

# 均线多头
def ma_long_history(instrument_filename, day_file_path, result_file_path, ma1, ma2, ma3):
    instruments = _load_instruments()
    if instruments is None:
        return

    instruments['close'] = None

    code_index = -1
    for code in instruments['code']:
        code_index += 1

        print("calculate %s" % code)

        if day_data_available(code):
            try:
                df = load_day_dataframe(code)

                df['ma'+str(ma1)] = df['close'].rolling(window=ma1).mean()
                df['ma'+str(ma2)] = df['close'].rolling(window=ma2).mean()
                df['ma'+str(ma3)] = df['close'].rolling(window=ma3).mean()

                df.fillna(0)

                last_row = df.tail(1)

                last_row.reset_index(drop=True, inplace=True)

                if not last_row.empty:
                    if (last_row['ma'+str(ma1)][0] > last_row['ma'+str(ma2)][0]) \
                            and (last_row['ma'+str(ma2)][0] > last_row['ma'+str(ma3)][0]):
                        instruments['close'][code_index] = last_row['close'][0]
            except pd.errors.EmptyDataError as pderror:
                continue
            except Exception as e:
                print(repr(e))
                break

    instruments = instruments.dropna(axis=0, subset=['close'])

    if not instruments.empty:
        _write_screen_results(instruments, result_file_path, 'ma_long')
    else:
        print("No qualified data")


# 突破均线
def break_ma(instrument_filename, day_file_path, result_file_path, ma1):
    instruments = _load_instruments()
    if instruments is None:
        return

    instruments['close'] = None

    code_index = -1
    for code in instruments['code']:
        code_index += 1

        print("calculate %s" % code)

        if day_data_available(code):
            try:
                df = load_day_dataframe(code)

                df['ma'+str(ma1)] = df['close'].rolling(window=ma1).mean()

                df.fillna(0)

                last_row = df.tail(1)

                last_row.reset_index(drop=True, inplace=True)

                if not last_row.empty:
                    ma_price = last_row['ma'+str(ma1)][0]
                    if (ma_price >= last_row['open'][0]) and (ma_price <= last_row['close'][0]):
                        instruments['close'][code_index] = last_row['close'][0]
            except pd.errors.EmptyDataError:
                continue
            except Exception as e:
                print(repr(e))
                break

    instruments = instruments.dropna(axis=0, subset=['close'])

    if not instruments.empty:
        _write_screen_results(instruments, result_file_path, 'break_ma')
    else:
        print("No qualified data")


# 年线之上的股票
def above_ma(instrument_filename, day_file_path, result_file_path, ma1):
    instruments = _load_instruments()
    if instruments is None:
        return

    instruments['close'] = None

    code_index = -1
    for code in instruments['code']:
        code_index += 1

        print("calculate %s" % code)

        if day_data_available(code):
            try:
                df = load_day_dataframe(code)

                df['ma'+str(ma1)] = df['close'].rolling(window=ma1).mean()

                df.fillna(0)

                last_row = df.tail(1)

                last_row.reset_index(drop=True, inplace=True)

                if not last_row.empty:
                    ma_price = last_row['ma'+str(ma1)][0]
                    if ma_price <= last_row['close'][0]:
                        instruments['close'][code_index] = last_row['close'][0]
            except pd.errors.EmptyDataError:
                continue
            except Exception as e:
                print(repr(e))
                break

    instruments = instruments.dropna(axis=0, subset=['close'])

    if not instruments.empty:
        _write_screen_results(instruments, result_file_path, 'above_ma')
    else:
        print("No qualified data")


def price_change_computer(instrument_filename, day_file_path, result_file_path):
    today = date.today()

    # 计算的周期, 近七天、一个月、三个月、六个月和一年
    days_list = [7, 30, 30*3, 30*6, 30*12]

    periods = []
    for days in days_list:
        period = PriceChangePeriod()
        period.begin_date = (date.today() + timedelta(days=-days)).strftime('%Y-%m-%d')
        period.end_date = today.strftime('%Y-%m-%d')
        period.title = 'rate' + str(days)
        periods.append(period)

    result = compute_all_instruments(instrument_filename, day_file_path, result_file_path, periods)

    print(result)


def price_amplitude_computer(days):
    today = date.today()
    period = PriceChangePeriod()
    period.begin_date = (date.today() + timedelta(days=-days)).strftime('%Y-%m-%d')
    period.end_date = today.strftime('%Y-%m-%d')
    period.title = 'amp_' + str(days)

    result = compute_all_instruments_amplitude(period)

    print(result)


if __name__ == '__main__':
   
    # highest_in_history(instrument_filename=config.INSTRUMENT_FILENAME, day_file_path=config.DAY_FILE_PATH,
    #                    result_file_path=config.RESULT_PATH)
    #
    # lowest_in_history(instrument_filename=config.INSTRUMENT_FILENAME, day_file_path=config.DAY_FILE_PATH,
    #                   result_file_path=config.RESULT_PATH)
    #
    # ma_long_history(instrument_filename=config.INSTRUMENT_FILENAME, day_file_path=config.DAY_FILE_PATH,
    #                 result_file_path=config.RESULT_PATH, ma1=5, ma2=10, ma3=20)
    #
    # break_ma(instrument_filename=config.INSTRUMENT_FILENAME, day_file_path=config.DAY_FILE_PATH,
    #          result_file_path=config.RESULT_PATH, ma1=20)
    #
    # above_ma(instrument_filename=config.INSTRUMENT_FILENAME, day_file_path=config.DAY_FILE_PATH,
    #          result_file_path=config.RESULT_PATH, ma1=250)
    #
    # price_change_computer(instrument_filename=config.INSTRUMENT_FILENAME, day_file_path=config.DAY_FILE_PATH,
    #                       result_file_path=config.RESULT_PATH)

    price_amplitude_computer(30)
