# coding=utf8

__author__ = 'Administrator'

"""
对股票进行分类
"""

import pandas as pd
from datetime import timedelta, datetime, date
from config import config
from bin.quotation import get_history_data
import tushare as ts
import numpy as np
from sklearn import cluster, covariance, manifold
import os
from sqlalchemy import create_engine
from models import StockCluster, StockClusterItem, Session
from sklearn.cluster import KMeans, AffinityPropagation

# 设置精度
pd.set_option('precision', 2)

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class ClusterItem(object):
    '''
    聚类中的股票以及相关系数
    '''
    def __init__(self, code, name, corr):
        self.code = code
        self.name = name
        self.corr = corr

    def __str__(self):
        return "[{}:{}:{}:{}]".format(self.__class__.__name__, self.code, self.name, self.corr)


class Cluster(object):
    '''
    一个分类，包含多个股票
    '''
    def __init__(self, code, name, label):
        self.name = name  # 簇心的名称
        self.code = code  # 簇心的代码
        self.max_corr = 0.5  # 簇的最大相关系数
        self.stocks = {}  # 簇包含的股票列表
        self.label = label

    def add(self, item):
        self.stocks[item.code] = item

    def exists(self, code):
        if self.stocks.has_key(code):
            return self.stocks[code]
        else:
            return None

    def remove(self, item):
        del self.stocks[item.code]

    def empty(self):
        return len(self.stocks) <= 0

    def __str__(self):
        return "[{}:{}:{}:{}]".format(self.__class__.__name__, self.code, self.name, len(self.stocks))


class Clusters(object):
    def __init__(self):
        self.items = []

    def add(self, cluster):
        self.items.append(cluster)

    def exists(self, code):
        for item in self.items:
            if item.exists(code):
                return True

        return False

    def existed_cluster(self, label):
        for item in self.items:
            if item.label == label:
                return item

        return None


def read_data(code, day_file_path):
    today = date.today()

    #start_date = (today - timedelta(days=20)).strftime("%Y-%m-%d")
    start_date = '2018-01-01'
    end_date = today.strftime("%Y-%m-%d")

    file_path = day_file_path + '/' + code + '.csv'
    df = pd.read_csv(file_path)
    df.set_index('date', inplace=True)
    df = df.loc[start_date:end_date, ]
    df.fillna(method='ffill', inplace=True)  # 前向填充
    #df.fillna(method='bfill', inplace=True)  # 后向填充
    #df.fillna(1.0, inplace=True)

    value = pd.Series(df['close'] - df['close'].shift(1), index=df.index)
    value = value.ffill()

    df['value'] = value
    df['rate'] = value/df['close']*100

    #df['rate'] = (df['close'] - df['close'][0])*100/df['close']
    #df['rate'] = (df['close'] - df['open']) * 100 / df['close']

    return df['rate']


# 对聚集进行裁剪
def cluster_cut(clusters, code, corr):
    for cluster in clusters.items:
        stock = cluster.exists(code)

        # 如果在前面的聚集中存在
        if stock is not None:
            # 如果相关系数比原簇中已经存在的相关系数大，则把原簇中的删掉，并返回False，这样可以提示新簇进行添加
            if stock.corr < corr:
                cluster.remove(stock)

                return False
            else:
                return True

    return False


# 分类计算
def compute_cluster(instruments, result_file_path, day_file_path, filename):
    data = pd.DataFrame()
    for code in instruments.index:
        s = read_data(code, day_file_path)
        data[code] = s

    data_corr = data.corr()

    clusters = Clusters()

    for code in instruments.index:
        # 如果在前面的聚集中已经包含了当前的股票，则忽略当前的股票
        if clusters.exists(code):
            continue

        # 取出一个聚集中的所有股票
        cols = data_corr[code]

        stock_list = cols[(cols > 0.5) & (cols < 1.0)]

        # 生成一个聚集
        cluster = Cluster(code, instruments.loc[str(code), 'name'].encode('utf-8'))

        for index, value in stock_list.iteritems():
            # 如果股票在前面的聚集中已经存在并且corr值更小，则将该股票从前面的聚集中删除，添加到新的聚集
            if not cluster_cut(clusters, index, value):
                cluster_item = ClusterItem(index, instruments.loc[str(index), 'name'].encode('utf-8'), value)
                cluster.add(cluster_item)
                if cluster.max_corr < value:
                    cluster.max_corr = value

        # 增加一个聚集
        clusters.add(cluster)

    return clusters


def cluster_by_kmeans(instruments, result_file_path, day_file_path, filename):
    data = pd.DataFrame()
    for code in instruments.index:
        s = read_data(code, day_file_path)
        data[code] = s

    data = data.fillna(method='ffill')
    data = data.fillna(0.01)
    data = data.astype('float64')

    data = data.T

    print data

    x = data.values

    kmeans = KMeans(n_clusters=10)  # n_clusters:number of cluster
    kmeans.fit(x)
    print kmeans.labels_

    clusters = Clusters()

    i = 0
    for label in kmeans.labels_:
        cluster = clusters.existed_cluster(label)

        if cluster is None:
            cluster = Cluster(instruments.index[i], instruments['name'][i], label)
            clusters.add(cluster)
        else:
            cluster_item = ClusterItem(instruments.index[i], instruments['name'][i], 1.0)
            cluster.add(cluster_item)

        i += 1

    return clusters


def cluster_by_ap(instruments, index_file_path, day_file_path, filename):
    data = pd.DataFrame()
    for code in instruments.index:
        s = read_data(code, day_file_path)
        data[code] = s

    #data_corr = data.corr()

    #data_corr = data_corr.fillna(0.01)

    #x = data_corr.values

    data = data.fillna(method='ffill')
    data = data.fillna(0.01)
    data = data.astype('float64')

    data = data.T

    print data

    x = data.values

    #print np.isnan(x).any()

    #print x

    #af = AffinityPropagation(affinity='precomputed').fit(x)
    af = AffinityPropagation(affinity='euclidean').fit(x)
    #cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_

    clusters = Clusters()

    i = 0
    for label in af.labels_:
        cluster = clusters.existed_cluster(label)

        if cluster is None:
            cluster = Cluster(instruments.index[i], instruments['name'][i], label)
            clusters.add(cluster)
        else:
            cluster_item = ClusterItem(instruments.index[i], instruments['name'][i], 1.0)
            cluster.add(cluster_item)

        i += 1

    return clusters


def cluster_by_ap_new(instruments, index_file_path, index_code, day_file_path):
    data = pd.DataFrame()

    index_data = read_data(index_code, index_file_path)
    index_code = '9' + index_code
    data[index_code] = index_data

    for code in instruments.index:
        s = read_data(code, day_file_path)
        data[code] = s
        data[code] - data[index_code]

    #data_corr = data.corr()

    #data_corr = data_corr.fillna(0.01)

    #x = data_corr.values

    data = data.fillna(method='ffill')
    data = data.fillna(0.01)
    data = data.astype('float64')

    data.drop([index_code], axis=1, inplace=True)

    data = data.T

    x = data.values

    #print np.isnan(x).any()

    #print x

    #af = AffinityPropagation(affinity='precomputed').fit(x)
    af = AffinityPropagation(affinity='euclidean').fit(x)
    #cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_

    clusters = Clusters()

    i = 0
    for label in af.labels_:
        cluster = clusters.existed_cluster(label)

        if cluster is None:
            cluster = Cluster(instruments.index[i], instruments['name'][i], label)
            clusters.add(cluster)
        else:
            cluster_item = ClusterItem(instruments.index[i], instruments['name'][i], 1.0)
            cluster.add(cluster_item)

        i += 1

    return clusters


# 写入数据库
def write_to_db(clusters, section):
    session = Session()

    session.query(StockCluster).filter(StockCluster.section==section).delete()

    session.query(StockClusterItem).filter(StockClusterItem.section==section).delete()

    for cluster in clusters.items:
        for code in cluster.stocks:
            stock_cluster_item = StockClusterItem(section=section, parent_code=cluster.code, code=code,
                                                  name=cluster.stocks[code].name, corr=cluster.stocks[code].corr)

            session.add(stock_cluster_item)

        stock_cluster = StockCluster(section=section, code=cluster.code, name=cluster.name)

        session.add(stock_cluster)

    session.commit()

    session.close()


def sz50_cluster():
    instruments = ts.get_sz50s()

    instruments.set_index('code', inplace=True)

    #clusters = compute_cluster(instruments, config.RESULT_PATH, config.DAY_FILE_PATH, 'sz50')
    #clusters = cluster_by_ap(instruments, config.RESULT_PATH, config.DAY_FILE_PATH, 'sz50')
    clusters = cluster_by_ap_new(instruments, config.INDEX_FILE_PATH, '000016', config.DAY_FILE_PATH)

    write_to_db(clusters=clusters, section='sz50')


def hs300_cluster():
    instruments = ts.get_hs300s()

    instruments.set_index('code', inplace=True)

    #clusters = compute_cluster(instruments, config.RESULT_PATH, config.DAY_FILE_PATH, 'hs300')
    clusters = cluster_by_ap_new(instruments, config.INDEX_FILE_PATH, '000300', config.DAY_FILE_PATH)

    write_to_db(clusters=clusters, section='hs300')


def zz500_cluster():
    instruments = ts.get_zz500s()

    instruments.set_index('code', inplace=True)

    #clusters = compute_cluster(instruments, config.RESULT_PATH, config.DAY_FILE_PATH, 'zz500')
    clusters = cluster_by_ap(instruments, config.RESULT_PATH, config.DAY_FILE_PATH, 'zz500')

    write_to_db(clusters=clusters, section='zz500')


# 所有股票聚类
def instruments_cluster(industry):
    instruments = ts.get_stock_basics()

    if industry != 'all':
        instruments = instruments[instruments['industry'] == industry]	

    data = instruments.drop(['name', 'industry', 'area', 'timeToMarket'], axis=1)
    #data = data.fillna(method='ffill')
    data = data.fillna(0.00)
    data = data.astype('float64')

    #data_corr = data.T.corr()

    #print(data_corr)

    #data_corr = data_corr.fillna(0.001)

    #x = data_corr.values

    x = data.values

    af = AffinityPropagation(affinity='euclidean').fit(x)
    #kmeans = KMeans(n_clusters=60)  # n_clusters:number of cluster
    #kmeans.fit(x)
    #cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_
    #labels = kmeans.labels_

    clusters = Clusters()

    i = 0
    for label in labels:
        cluster = clusters.existed_cluster(label)

        if cluster is None:
            cluster = Cluster(instruments.index[i], instruments['name'][i], label)
            clusters.add(cluster)
        else:
            cluster_item = ClusterItem(instruments.index[i], instruments['name'][i], 1.0)
            cluster.add(cluster_item)

        i += 1

    write_to_db(clusters=clusters, section=industry)


if __name__ == '__main__':
    #instruments_cluster()
    sz50_cluster()
    hs300_cluster()
    zz500_cluster()

