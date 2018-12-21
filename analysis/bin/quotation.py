# coding=utf8

"""
获取行情数据的接口
"""

__author__ = 'Administrator'

import tushare as ts
import text
import pandas as pd


"""
请求参数：
code: 证券代码：支持沪深A、B股 支持全部指数 支持ETF基金
ktype: 数据类型：默认为D日线数据 D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟
autype: 复权类型：qfq-前复权 hfq-后复权 None-不复权，默认为qfq
index: 是否为指数：默认为False 设定为True时认为code为指数代码
start: 开始日期 format：YYYY-MM-DD 为空时取当前日期
end: 结束日期 format：YYYY-MM-DD

返回：
date 日期和时间 低频数据时为：YYYY-MM-DD 高频数为：YYYY-MM-DD HH:MM
open 开盘价
close 收盘价
high 最高价
low 最低价
volume 成交量
code 证券代码
"""
# 获取历史行情数据
def get_history_data(code, start, end, ktype='D', autype='qfq', index=False):
    df = pd.DataFrame()

    try:
        df = ts.get_k_data(code=code, ktype=ktype, autype=autype, index=index, start=start, end=end)
    except Exception, e:
        print 'Exception:', repr(e)

        # 发送异常通知
        text.send_text("获取历史数据失败, %s" % code)

    return df


# 获取实时行情
def get_realtime_data():
    pass

