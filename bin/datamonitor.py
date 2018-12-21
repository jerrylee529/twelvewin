# -*- coding:utf-8 -*-

__author__ = 'jerry'

'''
1. 读取文件中定义的股票代码
2. 当股票的价格变化比率超过设置的阈值时发送告警列表到制定邮箱
'''

from threading import Timer
import time
from datetime import datetime, timedelta
import os
import pandas as pd
import tushare as ts
from sendmail import sendmail

stock_list = pd.read_csv('c:/stock/monitoring_stocks.csv', encoding='gbk', dtype=str)

#


#
def refreshquots():
    str_result = ''

    quots = ts.get_realtime_quotes(stock_list['code'])

    i = 0
    for code in stock_list['code']:
        #
        price = float(stock_list.loc[i, 'price'])

        trade = float(quots.loc[i, 'price'])

        changeratio = (trade-price)*100/price

        change = stock_list.loc[i, 'change']

        name = stock_list.loc[i, 'name']

        if float(changeratio) > float(change):
            strTmp = "alarm, code: %s, name: %s, base price: %.2f, current price: %.2f, change: %.2f%%\n" % (code, name, price, trade, changeratio)
            str_result = str_result + strTmp
            #print str1
        else:
            print "no alarm, code: %s, name: %s, base price: %.2f, current price: %.2f, change: %.2f%%" % (code, name, price, trade, changeratio)

        i += 1

    #
    if not strTmp == '':
        sendmail('股票告警列表', mailto=['38454880@qq.com'], content=str_result, attachments=None)

#
while True:
    refreshquots()
    time.sleep(60)
