# coding=utf8

__author__ = 'Administrator'


import os
import pandas as pd

def getFiles(path):
    # 所有文件
    fileList = []

    # 返回一个列表，其中包含在目录条目的名称(google翻译)
    files = os.listdir(path)

    # 先添加目录级别
    for f in files:
        if(os.path.isfile(path + '/' + f)):
            # 添加文件
            fileList.append(f)

    return fileList

dirPath = 'c:/stock/data'

files = getFiles(dirPath)

for f in files:
    filePath = dirPath + "/" + f
    print filePath
    df = pd.DataFrame.from_csv(filePath, header=None)
    close = df.pop(4)
    df.insert(2, 4, close)
    df.to_csv(filePath, header=None)

