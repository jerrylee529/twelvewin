# coding=utf8

"""
批处理脚本共享的本地路径配置。

集中定义历史行情、分钟数据、配置文件、分析结果、日线数据和股票代码表路径。
bin 目录下多数旧脚本直接引用这些常量读写本机或服务器上的 CSV/TXT 数据文件。
"""

__author__ = 'Administrator'

dataPath = '/home/ubuntu/stock/dataset'
minPath = '/home/ubuntu/stock/min'
configPath = '/home/ubuntu/stock'
resultPath = '/home/ubuntu/stock/product'

data_dayPath = '/home/ubuntu/stock/day'


# 获取股票代码
instrument_file_path = configPath + '/instruments.txt'

code_list_file = configPath + '/instruments.csv'
