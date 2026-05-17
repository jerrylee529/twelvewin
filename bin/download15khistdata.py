# coding=utf8

"""
下载股票列表和 15 分钟 K 线历史数据。

脚本通过 tushare 获取全部股票基础信息，先保存到 C:/Stock/stocklist.csv，
再为每只股票下载从 2013-01-01 开始的 15 分钟线历史数据，按股票代码写入
C:/Stock/data/15K/。输出文件使用 GBK 编码，面向旧 Windows 本地数据目录。
"""

__author__ = 'jerry'

import tushare as ts
import os,time,sys,re,datetime


#输出CSV文件，其中要进行转码，不然会乱码
def output_csv(df, folder, code):
    TODAY = datetime.date.today()
    CURRENTDAY=TODAY.strftime('%Y-%m-%d')
    reload(sys)
    sys.setdefaultencoding('gbk')
    df.to_csv(folder + code + '.csv', encoding='gbk')#选择保存

# 获取股票基本信息
#code,代码
#name,名称
#industry,所属行业
#area,地区
#pe,市盈率
#outstanding,流通股本
#totals,总股本(万)
#totalAssets,总资产(万)
#liquidAssets,流动资产
#fixedAssets,固定资产
#reserved,公积金
#reservedPerShare,每股公积金
#eps,每股收益
#bvps,每股净资
#pb,市净率
#timeToMarket,上市日期
def get_stock_list():
    df = ts.get_stock_basics()
    return df


# 获取历史数据
def get_hist_data(df_code, ktype, folder, start):
    for code in df_code.index:

        df = ts.get_hist_data(code, ktype=ktype, start=start)

        if df is not None:
            output_csv(df, folder, code)

df = get_stock_list()

output_csv(df, 'C:/Stock/', 'stocklist')

get_hist_data(df, '15', 'C:/Stock/data/15K/', '2013-01-01')

