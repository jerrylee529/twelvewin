# coding=utf8

__author__ = 'jerry'


import tushare as ts
#import talib as ta
import numpy as np
import pandas as pd
import os,time,sys,re,datetime
import csv
#import scipy
import smtplib
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart


# 获取股票基本信息
#code,代码
#name,名称
#industry,所属行业
#area,地区
#pe,市盈率
#outstanding,流通股本
#totals,总股本(万)
#totalAssets,总资产(万)
#liquidAssets,流动资产
#fixedAssets,固定资产
#reserved,公积金
#reservedPerShare,每股公积金
#eps,每股收益
#bvps,每股净资
#pb,市净率
#timeToMarket,上市日期
def get_stock_list():
    df = ts.get_stock_basics()
    df.sort_index(inplace=True)
    return df

