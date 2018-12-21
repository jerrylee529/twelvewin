#!/usr/bin/python
#coding:utf-8

__author__ = 'Administrator'

'''
下载指数的历史数据用于lstm计算
'''

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
