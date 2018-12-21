# coding=utf8
'''
股票涨跌幅计算
'''

import pandas as pd
import os
from config import config
import sys
import numpy as np
import datetime


# 设置精度
pd.set_option('precision', 2)


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


def compute_all_instruments(instrument_filename, day_file_path, result_file_path, periods):
    instruments = pd.read_csv(instrument_filename, index_col=False, dtype={'code': object})

    if instruments is None:
        print("Could not find any instruments, exit")
        return

    instruments['close'] = None
    instruments['update_time'] = None

    for period in periods:
        instruments[period.title] = -9999

    for code in instruments['code']:
        try:
            file_path = day_file_path + '/' + code + '.csv'
            df = pd.read_csv(file_path)

            for period in periods:
                rate, close, update_time = price_change(df, period.begin_date, period.end_date)

                instruments.loc[instruments['code'] == code, period.title] = rate
                instruments.loc[instruments['code'] == code, 'close'] = close
                instruments.loc[instruments['code'] == code, 'update_time'] = update_time
        except Exception as e:
            print(str(e))
            continue

    result_filename_date = result_file_path + "/price_change_" + datetime.date.today().strftime('%Y-%m-%d') + ".csv"

    result_filename = result_file_path + "/price_change.csv"

    instruments.to_csv(result_filename_date, index=False, float_format='%.2f')

    instruments.to_csv(result_filename, index=False, float_format='%.2f')

    return instruments

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

    print result
