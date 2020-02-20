#!/usr/bin/env python
# encoding: utf-8
"""
@author: Jerry Lee
@license: (C) Copyright 2013-2019, Node Supply Chain Manager Corporation Limited.
@file: rsi_analysis.py
@time: 2020/2/20 11:45
@desc: 
"""

import json
import random
import time

import pandas as pd
import numpy as np
import requests
from models import Session, XueQiuReportInfo, engine
from config import my_headers


def rsi(t, periods=10):
    '''
    计算rsi指标
    t: 行情数据列表
    periods: 计算周期
    '''
    length = len(t)
    rsies = [np.nan]*length
    #数据长度不超过周期，无法计算；
    if length <= periods:
        return rsies
    #用于快速计算；
    up_avg = 0
    down_avg = 0

    #首先计算第一个RSI，用前periods+1个数据，构成periods个价差序列;
    first_t = t[:periods+1]
    for i in range(1, len(first_t)):
        #价格上涨;
        if first_t[i] >= first_t[i-1]:
            up_avg += first_t[i] - first_t[i-1]
        #价格下跌;
        else:
            down_avg += first_t[i-1] - first_t[i]
    up_avg = up_avg / periods
    down_avg = down_avg / periods
    rs = up_avg / down_avg
    rsies[periods] = 100 - 100/(1+rs)

    #后面的将使用快速计算；
    for j in range(periods+1, length):
        up = 0
        down = 0
        if t[j] >= t[j-1]:
            up = t[j] - t[j-1]
            down = 0
        else:
            up = 0
            down = t[j-1] - t[j]
        #类似移动平均的计算公式;
        up_avg = (up_avg*(periods - 1) + up)/periods
        down_avg = (down_avg*(periods - 1) + down)/periods
        rs = up_avg/down_avg
        rsies[j] = 100 - 100/(1+rs)

    return rsies


def get_kline(security_code, timestamp, session, headers):
    url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={}&begin={}&period=day&' \
          'type=before&count=-142&indicator=kline'.format(security_code, timestamp)

    rsp = session.get(url, headers=headers)

    if rsp.status_code == 200:
        return rsp.json()
    else:
        print("request {} failure".format(security_code))
        return None


def rsi_compute(security_codes):
    session = requests.session()

    headers = {'User-Agent':  random.choice(my_headers)}

    session.get('https://xueqiu.com/', headers=headers)

    curr_timestamp = int(time.time()*1000)

    security_codes_long = []
    security_codes_short = []

    for security_code in security_codes:

        try:
            kline_data = get_kline(security_code, timestamp=curr_timestamp, session=session, headers=headers)

            if kline_data:
                #print(kline_data)

                item = kline_data['data']['item']

                values = []
                for quot in item:
                    values.append(quot[5])

                rsi_value = rsi(values, periods=6)

                if rsi_value[-1] > 80:
                    security_codes_long.append(security_code)
                elif rsi_value[-1] < 20:
                    security_codes_short.append(security_code)
                else:
                    print('{}: {}'.format(security_code, rsi_value[-1]))
        except Exception as e:
            print('{} exception: {}'.format(security_code, repr(e)))

    print("security codes for long, {}".format(security_codes_long))
    print("security codes for short, {}".format(security_codes_short))


def stock_rsi_compute():
    df = pd.read_csv('avg_roe.csv', index_col='code', encoding='gbk')

    def format_security_code(original_code):
        code = "%06d" % original_code
        if code[0] == '6':
            market = 'SH'
        else:
            market = 'SZ'

        return '{}{}'.format(market, code)

    security_codes = list(map(format_security_code, df.index))

    rsi_compute(security_codes)


def fund_rsi_compute():
    fund_codes = ['SH510050', 'SH510300', 'SH512000', 'SZ159949', 'SZ159952', 'SZ159901']

    rsi_compute(fund_codes)



if __name__ == '__main__':
    fund_rsi_compute()

