# coding=utf8

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