# coding=utf8

__author__ = 'Administrator'

'''
下载分钟K线的历史数据
'''

import tushare as ts
import pandas as pd
import commondatadef
import numpy as np
import datetime
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

print ts.__version__

# 获取股票代码
configfile = commondatadef.configPath + '/instruments.txt'

instruments = pd.DataFrame()

if not os.path.exists(configfile):
    instruments = ts.get_industry_classified()
    instruments.to_csv(configfile, header=None)
else:
    instruments = pd.read_csv(configfile, names=['code','name','industry'])

#
today = datetime.date.today()

#
def downloadstock(instrument, startdate, enddate, ktype, filepath):
    df = ts.get_hist_data(instrument, start=startdate, end=enddate, ktype=ktype)

    df.sort_index(inplace=True)

    df.to_csv(filepath, header=None)

#
for instrument in instruments['code']:
    filepath = "%s/%06d.txt" % (commondatadef.minPath, instrument)
    print filepath
    startdate = "2005-01-01"
    enddate = today.strftime("%Y-%m-%d")

    code = "%06d" % (instrument, )
    df_download = ts.get_hist_data(code, start=startdate, end=enddate, ktype='5')

    df_download.sort_index(inplace=True)

    df_download.to_csv(filepath, mode='a')


