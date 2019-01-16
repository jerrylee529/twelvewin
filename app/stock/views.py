# -*- coding: utf-8 -*-


from flask import request, jsonify, Blueprint, render_template, current_app
from flask_login import login_required, current_user
import csv
import os
import time
import json
from app import db
from app.models import SelfSelectedStock
from app.decorators import check_confirmed
from app import analyzer
from app.util import model_to_json

import sys   #reload()之前必须要引入模块
reload(sys)
sys.setdefaultencoding('utf-8')

stock_blueprint = Blueprint('stock', __name__,)


# 处理市盈率排行的ajax数据请求
@stock_blueprint.route('/<path>/data', methods=['POST', 'GET'])
@login_required
def get_stock_data(path):
    print("get_stock_data")

    info = request.values
    limit = info.get('limit', 10)  # 每页显示的条数
    offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点

    data = []

    if (path == 'pe'):
        csv_filename = "stock_pe.csv"
        title = "市盈率排名"
    elif (path == 'pb'):
        csv_filename = "stock_pb.csv"
        title = "市净率排名"
    elif (path == 'roe'):
        csv_filename = "stock_roe.csv"
        title = "净资产收益率排名"
    elif (path == 'divi'):
        csv_filename = "stock_dividence.csv"
        title = "股息率排名"
    else:
        return jsonify({'total': len(data), 'rows': data})

    pic_path = current_app.config['RESULT_PATH'] + '/' + csv_filename

    filemt = time.localtime(os.stat(pic_path).st_mtime)
    #print time.strftime("%Y-%m-%d", filemt)

    # 读取csv至字典
    csvFile = open(pic_path, "r")

    index = 1
    for row in csv.DictReader(csvFile):
        row['id'] = index
        row['updateTime'] = time.strftime("%Y-%m-%d", filemt)
        index += 1
        data.append(row)

        if current_user.is_anonymous and index > 20:
            break

    #return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
    return jsonify({'total': len(data), 'rows': data})


# 处理首页的导航
@stock_blueprint.route('/<path>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def list_stock(path):
    template_filename = 'stock/rank.html'

    title = "团赢数据"
    if path == 'pe':
        title = "市盈率排名"
    elif path == 'pb':
        title = "市净率排名"
    elif path == 'roe':
        title = "净资产收益率排名"
    elif path == 'divi':
        title = "股息率排名"
    elif path == 'business':
        title = "精选股票"
        template_filename = "business/business.html"
    else:
        return render_template('errors/404.html')

    return render_template(template_filename, title=title, path=path)


# 处理k线图
@stock_blueprint.route('/candlestick/<code>', methods=['GET', 'POST'])
def show_stock(code):
    template_filename = 'common/candlestick.html'

    return render_template(template_filename, title=code)


# 获取历史行情数据
@stock_blueprint.route('/candlestick/<code>/hq', methods=['GET', 'POST'])
def get_history_quotation(code):
    print("get_history_quotation: " + code)
    data = []

    pic_path = current_app.config['DAY_FILE_PATH'] + '/' + code + '.csv'

    filemt = time.localtime(os.stat(pic_path).st_mtime)
    #print time.strftime("%Y-%m-%d", filemt)

    # 读取csv至字典
    csv_file = open(pic_path, "r")

    for row in csv.DictReader(csv_file):
        item = []
        item.append(row['date'])
        try:
            item.append(float(row['open']))
            item.append(float(row['close']))
            item.append(float(row['low']))
            item.append(float(row['high']))
        except ValueError:
            continue
        data.append(item)

    quot = analyzer.get_quotation(code)

    if quot:
        last_item = []
        last_item.append(quot['update_time'].split()[0])
        last_item.append(float(quot['open']))
        last_item.append(float(quot['trade']))
        last_item.append(float(quot['low']))
        last_item.append(float(quot['high']))

        data.append(last_item)

    #del data[:-100]

    return jsonify({'rows': data, 'updateTime': time.strftime("%Y-%m-%d", filemt)})


# 增加自选股
@stock_blueprint.route('/stock/add_self_selected_stock', methods=['POST'])
@login_required
def add_self_selected_stock():
    code = request.form.get('code')

    email = current_user.email

    stock = db.session.query(SelfSelectedStock).filter_by(email=email, code=code).first()

    if stock is None:
        stock = SelfSelectedStock(current_user.email, code=code, labels='')

        db.session.add(stock)
    else:
        stock.deleted = False

    db.session.commit()

    myClassJson = stock.to_json()

    return jsonify(myClassJson)

