# coding=utf8

import pandas as pd
from config import config
from sklearn import svm,preprocessing
from sklearn.externals import joblib
import pickle
import os
import sys
import tushare as ts


def predict(code, day_file_path, result_file_path):
    file_path = day_file_path + '/' + code + '.csv'
    df = pd.read_csv(file_path)
    df.set_index('date', inplace=True)
    df.drop(['code'], axis=1, inplace=True)
    
    # 将日期作为index,顺序排列
    df = df.sort_index()
    # print df.head()
    # value表示涨跌
    value = pd.Series(df['close'].shift(-1) - df['close'], index=df.index)
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
    predict_length = 1
    train_length = L-predict_length

    # 对样本特征进行归一化处理
    df_X = df.drop(['Value'], axis=1)
    df_X = preprocessing.scale(df_X)

    # 开始循环预测，每次向前预测一个值
    correct = 0

    model_filename = result_file_path + '/' + code + '.model'

    # 如果存在模型文件则加载改模型文件，不存在则创建一个
    if os.path.exists(model_filename):
        classifier = joblib.load(model_filename)
    else:
        classifier = svm.SVC(C=1.0, kernel='rbf')

    data_train = df_X[0:train_length]
    value_train = value[0:train_length]
    data_predict = df_X[train_length:]

    classifier.fit(data_train, value_train)
    value_predict = classifier.predict(data_predict)

    joblib.dump(classifier, model_filename)

    print value_predict

    return value_predict

'''
def predict(code, day_file_path, result_file_path):
    file_path = day_file_path + '/' + code + '.csv'
    df = pd.read_csv(file_path)
    df.set_index('date', inplace=True)

    # 将日期作为index,顺序排列
    df = df.sort_index()
    # print df.head()
    # value表示涨跌
    value = pd.Series(df['close'] - df['close'].shift(1), index=df.index)
    value = value.bfill()
    value[value >= 0] = 1
    value[value < 0] = 0
    df['Value'] = value
    # 后向填充空缺值
    df = df.fillna(method='bfill')
    df = df.astype('float64')
    # print df.head()

    # 选取数据的80%作为训练集，20%作为测试集
    L = len(df)
    train = int(L * 0.8)
    total_predict_data = L - train

    # 对样本特征进行归一化处理
    df_X = df.drop(['Value'], axis=1)
    df_X = preprocessing.scale(df_X)

    # 开始循环预测，每次向前预测一个值
    correct = 0
    train_original = train

    classifier = None

    model_filename = result_file_path + '/' + code + '.model'

    # 如果存在模型文件则加载改模型文件，不存在则创建一个
    if os.path.exists(model_filename):
        classifier = joblib.load(model_filename)
    else:
        classifier = svm.SVC(C=1.0, kernel='poly')

    while train < L:
        data_train = df_X[train - train_original:train]
        value_train = value[train - train_original:train]
        data_predict = df_X[train:train + 1]
        value_real = value[train:train + 1]
        # 核函数分别选取'ploy','linear','rbf'
        # classifier = svm.SVC(C=1.0, kernel='poly')
        # classifier = svm.SVC(kernel='linear')
        # classifier = svm.SVC(C=1.0,kernel='rbf')
        classifier.fit(data_train, value_train)
        value_predict = classifier.predict(data_predict)
        print("value_real=%d value_predict=%d" % (value_real[0], value_predict))

        # 计算测试集中的正确率
        if value_real[0] == int(value_predict):
            correct += 1

        train += 1

    joblib.dump(classifier, model_filename)

    # 输出准确率
    correct = correct * 100 / total_predict_data
    print("Correct=%.2f%%" % correct)
'''

# 训练模型
def train(code, day_file_path, result_file_path):
    file_path = day_file_path + '/' + code + '.csv'
    df = pd.read_csv(file_path)

    if df.empty:
        return 0.0

    df.set_index('date', inplace=True)
    df.drop(['code'], axis=1, inplace=True)

    # 将日期作为index,顺序排列
    df = df.sort_index()
    # print df.head()
    # value表示涨跌
    value = pd.Series(df['close'].shift(-1) - df['close'], index=df.index)

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
    total_length = len(df)
    train_length = int(total_length * 0.8)

    # 对样本特征进行归一化处理
    df_X = df.drop(['Value'], axis=1)
    df_X = preprocessing.scale(df_X)

    classifier = None

    model_filename = result_file_path + '/' + code + '.model'

    # 如果存在模型文件则加载改模型文件，不存在则创建一个
    if os.path.exists(model_filename):
        classifier = joblib.load(model_filename)
    else:
        classifier = svm.SVC(C=1.0, kernel='rbf')

    data_train = df_X[0:train_length]

    value_train = value[0:train_length]

    classifier.fit(data_train, value_train)

    value_predict = classifier.predict(df_X[train_length:])

    correct = 0
    for i in range(len(value_predict)):
        if value_predict[i] == df['Value'][i+train_length]:
            correct += 1

    rate = correct*100/len(value_predict)

    print "correct: %f" % (rate,)

    # 输出模型文件
    joblib.dump(classifier, model_filename)

    return rate


# 训练所有股票
def train_all(instrument_filename, day_file_path, result_file_path):
    #instruments = pd.read_csv(instrument_filename, index_col=False, dtype={'code': object})
    instruments = ts.get_stock_basics()


    if instruments is None:
        print("Could not find any instruments, exit")
        return

    instruments.reset_index(inplace=True)

    results = []
    fileObject = open(result_file_path + '/sampleList.txt', 'w')
    for code in instruments['code']:
        try:
            rate = train(code, day_file_path=day_file_path, result_file_path=result_file_path)
            result = {}
            result['code'] = code
            result['rate'] = rate
            results.append(result)
            str_row = "%(code)s,%(rate)f" % result
            print str_row
            fileObject.write(str_row)
            fileObject.write('\n')
        except:
            print("%s compute failure" % code)
            continue

    fileObject.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: script [code] [t|p]"
        print "   t: train"
        print "   p: prediction"
        sys.exit(2)

    # train or predict
    flag = sys.argv[2]

    #代码
    code = sys.argv[1]

    if flag == 't':
        train(code, config.DAY_FILE_PATH, config.RESULT_PATH)
    elif flag == 'p':
        predict(code, config.DAY_FILE_PATH, config.RESULT_PATH)
    else:
        train_all(config.INSTRUMENT_FILENAME, config.DAY_FILE_PATH, config.RESULT_PATH)
