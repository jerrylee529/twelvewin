# coding=utf8

__author__ = 'Administrator'

"""
技术分析服务，每天收盘后运行一次
"""

import pandas as pd
from datetime import timedelta, datetime, date
from config import config
import os
import time
from price_change_analysis import compute_all_instruments, PriceChangePeriod, compute_all_instruments_amplitude

# 设置精度
pd.set_option('precision', 2)


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

        print("index: %d, date: %s, max date: %s" % (idx_max, df.ix[idx_max]['date'], df['date'].max(),))

        t1 = time.strptime(df.ix[idx_max]['date'], "%Y-%m-%d")
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
    instruments = pd.read_csv(instrument_filename, index_col=False, dtype={'code': object})

    if instruments is None:
        print("Could not find any instruments, exit")
        return

    instruments['close'] = None

    code_index = -1
    for code in instruments['code']:
        data_filename = "%s/%s.csv" % (day_file_path, code)  # 日线数据文件名

        code_index += 1

        print("calculate %s, file path: %s" % (code, data_filename))

        if os.path.exists(data_filename):
            try:
                df = pd.read_csv(data_filename, index_col=False)
                index = df['close'].idxmax()  # 最大值的索引

                print("index: %d, date: %s, max date: %s" % (index, df.ix[index]['date'], df['date'].max(),))

                t1 = time.strptime(df.ix[index]['date'], "%Y-%m-%d")
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
        today = date.today().strftime("%Y-%m-%d")

        filename = "%s/highest_in_history_%s.csv" % (result_file_path, today)

        # 这里close字段的类型是object，需要转换为float64
        instruments['close'] = instruments['close'].astype('float64')

        instruments.to_csv(filename, index=False, float_format='%.2f')

        filename = "%s/highest_in_history.csv" % (result_file_path,)

        instruments.to_csv(filename, index=False, float_format='%.2f')
    else:
        print("No qualified data")


# 历史新低
def lowest_in_history(instrument_filename, day_file_path, result_file_path):
    instruments = pd.read_csv(instrument_filename, index_col=False, dtype={'code': object})

    if instruments is None:
        print("Could not find any instruments, exit")
        return

    instruments['close'] = None

    code_index = -1
    for code in instruments['code']:
        data_filename = "%s/%s.csv" % (day_file_path, code)  # 日线数据文件名

        code_index += 1

        print("calculate %s, file path: %s" % (code, data_filename))

        if os.path.exists(data_filename):
            try:
                df = pd.read_csv(data_filename, index_col=False)
                index = df['close'].idxmin()  # 最小值的索引

                print("index: %d, date: %s, min date: %s" % (index, df.ix[index]['date'], df['date'].max()))

                t1 = time.strptime(df.ix[index]['date'], "%Y-%m-%d")
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
        today = date.today().strftime("%Y-%m-%d")

        filename = "%s/lowest_in_history_%s.csv" % (result_file_path, today)

        # 这里close字段的类型是object，需要转换为float64
        instruments['close'] = instruments['close'].astype('float64')

        instruments.to_csv(filename, index=False, float_format='%.2f')

        filename = "%s/lowest_in_history.csv" % (result_file_path,)

        instruments.to_csv(filename, index=False, float_format='%.2f')
    else:
        print("No qualified data")

# 均线多头
def ma_long_history(instrument_filename, day_file_path, result_file_path, ma1, ma2, ma3):
    instruments = pd.read_csv(instrument_filename, index_col=False, dtype={'code': object})

    if instruments is None:
        print("Could not find any instruments, exit")
        return

    instruments['close'] = None

    code_index = -1
    for code in instruments['code']:
        data_filename = "%s/%s.csv" % (day_file_path, code)  # 日线数据文件名

        code_index += 1

        print("calculate %s, file path: %s" % (code, data_filename))

        if os.path.exists(data_filename):
            try:
                df = pd.read_csv(data_filename, index_col=False)

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
        today = date.today().strftime("%Y-%m-%d")

        filename = "%s/ma_long_%s.csv" % (result_file_path, today)

        # 这里close字段的类型是object，需要转换为float64
        instruments['close'] = instruments['close'].astype('float64')

        instruments.to_csv(filename, index=False, float_format='%.2f')

        filename = "%s/ma_long.csv" % (result_file_path,)

        instruments.to_csv(filename, index=False, float_format='%.2f')
    else:
        print("No qualified data")


# 突破均线
def break_ma(instrument_filename, day_file_path, result_file_path, ma1):
    instruments = pd.read_csv(instrument_filename, index_col=False, dtype={'code': object})

    if instruments is None:
        print("Could not find any instruments, exit")
        return

    instruments['close'] = None

    code_index = -1
    for code in instruments['code']:
        data_filename = "%s/%s.csv" % (day_file_path, code)  # 日线数据文件名

        code_index += 1

        print("calculate %s, file path: %s" % (code, data_filename))

        if os.path.exists(data_filename):
            try:
                df = pd.read_csv(data_filename, index_col=False)

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
        today = date.today().strftime("%Y-%m-%d")

        filename = "%s/break_ma_%s.csv" % (result_file_path, today)

        # 这里close字段的类型是object，需要转换为float64
        instruments['close'] = instruments['close'].astype('float64')

        instruments.to_csv(filename, index=False, float_format='%.2f')

        filename = "%s/break_ma.csv" % (result_file_path,)

        instruments.to_csv(filename, index=False, float_format='%.2f')
    else:
        print("No qualified data")


# 年线之上的股票
def above_ma(instrument_filename, day_file_path, result_file_path, ma1):
    instruments = pd.read_csv(instrument_filename, index_col=False, dtype={'code': object})

    if instruments is None:
        print("Could not find any instruments, exit")
        return

    instruments['close'] = None

    code_index = -1
    for code in instruments['code']:
        data_filename = "%s/%s.csv" % (day_file_path, code)  # 日线数据文件名

        code_index += 1

        print("calculate %s, file path: %s" % (code, data_filename))

        if os.path.exists(data_filename):
            try:
                df = pd.read_csv(data_filename, index_col=False)

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
        today = date.today().strftime("%Y-%m-%d")

        filename = "%s/above_ma_%s.csv" % (result_file_path, today)

        # 这里close字段的类型是object，需要转换为float64
        instruments['close'] = instruments['close'].astype('float64')

        instruments.to_csv(filename, index=False, float_format='%.2f')

        filename = "%s/above_ma.csv" % (result_file_path,)

        instruments.to_csv(filename, index=False, float_format='%.2f')
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
