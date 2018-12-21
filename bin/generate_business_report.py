# -*- coding: utf-8 -*-
"""
Created on Thu May 10 20:11:08 2018

@author: Administrator
"""


import pandas as pd
import tushare as ts
import datetime
import numpy as np


def swap_value(x, y):
    return x if x!=0.00 else y


def get_price():
    ma = 20

    now = datetime.datetime.now()

    dt = now - datetime.timedelta(days=(ma*7+10))

    df = ts.get_k_data(code='600000', ktype='W', autype='qfq', start=dt.strftime('%Y-%m-%d'), end=now.strftime('%Y-%m-%d'))

    df.reset_index(inplace=True)

    df['ma'+str(ma)] = df['close'].rolling(window=ma).mean()

    last_row = df.tail(1)

    #price = last_row['ma'+str(ma)]

    price = df.iat[df.shape[0]-1, df.shape[1]-1]

    return price
    

# 获取股票的均线
def get_stock_ma(code, ma):
    now = datetime.datetime.now()

    dt = now - datetime.timedelta(days=(ma*7+10))

    df = ts.get_k_data(code=code, ktype='W', autype='qfq', start=dt.strftime('%Y-%m-%d'), end=now.strftime('%Y-%m-%d'))

    if (df.empty):
        return 0

    df.reset_index(inplace=True)

    df['ma'+str(ma)] = df['close'].rolling(window=ma).mean()

    #last_row = df.tail(1)

    #price = last_row['ma'+str(ma)]

    price = 0
    if (df.shape[0] > 0):
        price = df.iat[df.shape[0]-1, df.shape[1]-1]

    return price
    
    
'''
price = get_price()

df = ts.get_today_all()

temp = np.zeros(df.shape[0])

if (not np.isnan(price)):
    temp[0] = price[1]
'''


df_quots = ts.get_today_all()

df_quots['roe'] = df_quots['pb']*100/df_quots['per']
df_quots['close'] = map(swap_value, df_quots['trade'], df_quots['settlement'])

df_quots = df_quots[(df_quots['roe']>=5) & (df_quots['turnoverratio']>=2) & (df_quots['mktcap']>=500000000) & (df_quots['mktcap']>=30000000000) & (df_quots['close']<=50)]


temp = np.zeros(df_quots.shape[0])

index = 0
for code in df_quots['code']:
    price = get_stock_ma(code, 20)
    temp[index] = price
    index += 1

df_quots.insert(df_quots.shape[1], 'wma20', temp)


print df_quots

df_quots.to_csv('/home/ubuntu/x.csv', encoding='utf-8', index=False, float_format = '%.2f')  
