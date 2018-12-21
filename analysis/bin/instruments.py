# coding=utf8

"""
股票代码相关函数
"""

__author__ = 'Administrator'

import tushare as ts
import numpy as np
import text
from ..models import Instrument, Session
from ..config import config


# 字符串转换为浮点
def value_2_float(value):
    if np.isnan(value):
        return None
    else:
        return float(value)


# 获取所有股票列表并保存到文件
def get_instrument_list(config):
    try:
        # 下载数据
        df = ts.get_stock_basics()

        # 按照代码排序
        df.sort_index(inplace=True)

        # 保存到文件
        df.to_csv(config.INSTRUMENT_FILENAME)

        session = Session()

        for index, row in df.iterrows():
            item = Instrument(row['code'], name=row['name'], industry=row['industry'], area=row['area'],
                              pe=value_2_float(row['pe']), outstanding=value_2_float(row['outstanding']),
                              totals=value_2_float(row['totals']), total_assets=value_2_float(row['totalAssets']),
                              liquid_assets=value_2_float(row['liquidAssets']),
                              fixed_assets=value_2_float(row['fixedAssets']), reserved=value_2_float(row['reserved']),
                              reserved_per_share=value_2_float(row['reservedPerShare']), esp=value_2_float(row['esp']),
                              bvps=value_2_float(row['bvps']), pb=value_2_float(row['pb']),
                              time_2_market=value_2_float(row['timeToMarket']), undp=value_2_float(row['undp']),
                              perundp=value_2_float(row['perundp']), rev=value_2_float(row['rev']),
                              profit=value_2_float(row['profit']), gpr=value_2_float(row['gpr']),
                              npr=value_2_float(row['npr']), holders=value_2_float(row['holders']))

            session.add(item)

        session.commit()
    except Exception, e:
        print 'Exception:', repr(e)

        # 发送异常通知
        text.send_text("处理股票代码数据失败")

    return df

if __name__ == '__main__':
    get_instrument_list(config=config)