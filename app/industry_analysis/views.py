# -*- coding: utf-8 -*-


#################
#### imports ####
#################

from flask import render_template, jsonify, Blueprint, request
from flask_login import current_user, login_required
from app.models import SelfSelectedStock, Instrument, Report
from app import db
from sklearn.cluster import KMeans, AffinityPropagation
import tushare as ts
from app.decorators import check_confirmed
import time
import json
import os
from sklearn import svm, preprocessing, metrics

################
#### config ####
################

import sys   #reload()之前必须要引入模块
reload(sys)
sys.setdefaultencoding('utf-8')

industry_analysis_blueprint = Blueprint('industry_analysis', __name__,)

################
#### routes ####
################


def sort_key(item):
    return item['id']

# 计算中位数
def get_median(data):
    data.sort()
    half = len(data) // 2
    return (data[half] + data[~half]) / 2

# 获取自选股数据
#@industry_analysis_blueprint.route('/industry/data')
def list_stock_ex():
    industry = request.values.get('labels', '')

    if industry is None or industry == '':
        industry = '银行'

    id = 1

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
    total_pe = 0
    total_pb = 0
    total_esp = 0
    total_bvps = 0
    total_gpr = 0
    total_npr = 0
    pe_list = []
    pb_list = []
    esp_list = []
    bvps_list = []
    gpr_list = []
    npr_list = []
    for instrument in db.session.query(Instrument).filter_by(industry=industry).all():
        item = {}
        item['id'] = id
        item['industry'] = instrument.industry
        item['code'] = instrument.code
        item['name'] = instrument.name
        item['pe'] = instrument.pe
        item['outstanding'] = instrument.outstanding
        item['totals'] = instrument.totals
        item['totalAssets'] = instrument.total_assets
        item['liquidAssets'] = instrument.liquid_assets
        item['fixedAssets'] = instrument.fixed_assets
        item['esp'] = instrument.esp
        item['bvps'] = instrument.bvps
        item['pb'] = instrument.pb
        item['time_2_market'] = instrument.time_2_market
        item['gpr'] = instrument.gpr
        item['npr'] = instrument.npr
        item['holders'] = instrument.holders
        rows.append(item)
        id += 1
        total_pe += instrument.pe
        total_pb += instrument.pb
        total_esp += instrument.esp
        total_bvps += instrument.bvps
        total_gpr += instrument.gpr
        total_npr += instrument.npr
        pe_list.append(instrument.pe)
        pb_list.append(instrument.pb)
        esp_list.append(instrument.esp)
        bvps_list.append(instrument.bvps)
        gpr_list.append(instrument.gpr)
        npr_list.append(instrument.npr)

    result_data = {}
    rows_len = len(rows)
    result_data['total'] = rows_len
    result_data['rows'] = rows

    if rows_len > 0:
        result_data['avg_pe'] = round(total_pe/rows_len, 2)
        result_data['avg_pb'] = round(total_pb/rows_len, 2)
        result_data['avg_esp'] = round(total_esp/rows_len, 2)
        result_data['avg_bvps'] = round(total_bvps/rows_len, 2)
        result_data['avg_gpr'] = round(total_gpr/rows_len, 2)
        result_data['avg_npr'] = round(total_npr/rows_len, 2)
        result_data['mid_pe'] = get_median(pe_list)
        result_data['mid_pb'] = get_median(pb_list)
        result_data['mid_esp'] = get_median(esp_list)
        result_data['mid_bvps'] = get_median(bvps_list)
        result_data['mid_gpr'] = get_median(gpr_list)
        result_data['mid_npr'] = get_median(npr_list)

    return jsonify(result_data)


def industry_cluster(source):
    if len(source) <= 0:
        print source
        return None

    data = source.drop(['name', 'industry', 'area', 'timeToMarket', 'pe', 'pb'], axis=1)
    data = data.fillna(0.00)
    data = data.astype('float64')

    #x = preprocessing.scale(data)
    x = data.values

    af = AffinityPropagation(affinity='euclidean').fit(x)
    labels = af.labels_

    data['label'] = None

    label_index = list(data.columns).index('label')

    i = 0
    for label in labels:
        data.iloc[i, label_index] = label
        i += 1

    return data


# 增加行业聚类分析
@industry_analysis_blueprint.route('/industry/data')
def list_stock():
    industry = request.values.get('industry', '')


    if industry is None or industry == '':
        return jsonify({"total": 0, "rows": []})

    instruments = ts.get_stock_basics()

    instruments = instruments[instruments['industry'] == industry]

    clusters = industry_cluster(instruments)

    if clusters is None:
        return jsonify({"total": 0, "rows": []})

    id = 1
    rows = []
    total_pe = 0
    total_pb = 0
    total_esp = 0
    total_bvps = 0
    total_gpr = 0
    total_npr = 0
    pe_list = []
    pb_list = []
    esp_list = []
    bvps_list = []
    gpr_list = []
    npr_list = []
    for index, instrument in instruments.iterrows():
        item = {}
        item['id'] = id
        item['label'] = clusters.loc[index, 'label'] + 1
        item['industry'] = instrument['industry']
        item['code'] = index
        item['name'] = instrument['name']
        item['pe'] = instrument['pe']
        item['outstanding'] = instrument['outstanding']
        item['totals'] = instrument['totals']
        item['total_assets'] = instrument['totalAssets']
        item['liquid_assets'] = instrument['liquidAssets']
        item['fixed_assets'] = instrument['fixedAssets']
        item['esp'] = round(instrument['esp'], 2)
        item['bvps'] = instrument['bvps']
        item['pb'] = instrument['pb']
        item['time_2_market'] = instrument['timeToMarket']
        item['gpr'] = instrument['gpr']
        item['npr'] = instrument['npr']
        item['holders'] = instrument['holders']
        rows.append(item)
        id += 1
        total_pe += instrument.pe
        total_pb += instrument.pb
        total_esp += instrument.esp
        total_bvps += instrument.bvps
        total_gpr += instrument.gpr
        total_npr += instrument.npr
        pe_list.append(instrument.pe)
        pb_list.append(instrument.pb)
        esp_list.append(instrument.esp)
        bvps_list.append(instrument.bvps)
        gpr_list.append(instrument.gpr)
        npr_list.append(instrument.npr)

    rows = sorted(rows, key=lambda e: e.__getitem__('label'))

    result_data = {}
    rows_len = len(rows)
    result_data['total'] = rows_len
    result_data['rows'] = rows

    if rows_len > 0:
        result_data['avg_pe'] = round(total_pe/rows_len, 2)
        result_data['avg_pb'] = round(total_pb/rows_len, 2)
        result_data['avg_esp'] = round(total_esp/rows_len, 2)
        result_data['avg_bvps'] = round(total_bvps/rows_len, 2)
        result_data['avg_gpr'] = round(total_gpr/rows_len, 2)
        result_data['avg_npr'] = round(total_npr/rows_len, 2)
        result_data['mid_pe'] = round(get_median(pe_list), 2)
        result_data['mid_pb'] = round(get_median(pb_list), 2)
        result_data['mid_esp'] = round(get_median(esp_list), 2)
        result_data['mid_bvps'] = round(get_median(bvps_list), 2)
        result_data['mid_gpr'] = round(get_median(gpr_list), 2)
        result_data['mid_npr'] = round(get_median(npr_list), 2)

    return jsonify(result_data)


@industry_analysis_blueprint.route('/industry')
def index():
    template_filename = 'industry_analysis/industry.html'

    return render_template(template_filename, title='行业分析')


# 获取行业列表
@industry_analysis_blueprint.route('/industry/industries', methods=['GET', 'POST'])
def get_industries():
    industries = db.session.query(Instrument.industry).group_by(Instrument.industry).all()

    items = []
    
    id = 1
    for industry in industries:
        if (industry[0] is None) or (industry[0] == ''):
            continue
        item = {}
        item['id'] = id
        item['name'] = industry[0]
        items.append(item)
        id += 1

    return jsonify({'industries': items})


# 处理标签编辑的ajax请求
@industry_analysis_blueprint.route('/industry/update_labels', methods=['GET', 'POST'])
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


