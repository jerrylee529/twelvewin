
# -*- coding:utf-8 -*-
__author__ = 'jerry'

import pandas as pd
import tushare as ts
import datetime
from config import config
import numpy as np
import time

# 设置精度
pd.set_option('precision', 2)

# 财务年度
YEAR = 2017

# 财务季度
SEASON = 4 

key = ["code"]

today = datetime.date.today()

# 导出html表格
def export_report(dest, title):
    outputfile_date = "%s/%s_%s.csv" % (config.RESULT_PATH, title, today.strftime("%Y%m%d"),)

    dest.to_csv(outputfile_date, encoding='utf-8', index=False, float_format = '%.2f')

    outputfile = "%s/%s.csv" % (config.RESULT_PATH, title,)

    dest.to_csv(outputfile, encoding='utf-8', index=False, float_format = '%.2f')


# 交换值
def swap_value(x, y):
    return x if x!=0.00 else y


# 获取股票的均线
'''
def get_stock_ma(code, ma1, ma2, ma3):
    print "get data for " + code

    now = datetime.datetime.now()

    dt = now - datetime.timedelta(days=(max(ma1,ma2,ma3)*7+10))

    df = ts.get_k_data(code=code, ktype='W', autype='qfq', start=dt.strftime('%Y-%m-%d'), end=now.strftime('%Y-%m-%d'))

    if (df.empty):
        return 0 

    df.reset_index(inplace=True)

    df['ma'+str(ma1)] = df['close'].rolling(window=ma1).mean()
    df['ma'+str(ma2)] = df['close'].rolling(window=ma2).mean()
    df['ma'+str(ma3)] = df['close'].rolling(window=ma3).mean()

    price = []
    if (df.shape[0] > 0):
        ma1_value = df.iat[df.shape[0]-1, df.shape[1]-3]
        ma2_value = df.iat[df.shape[0]-1, df.shape[1]-2]
        ma3_value = df.iat[df.shape[0]-1, df.shape[1]-1]

        price.append(ma1_value)
        price.append(ma1_value if ma2_value is None else ma2_value)
        price.append(ma1_value if ma3_value is None else ma3_value)

    return price
'''

def get_stock_ma(code, ma1, ma2, ma3):
    print "get data for " + code

    now = datetime.datetime.now()

    dt = now - datetime.timedelta(days=(max(ma1,ma2,ma3)*7+10))

    df = ts.get_hist_data(code=code, ktype='W', start=dt.strftime('%Y-%m-%d'), end=now.strftime('%Y-%m-%d'))

    if (df.empty):
        return 0

    df.sort_index(inplace=True)

    df.reset_index(inplace=True)

    df.drop(labels=['ma5', 'ma10', 'ma20'], axis=1, inplace=True)

    df['ma'+str(ma1)] = df['close'].rolling(window=ma1).mean()
    df['ma'+str(ma2)] = df['close'].rolling(window=ma2).mean()
    df['ma'+str(ma3)] = df['close'].rolling(window=ma3).mean()

    price = []
    if (df.shape[0] > 0):
        ma1_value = df.iat[df.shape[0]-1, df.shape[1]-3]
        ma2_value = df.iat[df.shape[0]-1, df.shape[1]-2]
        ma3_value = df.iat[df.shape[0]-1, df.shape[1]-1]

        price.append(ma1_value)
        price.append(ma1_value if ma2_value is None else ma2_value)
        price.append(ma1_value if ma3_value is None else ma3_value)

    return price



def get_profit_report():
    df_quots = pd.DataFrame()

    for i in range(0,3):
        try:
            #获取最新股价
            df_quots = ts.get_today_all()

            if df_quots is not None:
                break  
        except:
            time.sleep(10*60) # 等待十分钟重试
            continue

    df_quots['roe'] = df_quots['pb']*100/df_quots['per']
    df_quots['close'] = map(swap_value, df_quots['trade'], df_quots['settlement'])

    df_quots = df_quots[(df_quots['roe']>=5) & (df_quots['turnoverratio']>=2) & (df_quots['nmc']>=300000) & (df_quots['nmc']<=3000000) & (df_quots['close']<=50)]

    df_quots.reset_index(inplace=True)
    df_quots = df_quots.drop(['index','changepercent','trade','open','high','low','settlement','volume','amount','mktcap'], axis=1)

    temp1 = np.zeros(df_quots.shape[0]) 
    temp2 = np.zeros(df_quots.shape[0])
    temp3 = np.zeros(df_quots.shape[0])

    ma10 = 10    
    ma30 = 30
    ma60 = 60

    index = 0
    for code in df_quots['code']:
        price = get_stock_ma(code, ma1=ma10, ma2=ma30, ma3=ma60)

        temp1[index] = price[0]	
        temp2[index] = price[1]
        temp3[index] = price[2]
        index += 1

    df_quots.insert(df_quots.shape[1], 'wma'+str(ma10), temp1)

    df_quots.insert(df_quots.shape[1], 'wma'+str(ma30), temp2)

    df_quots.insert(df_quots.shape[1], 'wma'+str(ma60), temp3)

    df_quots = df_quots.dropna(how='any')

    df_quots = df_quots[(df_quots['close']>df_quots['wma10']) & (df_quots['close']<df_quots['wma10']*1.1)]
  
    df_quots = df_quots[(df_quots['close']>df_quots['wma30']) & (df_quots['close']>df_quots['wma60']) & (df_quots['wma10']>=df_quots['wma30'])]    

    # 按现金股息率排行
    export_report(df_quots, title="stock_business")


if __name__=='__main__':
    get_profit_report()
