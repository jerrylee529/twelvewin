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
from models import StrategyResultInfo, Session
from sqlalchemy import desc

# 设置精度
pd.set_option('precision', 2)


# 选股策略
class Strategy(object):
    def __init__(self, day_file_path):
        self._securities = None
        self._buy_list = []
        self._sell_list = []
        self._day_file_path = day_file_path

    def _handle_data(self):
        pass

    def _get_securities(self):
        pass

    def run(self):
        self._securities = self._get_securities()

        self._buy_list, self._sell_list = self._handle_data()

        return self._buy_list, self._sell_list


# PE和均线选股策略
class PEMAStrategy(Strategy):
    def __init__(self, day_file_path):
        super(PEMAStrategy, self).__init__(day_file_path)

    def _get_securities(self):
        securities = ts.get_hs300s()

        return securities['code']

    def __get_sell_list(self, under_ma20_list):
        session = Session()

        ret = session.query(StrategyResultInfo).filter(StrategyResultInfo.name == self.__class__.__name__).order_by(
            desc(StrategyResultInfo.create_time)).first()

        sell_list = []
        last_buy_list = []

        if ret:
            last_buy_list = ret.buy_list.split(',')

            sell_list = [secId for secId in last_buy_list if secId in under_ma20_list]

        session.close()

        return last_buy_list, sell_list

    def _handle_data(self):
        ma_window_size = 20
        above_ma20_list = []
        under_ma20_list = []

        # 获取均线数据
        for security in self._securities:
            file_path = self._day_file_path + '/' + security + '.csv'

            try:
                df = pd.read_csv(file_path)

                if df.shape[0] < ma_window_size:
                    continue

                df['pre_close'] = df['close']
                df['pre_close'] = df['pre_close'].shift(1)
                df['ma20'] = df['close'].rolling(window=ma_window_size, center=False).mean()

                last_row = df.iloc[-1]

                if (last_row['ma20'] <= last_row['close']) and (last_row['ma20'] > last_row['pre_close']):
                    above_ma20_list.append(security)

                if last_row['ma20'] > last_row['close']:
                    under_ma20_list.append(security)
            except Exception as e:
                print "Exception: %s" % repr(e)

        # 获取当天的pe
        df = ts.get_stock_basics()

        df.reset_index(inplace=True)

        df = df[df['code'].isin(above_ma20_list)]

        df = df.sort_values(by='pe', ascending=True)

        pe_list = df['code'].values.tolist()

        last_buy_list, sell_list = self.__get_sell_list(under_ma20_list)

        buy_list = list(set(pe_list if len(pe_list) < 5 else pe_list[:5]).union(set(last_buy_list)))

        strategy_result_info = StrategyResultInfo(self.__class__.__name__, ','.join(buy_list), ','.join(sell_list))

        session = Session()
        session.add(strategy_result_info)
        session.commit()
        session.close()

        return buy_list, sell_list


if __name__ == '__main__':
    strategy = PEMAStrategy(config.DAY_FILE_PATH)

    buy_list, sell_list = strategy.run()

    print buy_list, sell_list
