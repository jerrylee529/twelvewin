# -*- coding: utf-8 -*-


from flask import request, jsonify, Blueprint, render_template, flash, current_app
from flask_login import current_user
import csv
import os
import time
import datetime
from flask_login import login_required
from app.decorators import check_confirmed


import sys   #reload()之前必须要引入模块
reload(sys)
sys.setdefaultencoding('utf-8')


BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

technical_analysis_blueprint = Blueprint('technical_analysis', __name__,)


# 突破历史最高价
@technical_analysis_blueprint.route('/tech/<path>/data', methods=['POST', 'GET'])
#@login_required
def get_data(path):
    print("get technical analysis data")

    info = request.values
    limit = info.get('limit',10)  # 每页显示的条数
    offset = info.get('offset',0)  # 分片数，(页码-1)*limit，它表示一段数据的起点

    data = []

    if path == 'highest':
        csv_filename = "highest_in_history.csv"
    elif path == 'lowest':
        csv_filename = "lowest_in_history.csv"
    elif path == 'ma_long':
        csv_filename = "ma_long.csv"
    elif path == 'break_ma':
        csv_filename = "break_ma.csv"
    elif path == 'above_ma':
        csv_filename = "above_ma.csv"
    else:
        return jsonify({'total': len(data), 'rows': data})

    pic_path = current_app.config['RESULT_PATH'] + '/' + csv_filename

    filemt = time.localtime(os.stat(pic_path).st_mtime)

    # 读取csv至字典
    csvFile = open(pic_path, "r")

    index = 1
    for row in csv.DictReader(csvFile):
        row['id']= index
        row['updateTime'] = time.strftime("%Y-%m-%d", filemt)
        index += 1
        data.append(row)

        if current_user.is_anonymous and index > 10:
            break

    #return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
    return jsonify({'total': len(data), 'rows': data})


# 处理首页的导航
@technical_analysis_blueprint.route('/tech/<path>', methods=['GET', 'POST'])
#@login_required
#@check_confirmed
def index(path):
    if path == 'highest':
        flash('股价创历史新高的股票列表','历史新高')
        title = "历史新高"
    elif path == 'lowest':
        flash('股价创历史新低的股票列表', '历史新低')
        title = "历史新低"
    elif path == 'ma_long':
        flash('5日、10日、20日均线呈多头排列的个股列表','均线多头')
        title = "均线多头"
    elif path == 'break_ma':
        flash('突破20日均线的个股列表','突破均线')
        title = "突破均线"
    elif path == 'above_ma':
        flash('年线以上的个股列表','年线以上')
        title = "年线以上"
    elif path == 'filter':
        title = "涨跌幅分析"
        return render_template('technical_analysis/filter.html', title=title, path=path)
    else:
        return render_template('errors/400.html')

    return render_template('technical_analysis/rank.html', title=title, path=path)


@technical_analysis_blueprint.route('/tech/filter/data', methods=['POST', 'GET'])
#@login_required
def get_filter_data():
    print("get filter analysis data")

    info = request.values

    print info

    PERIODS = {u'近一周': 7, u'近一月': 30, u'近三月': 30*3, u'近半年': 30*6, u'近一年': 30*12}

    begin_date = request.values.get('begin_date', '2018-01-01')
    end_date = request.values.get('end_date', '2018-12-01')

    days = "".join(request.values.get('days', u'近一周').split())
    if days is None or len(days) <= 0:
        days = u'近一周'

    period = PERIODS.get(days, 7)

    low = request.values.get('low', -30)
    high = request.values.get('high', 0)

    print "begin date: {}, end date: {}, days: {}, low: {}, high: {}".format(begin_date, end_date, days, low, high)

    data = []

    pic_path = current_app.config['RESULT_PATH'] + '/price_change.csv'

    filemt = time.localtime(os.stat(pic_path).st_mtime)

    # 读取csv至字典
    csvFile = open(pic_path, "r")

    index = 1
    for row in csv.DictReader(csvFile):
        rate = float(row['rate'+str(period)])
        if (rate > -9999) and (rate >= float(low)) and (rate <= float(high)):
            row['id'] = index
            row['rate'] = rate
            row['updateTime'] = time.strftime("%Y-%m-%d", filemt)
            index += 1
            data.append(row)

    return jsonify({'total': len(data), 'rows': data})
