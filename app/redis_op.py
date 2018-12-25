# -*- coding: utf-8 -*-

__author__ = 'Administrator'


import redis
import re


class RedisOP(object):
    """
    redis操作类，封装了redis连接池
    """
    def __init__(self):
        if not hasattr(RedisOP, 'pool'):
            raise Exception('No connection pool')
        self.conn = redis.Redis(connection_pool=RedisOP.pool)

    @staticmethod
    def create_pool(config):
        url = config['REDIS_URL']
        host = ''
        port = 6793
        password = ''
        db = 0
        if url is not None:
            match_result = re.match(r'redis://:(.*)@(.*):(.*)/(.?)', url, re.M|re.I)

            if match_result:
                password = match_result.group(1)
                host = match_result.group(2)
                port = int(match_result.group(3))
                db = int(match_result.group(4))

        RedisOP.pool = redis.ConnectionPool(host=host, password=password, port=port, db=db)

    """
    string类型 {'key':'value'} redis操作
    """
    def set_value(self, key, value, time=None):
        if time:
            res = self.conn.setex(key, value, time)
        else:
            res = self.conn.set(key, value)
        return res

    def get_value(self, key):
        res = self.conn.get(key).decode()
        return res

    def del_key(self, key):
        res = self.conn.delete(key)
        return res

    """
    hash类型，{'name':{'key':'value'}} redis操作
    """
    def set_hash(self, name, key, value):
        res = self.conn.hset(name, key, value)
        return res

    # 设置多个field-value, mapping为字典格式
    def set_m_hash(self, name, mapping):
        res = self.conn.hmset(name, mapping)
        return res

    def get_hash(self, name, key=None):
        # 判断key是否我为空，不为空，获取指定name内的某个key的value; 为空则获取name对应的所有value
        if key:
            res = self.conn.hget(name, key)
        else:
            res = self.conn.hgetall(name)
        return res

    def del_hash_key(self, name, key=None):
        if key:
            res = self.conn.hdel(name, key)
        else:
            res = self.conn.delete(name)
        return res