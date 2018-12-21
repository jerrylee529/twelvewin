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
import cluster_data_service as cds

if __name__ == '__main__':
    cds.instruments_cluster('银行')
    

