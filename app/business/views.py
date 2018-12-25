# -*- coding: utf-8 -*-


from flask import jsonify, request, render_template, Blueprint
import csv
import json
from app.models import StockLabels
from app import db
from flask_login import login_required
from flask import current_app

import sys  # reload()之前必须要引入模块

reload(sys)
sys.setdefaultencoding('utf-8')

business_blueprint = Blueprint('business', __name__)


class LabelResult:
    code = ''
    labels = ''

    def __init__(self, code, labels):
        self.code = code
        self.labels = labels


# 处理精选排行
def handle_business(labels):
    pic_path = current_app.config['RESULT_PATH'] + '/stock_business.csv'

    # 读取csv至字典
    csvFile = open(pic_path, "r")

    stockdata = csv.DictReader(csvFile)

    labelset = labels.split()

    resultList = []

    # 不需要过滤
    if len(labelset) <= 0:
        for item in stockdata:
            stockLabels = db.session.query(StockLabels).filter_by(code=item['code']).first()

            if stockLabels is not None:
                item['labels'] = stockLabels.labels

            resultList.append(item)

    else:
        for item in stockdata:
            stockLabels = db.session.query(StockLabels).filter_by(code=item['code']).first()

            if stockLabels is None:
                continue

            item['labels'] = stockLabels.labels

            combineset = list(set(stockLabels.labels.split()).intersection(set(labelset)))
            if combineset is not None and len(combineset) > 0:
                resultList.append(item)

    template_filename = "business.html"

    return render_template(template_filename, title='精选股票', stockdata=resultList)


# 获取精选排行数据
def create_business_data(labels):
    pic_path = current_app.config['RESULT_PATH'] + '/stock_business.csv'

    # 读取csv至字典
    csvFile = open(pic_path, "r")

    stockdata = csv.DictReader(csvFile)

    labelset = labels.split()

    resultList = []

    index = 1

    # 不需要过滤
    if len(labelset) <= 0:
        for item in stockdata:
            stockLabels = db.session.query(StockLabels).filter_by(code=item['code']).first()

            if stockLabels is not None:
                item['labels'] = stockLabels.labels

            item['id'] = index

            index += 1

            resultList.append(item)

    else:
        for item in stockdata:
            stockLabels = db.session.query(StockLabels).filter_by(code=item['code']).first()

            if stockLabels is None:
                continue

            item['labels'] = stockLabels.labels

            combineset = list(set(stockLabels.labels.split()).intersection(set(labelset)))
            if combineset is not None and len(combineset) > 0:
                item['id'] = index
                index += 1
                resultList.append(item)

    return resultList


# 处理精选排行的ajax数据请求
@business_blueprint.route('/data', methods=['POST', 'GET'])
@login_required
def get_business_data():
    print("get business data")

    info = request.values
    limit = info.get('limit', 10)  # 每页显示的条数
    offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
    labels = info.get('labels', '')

    data = create_business_data(labels)
    # return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
    return jsonify({'total': len(data), 'rows': data})


