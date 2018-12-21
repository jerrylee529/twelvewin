
# -*- coding:utf-8 -*-
__author__ = 'jerry'

import pandas as pd
import tushare as ts
import datetime
from sendmail import sendmail
import commondatadef
import csv2html as c2h

# 财务年度
YEAR = 2017

# 财务季度
SEASON = 3

key = ["code"]

today = datetime.date.today()


def export_report(source, columns, title):
    htmlfile = "/home/ubuntu/web/%s_%s.html" % (title, today.strftime("%Y%m%d"),)

    outputfile = "%s/finance_report_%s.csv" % (commondatadef.resultPath, today.strftime("%Y%m%d"),)

    dest = source.sort_values(["code"])

    dest.drop_duplicates(inplace=True)

    dest.to_csv(outputfile, encoding='utf-8', index=False)

    c2h.csv2html(outputfile, htmlfile, title, columns)

#获取股票列表
df_basic = ts.get_stock_basics()
df_basic.reset_index(inplace=True)

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
columns = {}
columns['name'] = ['代码', '名称', '所属行业', '地区', '市盈率', '流通股本(亿)','总股本(亿)', '总资产(万)', '流动资产', '固定资产', '公积金', '每股公积金', '每股收益', '每股净资产', '市净率', '上市日期', '未分利润', '每股未分配', '收入同比(%)', '利润同比(%)', '毛利率(%)', '净利润率(%)', '股东人数']
columns['index'] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

export_report(df_basic, columns=columns, title="股票列表")

#获取业绩报表
df_achievements = ts.get_report_data(YEAR, SEASON)

'''
code,代码
name,名称
esp,每股收益
eps_yoy,每股收益同比(%)
bvps,每股净资产
roe,净资产收益率(%)
epcf,每股现金流量(元)
net_profits,净利润(万元)
profits_yoy,净利润同比(%)
distrib,分配方案
report_date,发布日期
'''
columns = {}
columns['name'] = ['代码', '名称', '每股收益', '每股收益同比', '每股净资产', '每股现金流量','净利润', '净利润同比', '分配方案', '发布日期']
columns['index'] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

export_report(df_achievements, columns=columns, title="业绩报表")

df_achievements.reset_index(inplace=True)
df_achievements = df_achievements.drop(['index', 'name'], axis=1)

df = pd.merge(df_basic, df_achievements, how='left', on=key)


#获取盈利能力
df_profits = ts.get_profit_data(YEAR, SEASON)
df_profits.reset_index(inplace=True)
df_profits = df_profits.drop(['index', 'name'], axis=1)

'''
code,代码
name,名称
roe,净资产收益率(%)
net_profit_ratio,净利率(%)
gross_profit_rate,毛利率(%)
net_profits,净利润(万元)
esp,每股收益
business_income,营业收入(百万元)
bips,每股主营业务收入(元)
'''
columns = {}
columns['name'] = ['代码', '名称', '净资产收益率(%)', '净利率(%)', '毛利率(%)', '净利润(万元)','每股收益', '营业收入(百万元)', '每股主营业务收入(元)']
columns['index'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]

export_report(df_profits, columns=columns, title="盈利能力报表")

df = pd.merge(df, df_profits, how='left', on=key)

#获取营运能力
df_operations = ts.get_operation_data(YEAR, SEASON)
df_operations.reset_index(inplace=True)
df_operations = df_operations.drop(['index', 'name'], axis=1)

'''
code,代码
name,名称
arturnover,应收账款周转率(次)
arturndays,应收账款周转天数(天)
inventory_turnover,存货周转率(次)
inventory_days,存货周转天数(天)
currentasset_turnover,流动资产周转率(次)
currentasset_days,流动资产周转天数(天)
'''
columns = {}
columns['name'] = ['代码', '名称', '应收账款周转率(次)', '应收账款周转天数(天)', '存货周转率(次)', '存货周转天数(天)','流动资产周转率(次)', '流动资产周转天数(天)']
columns['index'] = [0, 1, 2, 3, 4, 5, 6, 7]

export_report(df_operations, columns=columns, title="营运能力报表")

df = pd.merge(df, df_operations, how='left', on=key)

quit()

#成长能力
df_growths = ts.get_growth_data(YEAR, SEASON)
df_growths.reset_index(inplace=True)
df_growths = df_growths.drop(['index', 'name'], axis=1)

df = pd.merge(df, df_growths, how='left', on=key)

#获取偿债能力
df_paydebts = ts.get_debtpaying_data(YEAR, SEASON)
df_paydebts.reset_index(inplace=True)
df_paydebts = df_paydebts.drop(['index', 'name'], axis=1)

df = pd.merge(df, df_paydebts, how='left', on=key)

#获取现金流量
df_cashs = ts.get_cashflow_data(YEAR, SEASON)
df_cashs.reset_index(inplace=True)
df_cashs = df_cashs.drop(['index', 'name'], axis=1)

df = pd.merge(df, df_cashs, how='left', on=key, sort=True)

df.drop_duplicates(inplace=True)

outputfile = "%s/finance_report_%s.csv" % (commondatadef.resultPath,today.strftime("%Y%m%d"),)

df.to_csv(outputfile, encoding='utf-8', index=False)

quit()

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


columns = {}
columns['name'] = ['code','name','industry','area','pe','outstanding','totals','totalAssets','liquidAssets','fixedAssets','reserved','reservedPerShare','esp']
columns['index'] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

htmlfile = "/home/ubuntu/web/finance_report_%s.html" % (today.strftime("%Y%m%d"),)


c2h.csv2html(outputfile, htmlfile, "股票列表", columns)

