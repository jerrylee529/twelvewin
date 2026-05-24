# coding=utf8

"""
筛选当日向上突破均线的股票。

脚本读取 commondatadef.instrument_file_path 股票列表和 commondatadef.dataPath
下的历史行情文件，分别计算 20 日和 60 日简单移动均线。若最新收盘价站上均线、
前一日收盘价在均线下方且均线本身向上，则输出 mafilter_*.csv 并邮件发送。
"""

__author__ = 'Administrator'

import commondatadef
import pandas as pd
import matplotlib
import datetime
import numpy as np
import matplotlib.pyplot as plt
from sendmail import  sendmail

import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

matplotlib.style.use('ggplot')

MAs = [20, 60]

# get instruments
#instruments = {'code':[2681]}
instruments = pd.read_csv(commondatadef.instrument_file_path, names=['code','name','industry'], dtype=str)

#
today = datetime.date.today()


instruments.index = instruments.index.astype(int)

print instruments.index

#
for ma in MAs:
    result = pd.DataFrame()

    index = 0
    for code in instruments['code']:
        name = instruments.loc[index, 'name']

        index += 1

        filepath = "%s/%s.txt" % (commondatadef.dataPath, code)

        #print filepath

        stock_data = pd.read_csv(filepath, names=['date', 'open', 'high', 'low', 'close', 'volume', 'amount'], parse_dates=[0], index_col=0)

        col_ma = 'MA_' + str(ma)

        # 计算简单算术移动平均线MA - 注意：stock_data['close']为股票每天的收盘价
        stock_data[col_ma] = pd.rolling_mean(stock_data['close'], ma)

        if len(stock_data) < 2:
            continue

        lastlast_record = stock_data.iloc[-2]

        last_record = stock_data.iloc[-1]
        last_date = stock_data.index[-1]

        if (last_record[col_ma] > lastlast_record[col_ma]) and (last_record['close'] > last_record[col_ma]) and (lastlast_record['close'] < last_record[col_ma]):
            d = today #+ datetime.timedelta(days = -1)
            if  d.strftime("%Y-%m-%d") == last_date.strftime("%Y-%m-%d"):
                last_record['date'] = last_date.strftime("%Y-%m-%d")
                last_record['name'] = name
                result[code] = last_record

    result = result.T

    names = result.pop('name')
    result.insert(0, 'name', names)

    # 输出到文件
    outputfile = "%s/mafilter_%d_%s.csv" % (commondatadef.resultPath, ma, today.strftime("%Y%m%d"))

    result.to_csv(outputfile, index=True, index_label=['code'], encoding='gbk')

    subject = "突破%d日线的股票列表" % (ma,)

    sendmail(subject, mailto=['38454880@qq.com'], content="Please check attachment", attachments=[outputfile])

#result.plot()
#plt.show()


# 将数据按照交易日期从近到远排序
#stock_data.sort('date', ascending=False, inplace=True)

# ========== 将算好的数据输出到csv文件 - 注意：这里请填写输出文件在您电脑中的路径
#outputfile = "%s/%06d_ma_ema.txt" % (commondatadef.dataPath, code)

#stock_data.to_csv(outputfile, index=False)
