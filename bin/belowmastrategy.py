# coding=utf8

__author__ = 'Administrator'

'''
1. 读取股票列表
2. 读取股票列表中每只股票的历史数据，
3. 计算移动平均线
4. 将低于移动平均线条件的股票筛选出来保存到文件
5. 将文件发送邮件到制定邮箱
'''

import commondatadef
import pandas as pd
import matplotlib
import datetime
import numpy as np
import matplotlib.pyplot as plt
from sendmail import sendmail

import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

matplotlib.style.use('ggplot')

ma = 60
change_percent = 20

# get instruments
# instruments = {'code':[2681]}
instruments = pd.read_csv(commondatadef.instrument_file_path, names=['code', 'name', 'industry'], dtype=str)

#
today = datetime.date.today()

#
result = pd.DataFrame()

instruments.index = instruments.index.astype(int)

print instruments.index

index = 0
for code in instruments['code']:
    name = instruments.loc[index, 'name']

    index += 1

    filepath = "%s/%s.txt" % (commondatadef.dataPath, code)

    #print filepath

    stock_data = pd.read_csv(filepath, names=['date', 'open', 'high', 'low', 'close', 'volume', 'amount'],
                             parse_dates=[0], index_col=0)

    col_ma = 'MA_' + str(ma)

    # 计算简单算术移动平均线MA - 注意：stock_data['close']为股票每天的收盘价
    stock_data[col_ma] = pd.ewma(stock_data['close'], ma)

    if len(stock_data) < 2:
        continue

    lastlast_record = stock_data.iloc[-2]

    last_record = stock_data.iloc[-1]
    last_date = stock_data.index[-1]

    p_change = (last_record[col_ma] - last_record['close']) * 100 / last_record['close']
    if p_change > change_percent:
        d = today  # + datetime.timedelta(days = -1)
        if d.strftime("%Y-%m-%d") == last_date.strftime("%Y-%m-%d"):
            last_record['date'] = last_date.strftime("%Y-%m-%d")
            last_record['name'] = name
            last_record['p_change'] = p_change
            result[code] = last_record

result = result.T

names = result.pop('name')
result.insert(0, 'name', names)

result = result.sort(['p_change'], ascending=False)

outputfile = "%s/belowma_%d_%d_%s.csv" % (commondatadef.resultPath, ma, change_percent, today.strftime("%Y%m%d"))

result.to_csv(outputfile, index=True, index_label=['code'], encoding='gbk')

subject = "背离%d日线的股票列表" % (ma,)
sendmail(subject, mailto=['38454880@qq.com'], content="Please check attachment", attachments=[outputfile])

#result.plot()
#plt.show()


# 将数据按照交易日期从近到远排序
#stock_data.sort('date', ascending=False, inplace=True)

# ========== 将算好的数据输出到csv文件 - 注意：这里请填写输出文件在您电脑中的路径
#outputfile = "%s/%06d_ma_ema.txt" % (commondatadef.dataPath, code)

#stock_data.to_csv(outputfile, index=False)

