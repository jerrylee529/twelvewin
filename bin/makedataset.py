# coding=utf8

__author__ = 'jerry'


import tushare as ts
import pandas as pd
import commondatadef
import numpy as np
import datetime
from datetime import timedelta
import os
import sys
import stock_utility as su
import commondatadef as cdd
import pandas as pd



def handleData(code, days):
    filename = "%s/%s.csv" % (commondatadef.data_dayPath, code)

    #——————————————————导入数据——————————————————————
    df = pd.read_csv(filename)     #读入股票数据

    # 改为以date为索引
    #df.sort_index(ascending=True, inplace=True)

    # 计算收盘价的5,10,20,60移动平均线
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()

    # 计算成交量的5,10,20,60移动平均线
    df['va5'] = df['volume'].rolling(window=5).mean()
    df['va10'] = df['volume'].rolling(window=10).mean()
    df['va20'] = df['volume'].rolling(window=20).mean()
    df['va60'] = df['volume'].rolling(window=60).mean()

    labels = df['close']
    
    true_labels = 0

    if days < len(labels):
        final_labels = labels[days:]
        new_index = range(0, len(labels)-days)
        
        true_labels = pd.Series(final_labels.values, index=new_index)
    else:
        print "invalid days: %d" % (days)

    df['labels'] = true_labels

    dataset_filename = "%s/%s.csv" % (commondatadef.dataPath, code)

    df.sort_index(ascending=True, inplace=True)

    df.to_csv(dataset_filename, index=False)

    return df


if len(sys.argv) < 2:
    print "Usage: script [code]"
    sys.exit(2)

#代码
code = sys.argv[1]


#
handleData(code, days=3)
