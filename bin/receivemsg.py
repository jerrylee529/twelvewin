# coding=utf8

"""
批量下载行业分类股票的后复权历史行情。

脚本通过 tushare.get_industry_classified 获取股票列表，逐只下载
2009-01-01 到 2015-11-04 的 hfq 后复权历史数据，并保存为
C:/Stock/Data/<code>.txt。文件名 receivemsg 与实际功能不匹配，实际用途是旧数据下载。
"""

__author__ = 'Administrator'

import tushare as ts
import pandas as pd

print ts.__version__

# get all industry
#codes = ts.get_industry_classified()

#
instruments = ts.get_industry_classified()
#instruments = pd.DataFrame([{'code':'000001', 'name':'pingan'}])

#
#print codes

#
for instrument in instruments['code']:
    df = ts.get_h_data(instrument, start='2009-01-01', end='2015-11-04', autype='hfq')

    df.sort_index(inplace=True)

    filename = 'C:/Stock/Data/' + instrument + '.txt'

    df.to_csv(filename, header=None)

    #downloadcode('C:/Users/Administrator/Desktop/Day/', code=instrument, startdate='2009-1-1', enddate='2015-10-27', fqtype='hfq')
