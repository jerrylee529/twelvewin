# -*- coding: utf-8 -*-

__author__ = 'Jerry Lee'


from redis_op import RedisOP
from app.models import Instrument
from sklearn import svm,preprocessing
from sklearn.externals import joblib
import pandas as pd
import os


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
        file_path = self.app.config['DAY_FILE_PATH'] + '/' + code + '.csv'
        df = pd.read_csv(file_path)
        df.set_index('date', inplace=True)
        df.drop(['code'], axis=1, inplace=True)

        # 将日期作为index,顺序排列
        df = df.sort_index()
        # print df.head()
        # value表示涨跌
        value = pd.Series(df['close'] - df['close'].shift(1), index=df.index)

        value = value.ffill()
        value[value >= 0] = 1
        value[value < 0] = 0
        df['Value'] = value

        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma250'] = df['close'].rolling(window=250).mean()

        # 后向填充空缺值
        df = df.fillna(method='bfill')
        df = df.astype('float64')
        # print df.head()

        # 选取数据的80%作为训练集，20%作为测试集
        L = len(df)
        predict_length = 5
        train_length = L-predict_length

        # 对样本特征进行归一化处理
        df_X = df.drop(['Value'], axis=1)
        df_X = preprocessing.scale(df_X)

        # 开始循环预测，每次向前预测一个值
        correct = 0

        model_filename = self.app.config['RESULT_PATH'] + '/' + code + '.model'

        # 如果存在模型文件则加载改模型文件，不存在则创建一个
        if os.path.exists(model_filename):
            classifier = joblib.load(model_filename)
        else:
            classifier = svm.SVC(C=1.0, kernel='rbf')

        data_train = df_X[0:train_length]
        value_train = value[0:train_length]
        data_predict = df_X[train_length:]

        #classifier.fit(data_train, value_train)
        value_predict = classifier.predict(data_predict)

        joblib.dump(classifier, model_filename)

        print df.index.values[L-predict_length:], value.values[L-predict_length:], value_predict

        return df.index.values[L-predict_length:], value.values[L-predict_length:], value_predict