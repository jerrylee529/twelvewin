# -*- coding: utf-8 -*-


__author__ = 'Administrator'

"""
按时间段更新行情并写入到redis
"""

import redis
import tushare as ts
import time
import random
import sys   #reload()之前必须要引入模块
reload(sys)
sys.setdefaultencoding('utf-8')

REALTIME_QUOTATION_KEY = 'realtime_quotation'

"""
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
"""
field_list = ["code", "name", "changepercent", "trade", "open", "high", "low", "settlement", "volume", "turnoverratio", "amount", "per", "pb", "mktcap", "nmc"]


def update():
    print "start updating"
    try:
        redis_db = redis.StrictRedis(host='localhost', port=8081, password='tw!@#$1234', decode_responses=False)   # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379

        df = ts.get_today_all()

        #data = df.to_msgpack(compress='zlib') # 直接转成msg写入redis
        #redis_db.set(REALTIME_QUOTATION_KEY, data)  # key是"realtime_quotation" value是data 将键值对存入redis缓存
        
        for index, row in df.iterrows():
            code = row["code"]

            values = {}
            for field in field_list:
                values[field] = row[field]

            values["update_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            redis_db.hmset(code, values)

        '''
        cached_data = redis_db.get(REALTIME_QUOTATION_KEY)

        df = pd.read_msgpack(cached_data)

        print df
        '''
    except Exception as e:
        print str(e)

if __name__ == '__main__':
    while True:
        current_time = time.localtime(time.time())
        if (current_time.tm_hour <= 15) and (current_time.tm_hour >= 9) and (current_time.tm_wday >= 0) and (current_time.tm_wday <= 6):
            update()
            time.sleep(60*random.randint(10, 30))
        else:
            time.sleep(60)
