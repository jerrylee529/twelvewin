# -*- coding: utf-8 -*-


#################
#### imports ####
#################

from flask import render_template, jsonify, Blueprint, request
from flask_login import current_user, login_required
from app.models import SelfSelectedStock, Instrument, Report
from app import db
from app.decorators import check_confirmed
import json
from app import analyzer, log

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


# 增加行业聚类分析
@industry_analysis_blueprint.route('/industry/data', methods=['GET'])
def list_stock():
    industry = request.values.get('industry', '')
    cluster_type = int(request.values.get('cluster_type', 0))

    log.info("industry: {}, cluster type: {}, {}".format(industry, cluster_type, type(cluster_type)))

    if industry is None or industry == '':
        return jsonify({"total": 0, "rows": []})

    if cluster_type == 0:
        instruments = analyzer.industry_cluster_basic(industry)
    else:
        instruments = analyzer.industry_cluster_by_tech(industry, '2018-01-01')

    if instruments is None or len(instruments) <= 0:
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
        #item['label'] = clusters.loc[index, 'label'] + 1
        item['label'] = instrument['label'] + 1
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
@login_required
@check_confirmed
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


@industry_analysis_blueprint.route('/industry/stock/<code>', methods=['GET'])
def get_industry_stock(code):
    industry = request.values.get('industry', '')
    cluster_type = int(request.values.get('cluster_type', 0))

    log.info("code: {}, industry: {}, cluster type: {}, {}".format(code, industry, cluster_type, type(cluster_type)))

    if industry is None or industry == '':
        return jsonify({"total": 0, "rows": []})

    if cluster_type == 0:
        instruments = analyzer.industry_cluster_basic(industry)
    else:
        instruments = analyzer.industry_cluster_by_tech(industry, '2018-01-01')

    if instruments is None or len(instruments) <= 0:
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

    label = instruments['label'][code]

    num = 0

    for index, instrument in instruments.iterrows():
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

        num += 1

        if instrument['label'] != label:
            continue

        item = {}
        item['id'] = id
        #item['label'] = clusters.loc[index, 'label'] + 1
        item['label'] = instrument['label'] + 1
        item['industry'] = instrument['industry']
        item['code'] = index
        item['name'] = instrument['name']
        item['pe'] = instrument['pe']
        #item['outstanding'] = instrument['outstanding']
        #item['totals'] = instrument['totals']
        #item['total_assets'] = instrument['totalAssets']
        #item['liquid_assets'] = instrument['liquidAssets']
        #item['fixed_assets'] = instrument['fixedAssets']
        #item['esp'] = round(instrument['esp'], 2)
        #item['bvps'] = instrument['bvps']
        item['pb'] = instrument['pb']
        #item['time_2_market'] = instrument['timeToMarket']
        item['gpr'] = instrument['gpr']
        item['npr'] = instrument['npr']
        #item['holders'] = instrument['holders']
        rows.append(item)
        id += 1

    rows = sorted(rows, key=lambda e: e.__getitem__('label'))

    result_data = {}
    result_data['total'] = len(rows)
    result_data['rows'] = rows

    if num > 0:
        result_data['avg_pe'] = round(total_pe/num, 2)
        result_data['avg_pb'] = round(total_pb/num, 2)
        result_data['avg_esp'] = round(total_esp/num, 2)
        result_data['avg_bvps'] = round(total_bvps/num, 2)
        result_data['avg_gpr'] = round(total_gpr/num, 2)
        result_data['avg_npr'] = round(total_npr/num, 2)
        result_data['mid_pe'] = round(get_median(pe_list), 2)
        result_data['mid_pb'] = round(get_median(pb_list), 2)
        result_data['mid_esp'] = round(get_median(esp_list), 2)
        result_data['mid_bvps'] = round(get_median(bvps_list), 2)
        result_data['mid_gpr'] = round(get_median(gpr_list), 2)
        result_data['mid_npr'] = round(get_median(npr_list), 2)

    return jsonify(result_data)
