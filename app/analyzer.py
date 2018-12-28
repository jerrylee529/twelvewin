# -*- coding: utf-8 -*-

__author__ = 'Jerry Lee'


from redis_op import RedisOP
from app.models import Instrument


class Analyzer(object):
    """
    股票分析结果类，所有的关于股票的信息都从这个类获取
    """
    def __init__(self, app, db):
        self.app = app

        self.db = db

        self.securities = []

        self.instruments = []

        self._get_instruments()

    # 获取所有的股票信息
    def _get_instruments(self):
        try:
            self.securities = self.db.session.query(Instrument).all()

            index = 1
            for security in self.securities:
                if (security.code is None) or (security.code == ''):
                    continue
                item = {}
                item['id'] = index
                item['code'] = security.code
                item['name'] = security.name
                self.instruments.append(item)
                index += 1
        except Exception, e:
            print(str(e))

    # 获取行情数据
    def get_quotation(self, code):
        try:
            redisOP = RedisOP()
            quot = redisOP.get_hash(code)
        except Exception as e:
            print(str(e))

        return quot

    # 获取预测值
    def get_prediction(self, code):
        pass