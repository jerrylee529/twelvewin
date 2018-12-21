# coding=utf8

__author__ = 'Administrator'

'''
下载指数的历史数据
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

indexes = ['000001', '399001', '000300', '399005', '399006']


for index in indexes:
    filepath = "%s//index//%s.txt" % (commondatadef.dataPath, index)

    df = ts.get_h_data(index, index=True)

    df.sort_index(inplace=True)

    df.to_csv(filepath, header=None)


