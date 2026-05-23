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
from app import log
from app.services.industry_cluster_service import (
    get_industry_cluster_payload,
    get_industry_stock_payload,
)

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

    if cluster_type != 0:
        log.info('cluster_type=%s uses precomputed fundamentals clusters only', cluster_type)

    return jsonify(get_industry_cluster_payload(industry))


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

    if cluster_type != 0:
        log.info('cluster_type=%s uses precomputed fundamentals clusters only', cluster_type)

    return jsonify(get_industry_stock_payload(industry, code))
