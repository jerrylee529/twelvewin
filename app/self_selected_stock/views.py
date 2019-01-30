# -*- coding: utf-8 -*-


#################
#### imports ####
#################

from flask import render_template, jsonify, Blueprint, request
from flask_login import current_user, login_required
from app.models import SelfSelectedStock, Instrument, Report
from app import db, analyzer
from app.decorators import check_confirmed
import time
import json
import os

################
#### config ####
################

import sys   #reload()之前必须要引入模块
reload(sys)
sys.setdefaultencoding('utf-8')

self_selected_stock_blueprint = Blueprint('self_selected_stock', __name__,)

################
#### routes ####
################


def sort_key(item):
    return item['id']


# 获取自选股数据
@self_selected_stock_blueprint.route('/selfselectedstock/data')
@login_required
def list_stock():
    result_list = {}
    email = current_user.email

    labels = request.values.get('labels', '')
    labelset = labels.split()

    id = 1
    code_list = []

    # 不需要过滤
    if len(labelset) <= 0:
        for stock in db.session.query(SelfSelectedStock).filter_by(email=email, deleted=False).all():
            item = {}
            item['id'] = id
            item['code'] = stock.code
            item['labels'] = stock.labels
            item['updateTime'] = time.strftime("%Y-%m-%d", stock.update_time.timetuple())
            result_list[stock.code] = item
            id += 1
            code_list.append(stock.code)
    else:
        for stock in db.session.query(SelfSelectedStock).filter_by(email=email, deleted=False).all():
            combineset = list(set(stock.labels.split()).intersection(set(labelset)))

            if combineset is not None and len(combineset) > 0:
                item = {}
                item['id'] = id
                item['code'] = stock.code
                item['labels'] = stock.labels
                item['updateTime'] = time.strftime("%Y-%m-%d", stock.update_time.timetuple())
                result_list[stock.code] = item
                id += 1
                code_list.append(stock.code)


    """
    industry = db.Column(db.String(32))  # 所属行业
    area = db.Column(db.String(32))  # 地区
    pe = db.Column(db.Float)  # 市盈率
    outstanding = db.Column(db.Float)  # 流通股本(亿)
    totals = db.Column(db.Float)  # 总股本(亿)
    total_assets = db.Column(db.Float)  # 总资产(万)
    liquid_assets = db.Column(db.Float)  # 流动资产
    fixed_assets = db.Column(db.Float)  # 固定资产
    reserved = db.Column(db.Float)  # 公积金
    reserved_per_share = db.Column(db.Float)  # 每股公积金
    esp = db.Column(db.Float)  # 每股收益
    bvps = db.Column(db.Float)  # 每股净资
    pb = db.Column(db.Float)  # 市净率
    time_2_market = db.Column(db.String(16))  # 上市日期
    undp = db.Column(db.Float)  # 未分利润
    perundp = db.Column(db.Float)  # 每股未分配
    rev = db.Column(db.Float)  # 收入同比(%)
    profit = db.Column(db.Float)  # 利润同比(%)
    gpr = db.Column(db.Float)  # 毛利率(%)
    npr = db.Column(db.Float)  # 净利润率(%)
    holders = db.Column(db.Integer)  # 股东人数

    """
    rows = []
    for instrument in db.session.query(Instrument).filter(Instrument.code.in_(code_list)):
        item = result_list[instrument.code]
        item['industry'] = instrument.industry
        item['name'] = instrument.name
        item['pe'] = instrument.pe
        item['outstanding'] = instrument.outstanding
        item['totals'] = instrument.totals
        item['total_assets'] = instrument.total_assets
        item['esp'] = instrument.esp
        item['bvps'] = instrument.bvps
        item['roe'] = round(instrument.esp*100/instrument.bvps, 2)
        item['pb'] = instrument.pb
        item['time_2_market'] = instrument.time_2_market
        item['gpr'] = instrument.gpr
        item['npr'] = instrument.npr
        item['holders'] = instrument.npr
        rows.append(item)

    rows.sort(key=sort_key)

    return jsonify({'total': len(result_list), 'rows': rows})


@self_selected_stock_blueprint.route('/selfselectedstock')
@login_required
@check_confirmed
def index():
    template_filename = 'self_selected_stock/self_selected_stock.html'

    return render_template(template_filename, title='自选股')


# 处理标签编辑的ajax请求
@self_selected_stock_blueprint.route('/self_selected_stock/update_labels', methods=['GET', 'POST'])
@login_required
def update_labels():
    code = request.form.get('code')
    labels = request.form.get('labels')
    email = current_user.email

    stock = db.session.query(SelfSelectedStock).filter_by(email=email, code=code).first()

    if stock is None:
        return None
    else:
        stock.labels = labels

    db.session.add(stock)

    db.session.commit()

    myClassDict = {}

    myClassDict['code'] = stock.code
    myClassDict['labels'] = stock.labels


    # 打印字典
    # print (myClassDict)
    # 字典转化为json
    myClassJson = json.dumps(myClassDict)

    return jsonify(myClassJson)


# 处理标签编辑的ajax请求
@self_selected_stock_blueprint.route('/self_selected_stock/delete', methods=['GET', 'POST'])
@login_required
def delete():
    code = request.form.get('code')
    email = current_user.email

    stock = db.session.query(SelfSelectedStock).filter_by(email=email, code=code).first()

    #db.session.delete(stock)
    stock.deleted = True

    db.session.add(stock)

    db.session.commit()

    myClassDict = {}

    myClassDict['code'] = stock.code
    # 打印字典
    # print (myClassDict)
    # 字典转化为json
    myClassJson = json.dumps(myClassDict)

    return jsonify(myClassJson)

def convert_float(value, is_amount=False):
    result = 0.0

    if value is not None:
        result = round(value/10000 if is_amount else value, 2)

    return result

# 获取净利润
@self_selected_stock_blueprint.route('/bar/<code>/<field>', methods=['GET', 'POST'])
def get_net_profit(code, field):
    data = []

    reports = analyzer.get_finance_indicators(code)

    for key in sorted(reports.keys(), reverse=False):
        row = reports[key]

        #print row

        item = []
        item.append(key)
        try:
            if field == 'npr':
                item.append(convert_float(row['net_profit_after_nrgal_atsolc'], is_amount=True))
            elif field == 'roe':
                item.append(convert_float(row['avg_roe']))
            elif field == 'profits_yoy':
                item.append(convert_float(row['np_atsopc_nrgal_yoy']))
            elif field == 'eps':
                item.append(convert_float(row['basic_eps']))
            elif field == 'eps_yoy':
                item.append(convert_float(row['gross_selling_rate']))
            elif field == 'np_per_share':
                item.append(convert_float(row['np_per_share']))
            else:
                item.append(0)
        except ValueError:
            continue
        data.append(item)

    return jsonify({'rows': data})

