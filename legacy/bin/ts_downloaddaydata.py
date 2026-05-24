# coding=utf8

"""
下载所有股票日线数据并生成 TensorFlow 预测数据集。

脚本通过 stock_utility 获取股票列表，逐只增量下载 hfq 后复权日线到
commondatadef.data_dayPath；随后为每只股票计算收盘价和成交量的 5/10/20/60
日均线，并将 3 个交易日后的收盘价写入 labels 列，输出到 commondatadef.dataPath。
每只股票处理后 sleep 60 秒以降低接口调用频率。
"""

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
import time

reload(sys)
sys.setdefaultencoding('utf8')

print ts.__version__

# 下载数据
instruments = su.get_stock_list()

# 如果下载成功，则保存
if not instruments is None:
    print "download instruments success, save to file %s" % (cdd.code_list_file)
    instruments.to_csv(cdd.code_list_file)
else:
    print "download instruments success, read from file %s" % (cdd.code_list_file)
    instruments = pd.read_csv(cdd.code_list_file,  index_col=['code'])

if instruments is None:
    print "instruments is empty, exit"
    exit()

#
today = datetime.date.today()

#
def downloadstock(instrument, startdate, enddate, filepath):
    df = ts.get_h_data(instrument, start=startdate, end=enddate, autype='hfq')

    df.sort_index(inplace=True)

    df.to_csv(filepath)

# 是否数字
def isNum(value):
    try:
        float(value) + 1
    except TypeError:
        return False
    except ValueError:
        return False
    else:
        return True

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


#
for code in instruments.index:
    filepath = "%s/%s.csv" % (commondatadef.data_dayPath, code)
    print "starting download %s, file path: %s" % (code, filepath)
    startdate = "1990-01-01"
    enddate = today.strftime("%Y-%m-%d")
    df = pd.DataFrame()
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, index_col=['date'])
        last_date = datetime.datetime.strptime(df.index[-1], "%Y-%m-%d") + datetime.timedelta(days=1)
        startdate = last_date.strftime("%Y-%m-%d")
        print "file %s exists, download data from %s" % (filepath, startdate)

    data_enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d") + timedelta(days=1)

    print "download data, code: %s, startdate: %s, enddate: %s" % (code, startdate, data_enddate.strftime("%Y-%m-%d"))

    try:
        df_download = ts.get_h_data(code, start=startdate, end=data_enddate.strftime("%Y-%m-%d"), autype='hfq')
    except:
        print "download failure, code: %s" % code
        continue

    if not (df_download is None):
        #
        df_download.sort_index(inplace=True)

        if os.path.exists(filepath):
            df_download.to_csv(filepath, mode='a', header=None)
        else:
            df_download.to_csv(filepath)

    #处理数据，增加ma等指标 
    handleData(code, 3)

    #等待时间
    time.sleep(60)
