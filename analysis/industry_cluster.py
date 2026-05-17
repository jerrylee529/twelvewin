# coding=utf8

"""行业聚类脚本入口。

该文件主要作为 cluster_data_service 的轻量入口和历史兼容包装。直接运行时会调用
instruments_cluster('银行')，基于股票基本面指标对银行行业股票进行聚类并写入数据库。
"""

__author__ = 'Administrator'

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
import cluster_data_service as cds

if __name__ == '__main__':
    cds.instruments_cluster('银行')
    
