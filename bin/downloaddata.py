# coding=utf8

"""
增量下载股票后复权历史日线数据。

脚本读取 commondatadef.instrument_file_path 股票列表，为每只股票检查
commondatadef.dataPath 下已有的历史 txt 文件，从最后交易日的下一天开始
通过 tushare.get_h_data 下载 hfq 后复权数据，并追加写回原文件。
"""

__author__ = 'Administrator'

import tushare as ts
import pandas as pd
import commondatadef
import numpy as np
import datetime
from datetime import timedelta
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

print ts.__version__

# get instruments
instruments = pd.read_csv(commondatadef.instrument_file_path, names=['code','name','industry'], dtype=str)

#
today = datetime.date.today()

#
def downloadstock(instrument, startdate, enddate, filepath):
    df = ts.get_h_data(instrument, start=startdate, end=enddate, autype='hfq')

    df.sort_index(inplace=True)

    df.to_csv(filepath, header=None)

#
for code in instruments['code']:
    filepath = "%s/%s.txt" % (commondatadef.dataPath, code)
    print filepath
    startdate = "2005-01-01"
    enddate = today.strftime("%Y-%m-%d")
    df = pd.DataFrame()
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, names=['date', 'open', 'high', 'low', 'close', 'volume', 'amount'], index_col=0)
        last_date = datetime.datetime.strptime(df.index[-1], "%Y-%m-%d") + datetime.timedelta(days=1)
        startdate = last_date.strftime("%Y-%m-%d")

    if startdate == enddate:
        continue

    data_enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d") + timedelta(days=1)

    print "download data, code: %s, startdate: %s, enddate: %s" % (code, startdate, data_enddate.strftime("%Y-%m-%d"))

    df_download = ts.get_h_data(code, start=startdate, end=data_enddate.strftime("%Y-%m-%d"), autype='hfq')

    if df_download is None:
        continue

    #
    close = df_download.pop('low')
    df_download.insert(2, 'low', close)

    df_download.sort_index(inplace=True)

    df_download.to_csv(filepath, header=None, mode='a')


