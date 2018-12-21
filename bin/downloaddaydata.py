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

reload(sys)
sys.setdefaultencoding('utf8')

print ts.__version__

# 下载数据
instruments = su.get_stock_list()

# 如果下载成功，则保存
if instruments is not None:
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

def handleData(df):
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

    return df  

# 增加label列
df['label'] = df['close']

labels = df['label']

for i in range(len(labels)):
    if i != len(labels)-1:
        labels[i] = labels[i+1]


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

        #modified = False
        #dflen = df.shape[0]
        #for i in range(0, dflen):
        #    x = df.iat[i, 1]
        #    if (i > 1) and (isNum(x) is False):
        #        print "remove row: %d" % (i, )
        #        df.drop('date', inplace=True)
        #        modified = True
        #        break

        #if modified is True:
        #    print "save file %s" % (filepath, )
        #    df.to_csv(filepath)

    data_enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d") + timedelta(days=1)

    print "download data, code: %s, startdate: %s, enddate: %s" % (code, startdate, data_enddate.strftime("%Y-%m-%d"))

    df_download = ts.get_h_data(code, start=startdate, end=data_enddate.strftime("%Y-%m-%d"), autype='hfq')

    if df_download is None:
        continue

    #
    df_download.sort_index(inplace=True)

    if os.path.exists(filepath):
        df_download.to_csv(filepath, mode='a', header=None)
    else:
        df_download.to_csv(filepath)


