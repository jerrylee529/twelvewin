# coding=utf8

__author__ = 'Administrator'

'''
下载指数的历史数据
'''

import tushare as ts
import pandas as pd
import numpy as np
import datetime
import os
import sys
from config import config
import time

reload(sys)
sys.setdefaultencoding('utf8')

print ts.__version__

#indexes = ['000001', '399001', '000300', '399005', '399006']

indexes = ['000905']

for index in indexes:
    filepath = "%s/%s.csv" % (config.INDEX_FILE_PATH, index)

    dfs = []
    for y in range(1991,2019):
        start = "%s-01-01" % y
        end = "%s-12-31" % y

        df = ts.get_h_data(index, index=True, start=start, end=end)

        df.sort_index(inplace=True)

        dfs.append(df)

        time.sleep(300)

    df_total = pd.concat(dfs, axis=0)
    
    df_total.reset_index(inplace=True)

    df_total.to_csv(filepath, index=False)

        
