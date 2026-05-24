#!/usr/bin/python
#coding:utf-8

"""
为单个指数生成 LSTM 训练用历史数据集。

用法: downloaddata4lstm [code]
脚本从 2010-01-01 开始下载指定指数的历史行情，计算收盘价和成交量的
5/10/20/60 日均线，并将 3 个交易日后的收盘价写入 label 列，最终输出为
<code>.csv。
"""

__author__ = 'Administrator'

import tushare as ts
import sys
import datetime

if len(sys.argv) < 2:
    print "Usage: downloaddata4lstm [code]"
    sys.exit(2)

#代码
code = sys.argv[1]

#df = ts.get_stock_basics()
#date = df.ix[code]['timeToMarket'] #上市日期YYYYMMDD

#if date == 0:
#    print "Invalid timeToMarket"
#    sys.exit(2)

# 获取开始时间
#startDate = "%04d-%02d-%02d" % (date/10000, date/100%100, date%100)
startDate = "2010-01-01"

# 获得结束时间
now = datetime.datetime.now()  # 这是时间数组格式
# 转换为指定的格式:
endDate = now.strftime("%Y-%m-%d")

# 下载数据
df = ts.get_h_data(code, index=True, start=startDate, end=endDate)

# 改为以date为索引
df.sort_index(ascending=True, inplace=True)

# 删除code列
#df.pop('code')

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

# 增加label列
df['label'] = df['close']

labels = df['label']

for i in range(len(labels)):
    if i < len(labels)-3:
        labels[i] = labels[i+3]

filename = "%s.csv" % (code)

df.to_csv(filename)
