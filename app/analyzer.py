# -*- coding: utf-8 -*-

__author__ = 'Jerry Lee'


from redis_op import RedisOP
from app.models import Instrument
from sklearn import svm,preprocessing
from sklearn.externals import joblib
import pandas as pd
import os
import tushare as ts
from sklearn.cluster import AffinityPropagation
from datetime import date
from sklearn.decomposition import PCA

class Analyzer(object):
    """
    股票分析结果类，所有的关于股票的信息都从这个类获取
    """
    def __init__(self, app, db):
        self.app = app

        self.db = db

        self.securities = []

        self.instruments = []

        self.__get_instruments()

        self.stock_basic = None

        self.stock_basic_update_date = None

    # 获取所有的股票信息
    def __get_instruments(self):
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
                item['industry'] = security.industry
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

    # 行业聚类分析
    def industry_cluster(self, industry):
        curr_date = date.today().strftime("%Y-%m-%d")

        if (self.stock_basic_update_date is None) or (curr_date != self.stock_basic_update_date):
            self.stock_basic = ts.get_stock_basics()
            self.stock_basic_update_date = curr_date

        instruments = self.stock_basic[self.stock_basic['industry'] == industry]

        if len(instruments) <= 0:
            return None

        data = instruments.drop(['name', 'industry', 'area', 'timeToMarket', 'pe', 'pb'], axis=1)
        data = data.fillna(0.00)
        data = data.astype('float64')

        #x = preprocessing.scale(data)
        x = data.values

        #pca = PCA(n_components=8, copy=False)
        #x = pca.fit_transform(x)

        #print x

        af = AffinityPropagation(affinity='euclidean').fit(x)
        labels = af.labels_

        instruments['label'] = None

        label_index = list(instruments.columns).index('label')

        i = 0
        for label in labels:
            instruments.iloc[i, label_index] = label
            i += 1

        return instruments

    # 读取历史数据并返回每日涨跌幅
    def __read_data(self, folder, begin_date, code):
        file_path = folder + '/' + code + '.csv'
        today = date.today()

        end_date = today.strftime("%Y-%m-%d")

        df = pd.read_csv(file_path)
        df.set_index('date', inplace=True)

        df = df.loc[begin_date:end_date, ]
        df.fillna(method='ffill', inplace=True)  # 前向填充

        value = pd.Series(df['close'] - df['close'].shift(1), index=df.index)
        value = value.ffill()

        df['value'] = value
        df['rate'] = value/df['close']*100

        return df['rate']

    # 行业对涨跌幅进行聚类分析
    def industry_cluster_by_tech(self, industry, begin_date):
        curr_date = date.today().strftime("%Y-%m-%d")

        if (self.stock_basic_update_date is None) or (curr_date != self.stock_basic_update_date):
            self.stock_basic = ts.get_stock_basics()
            self.stock_basic_update_date = curr_date

        instruments = self.stock_basic[self.stock_basic['industry'] == industry]

        if len(instruments) <= 0:
            return None

        df = pd.DataFrame()

        index_code = '000001'
        index_data = self.__read_data(self.app.config['INDEX_FILE_PATH'], begin_date, index_code)
        index_code = '9' + index_code
        df[index_code] = index_data

        for code in instruments.index:
            data = self.__read_data(self.app.config['DAY_FILE_PATH'], begin_date, code)
            df[code] = data

        df.fillna(method='ffill', inplace=True)
        df.fillna(0.01, inplace=True)
        df = df.astype('float64')

        df.drop([index_code], axis=1, inplace=True)

        df = df.T

        x = df.values

        af = AffinityPropagation(affinity='euclidean').fit(x)
        labels = af.labels_

        instruments['label'] = None

        label_index = list(instruments.columns).index('label')

        i = 0
        for label in labels:
            instruments.iloc[i, label_index] = label
            i += 1

        return instruments