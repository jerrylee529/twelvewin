# coding=utf8
__author__ = 'Administrator'

import pandas as pd
import numpy as np
import datetime
import time
from sendmail import  sendmail
from os.path import join, getsize

import sys

reload(sys)
sys.setdefaultencoding('utf8')


def get_buy_stocks():
    path = "C:/Stock/product/"

    filepath = path + "buy_top5.srf"

    size = getsize(filepath)

    if size > 0:
        subject = "买入的股票列表"
        sendmail(subject, mailto=['38454880@qq.com'], content="Please check attachment", attachments=[filepath])


def get_sell_stocks():
    path = "C:/Stock/product/"

    filepath = path + "sell_top5.srf"

    size = getsize(filepath)

    if size > 0:
        subject = "卖出的股票列表"
        sendmail(subject, mailto=['38454880@qq.com'], content="Please check attachment", attachments=[filepath])


def get_stock_trades():
    path = "C:/Stock/product/"

    filepath = path + "strategyresult.srf"

    df = pd.read_csv(filepath, header=None, sep='\t', index_col=[0,1], encoding='GBK')

    trades_col = df[15]

    # 去掉
    trades_col = trades_col.dropna()

    stock_trades = {}

    #
    for index in trades_col.index:
        result = trades_col[index]
        trades = result.split(',')
        #print trades
        stock_trades[index] = []
        for trade in trades:
            items = trade.split(':')
            if len(items) != 6:
                continue
            trade_info = {}
            trade_info['buy_date'] = items[0]
            trade_info['buy_price'] = items[1]
            trade_info['sell_date'] = items[2]
            trade_info['sell_price'] = items[3]
            trade_info['period'] = items[4]
            trade_info['ratio'] = items[5]
            #print trade_info

            stock_trades[index].append(trade_info)
            #stocks[index] =

        #print stock_trades[index]

    return stock_trades

stock_trades = get_stock_trades()

#print stock_trades

hold_trades = {}

for key in stock_trades.keys():
    data = stock_trades[key]

    if data[len(data)-1]['sell_date'][1:4].isdigit() == False:
        hold_trades[key] = data[len(data)-1]

#print hold_trades

df = pd.DataFrame(hold_trades)

df = df.T

df = df.sort_values(by=['buy_date'], ascending=False)

#
df['buy_date'] = df['buy_date'].astype(np.datetime64)
df['ratio'] = df['ratio'].astype(np.float64)

print df['buy_date'].dtype

t = np.datetime64('2015-10-01')
df = df[df['buy_date'] > t]

df = df.sort_values(by=['ratio'], ascending=False)

TODAY = datetime.date.today()
CURRENTDAY = TODAY.strftime('%Y-%m-%d')

filename = "C:/Stock/product/returnTop10_%s.txt" % (CURRENTDAY,)


df.to_csv("C:/Stock/product/returnTop10.txt", columns=['code', 'name', 'buy_date', 'buy_price', 'period',  'ratio',  'sell_date',  'sell_price'], index=True, sep='\t')
df.to_csv(filename, columns=['code', 'name', 'buy_date', 'buy_price', 'period',  'ratio',  'sell_date',  'sell_price'], index=True, sep='\t')

get_sell_stocks()

get_buy_stocks()

print df


