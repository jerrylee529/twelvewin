# -*- coding: utf-8 -*-

__author__ = 'Jerry Lee'


from redis_op import RedisOP


class Analyzer(object):
    """
    股票分析结果类，所有的关于股票的信息都从这个类获取
    """
    def __init__(self, app):
        self.app = app


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