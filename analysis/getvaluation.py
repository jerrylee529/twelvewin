
# -*- coding:utf-8 -*-
__author__ = 'jerry'

import pandas as pd
import tushare as ts
import datetime
from config import config

# 设置精度
pd.set_option('precision', 2)

# 财务年度
YEAR = 2017

# 财务季度
SEASON = 4 

key = ["code"]

today = datetime.date.today()

# 导出html表格
def export_report(dest, title):
    outputfile_date = "%s/%s_%s.csv" % (config.RESULT_PATH, title, today.strftime("%Y%m%d"),)

    dest.to_csv(outputfile_date, encoding='utf-8', index=False, float_format = '%.2f')

    outputfile = "%s/%s.csv" % (config.RESULT_PATH, title,)

    dest.to_csv(outputfile, encoding='utf-8', index=False, float_format = '%.2f')


# 交换值
def swap_value(x, y):
    return x if x!=0.00 else y


def get_valuation_report():
    # 获取股票列表
    df_basic = ts.get_stock_basics()

    df_basic['roe'] = df_basic['esp']*100/df_basic['bvps']

    df_basic['peg'] = df_basic['pe']/df_basic['profit']
    #df_basic['value_increase'] = df_basic['esp']*(8.5+2*df_basic['profit']/100)

    df_basic.reset_index(inplace=True)
    df_basic = df_basic.drop(['area', 'outstanding', 'totalAssets', 'liquidAssets', 'fixedAssets', 'reserved', 'reservedPerShare', 'undp', 'perundp', 'rev', 'profit', 'gpr', 'npr', 'holders'], axis=1)

    '''
    code,代码
    name,名称
    industry,所属行业
    area,地区
    pe,市盈率
    outstanding,流通股本(亿)
    totals,总股本(亿)
    totalAssets,总资产(万)
    liquidAssets,流动资产
    fixedAssets,固定资产
    reserved,公积金
    reservedPerShare,每股公积金
    esp,每股收益
    bvps,每股净资
    pb,市净率
    timeToMarket,上市日期
    undp,未分利润
    perundp, 每股未分配
    rev,收入同比(%)
    profit,利润同比(%)
    gpr,毛利率(%)
    npr,净利润率(%)
    holders,股东人数
    '''

    #获取最新股价
    df_quots = ts.get_today_all()  

    '''
    code：代码
    name:名称
    changepercent:涨跌幅
    trade:现价
    open:开盘价
    high:最高价
    low:最低价
    settlement:昨日收盘价
    volume:成交量
    turnoverratio:换手率
    amount:成交量
    per:市盈率
    pb:市净率
    mktcap:总市值
    nmc:流通市值
    '''

    df_quots['close'] = map(swap_value, df_quots['trade'], df_quots['settlement'])

    df_quots.reset_index(inplace=True)
    df_quots = df_quots.drop(['index','name','changepercent','trade','open','high','low','settlement','volume','turnoverratio','amount','per','pb','nmc'], axis=1)

    df = pd.merge(df_basic, df_quots, how='left', on=key)

    df['value'] = df['esp']/0.08

    df['rate'] = (df['value']-df['close'])*100/df['close']

    #df['rate_inc'] = (df['value_increase']-df['close'])*100/df['close']

    df = df.sort_values(["rate"], ascending=False)

    df.drop_duplicates(inplace=True)

    columns = {}
    columns['name'] = ['代码', '名称', '所属行业', '市盈率', '总股本(亿)', '每股收益', '每股净资产', '市净率', '上市日期', '净资产收益率', 'PEG',  '总市值', '现价', '估值', '估值差(%)']
    columns['index'] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

    export_report(df, columns=columns, title="stockvaluation")


# 获取股票的均线
def get_stock_ma(code, ma):
    df = ts.get_k_data(code=code, ktype='W', autype='qfq')

    df['ma'+str(ma)] = df['close'].rolling(window=ma).mean()

    return df


def get_profit_report():
    df = ts.profit_data(top=4000)

    df = df.sort_values('divi', ascending=False)

    #获取最新股价
    df_quots = ts.get_today_all()

    df_quots['roe'] = df_quots['pb']*100/df_quots['per']
    #df_basic['peg'] = df_basic['pe']/df_basic['profit']
    df_quots['close'] = map(swap_value, df_quots['trade'], df_quots['settlement'])


    df_quots.reset_index(inplace=True)
    df_quots = df_quots.drop(['index','name','changepercent','trade','open','high','low','settlement','volume','turnoverratio','amount','nmc'], axis=1)

    df = pd.merge(df, df_quots, how='left', on=key)

    df['rate'] = df['divi']/10*100/df['close']	

    df['valueprice'] = df['roe']*(df['close']/df['pb'])/15

    df = df.sort_values('rate', ascending=False)

    #df['value'] = df['esp']/0.08

    #df['rate'] = (df['value']-df['close'])*100/df['close']

    df = df[df['per']>0]

    df = df.sort_values('report_date', ascending=False)

    df = df.drop_duplicates(['name'])


    # 按现金股息率排行
    df = df.sort_values('rate', ascending=False)
    export_report(df, title="stock_dividence")

    # 按roe排行
    df = df.sort_values('roe', ascending=False)
    export_report(df, title="stock_roe")

    # 按市盈率
    df = df.sort_values('per', ascending=True)
    export_report(df, title="stock_pe")

    # 按市净率
    df = df.sort_values('pb', ascending=True)
    export_report(df, title="stock_pb") 

    # 不排序
    df = df.sort_values('mktcap', ascending=True)
    export_report(df, title="stock_value")

    # 按peg排行
    #export_report(df, columns=columns, title="stock_pb")

if __name__ == '__main__':
    get_profit_report()
