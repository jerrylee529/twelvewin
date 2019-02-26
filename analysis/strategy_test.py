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
import tushare as ts

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


# 选股策略
class Strategy(object):
    def __init__(self, day_file_path):
        self._securities = None
        self._choices = []
        self._day_file_path = day_file_path

    def _handle_data(self):
        pass

    def _get_securities(self):
        pass

    def run(self):
        self._securities = self._get_securities()

        self._choices = self._handle_data()

        return self._choices


# PE和均线选股策略
class PEMAStrategy(Strategy):
    def __init__(self, day_file_path):
        super(PEMAStrategy, self).__init__(day_file_path)

    def _get_securities(self):
        securities = ts.get_hs300s()

        return securities['code']

    def _handle_data(self):
        ma_choices = []

        for security in self._securities:
            file_path = self._day_file_path + '/' + security + '.csv'

            try:
                df = pd.read_csv(file_path)

                df['pre_close'] = df['close']
                df['pre_close'] = df['pre_close'].shift(1)
                df['ma20'] = df['close'].rolling(window=20, center=False).mean()

                last_row = df.iloc[-1]

                if (last_row['ma20'] <= last_row['close']) and (last_row['ma20'] > last_row['pre_close']):
                    ma_choices.append(security)
            except Exception as e:
                print "Exception: %s" % repr(e)

        print ma_choices

        df = ts.get_stock_basics()

        df.reset_index(inplace=True)

        df = df[df['code'].isin(ma_choices)]

        df = df.sort_values(by='pe', ascending=True)

        df.set_index('code', inplace=True)

        #print df

        return df.index


if __name__ == '__main__':
    strategy = PEMAStrategy(config.DAY_FILE_PATH)

    df = strategy.run()

    print df[:5]
