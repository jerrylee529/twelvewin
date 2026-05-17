# coding=utf8

"""
下载主要指数的历史日线数据。

脚本固定下载 000001、399001、000300、399005、399006 等指数的历史数据，
通过 tushare.get_h_data(index=True) 获取行情，按指数代码写入
commondatadef.dataPath/index/ 下的 txt 文件。
"""

__author__ = 'Administrator'

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

indexes = ['000001', '399001', '000300', '399005', '399006']


for index in indexes:
    filepath = "%s//index//%s.txt" % (commondatadef.dataPath, index)

    df = ts.get_h_data(index, index=True)

    df.sort_index(inplace=True)

    df.to_csv(filepath, header=None)


