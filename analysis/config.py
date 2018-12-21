# coding=utf8

__author__ = 'Administrator'


class BasicConfig(object):
    DEBUG = True
    DATASET_PATH = '/home/dev/twelvewin_data/analysis/data/dataset'
    CONFIG_PATH = '/home/dev/twelvewin_data/analysis'
    RESULT_PATH = '/home/dev/twelvewin_data/analysis/product'
    DAY_FILE_PATH = '/home/dev/twelvewin_data/analysis/day'
    INDEX_FILE_PATH = '/home/dev/twelvewin_data/analysis/index'


    # 股票代码文件路径
    INSTRUMENT_FILENAME = CONFIG_PATH + '/instruments.csv'

    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@127.0.0.1:3306/stock_test?charset=utf8'

# 测试配置
class TestConfig(BasicConfig):
    DEBUG = True
    DATASET_PATH = '/home/dev/twelvewin_data/analysis/data/dataset'
    CONFIG_PATH = '/home/dev/twelvewin_data/analysis/data'
    RESULT_PATH = '/home/dev/twelvewin_data/analysis/data/product'
    DAY_FILE_PATH = '/home/dev/twelvewin_data/analysis/data/day'
    INDEX_FILE_PATH = '/home/dev/twelvewin_data/analysis/index'
    
    # 股票代码文件路径
    INSTRUMENT_FILENAME = CONFIG_PATH + '/instruments.csv'

    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@127.0.0.1:3306/stock_test?charset=utf'

# 开发配置
class DevelopmentConfig(BasicConfig):
    DEBUG = True
    DATASET_PATH = '/home/dev/data/dataset'
    CONFIG_PATH = '/home/dev/data'
    RESULT_PATH = '/home/dev/data/product'
    DAY_FILE_PATH = '/home/dev/data/day'
    INDEX_FILE_PATH = '/home/dev/data/index'

    INSTRUMENT_FILENAME = CONFIG_PATH + '/instruments.csv'

    # 股票代码文件路径
    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@127.0.0.1:3306/stock_test?charset=utf'


# 生产配置
class ProductionConfig(BasicConfig):
    DEBUG = False
    DATASET_PATH = '/home/dev/data/dataset'
    CONFIG_PATH = '/home/dev/data'
    RESULT_PATH = '/home/dev/data/product'
    DAY_FILE_PATH = '/home/dev/data/day'
    INDEX_FILE_PATH = '/home/dev/data/index'

    INSTRUMENT_FILENAME = CONFIG_PATH + '/instruments.csv'

    # 股票代码文件路径
    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@127.0.0.1:3306/stock_test?charset=utf'


#config = DevelopmentConfig()
config = ProductionConfig()
