# -*- coding: utf-8 -*-


from flask import request, jsonify, Blueprint, render_template
from flask_login import login_required, current_user
import csv
import os
import time
import json
from app import db
from app.models import StockCluster, StockClusterItem
from app.decorators import check_confirmed
from app.util import model_to_json


import sys   #reload()之前必须要引入模块
reload(sys)
sys.setdefaultencoding('utf-8')

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from analysis.cluster_data_service import instruments_cluster

cluster_analysis_blueprint = Blueprint('cluster', __name__,)


# 处理行业分类的ajax数据请求
@cluster_analysis_blueprint.route('/cluster/<path>/data', methods=['POST', 'GET'])
@login_required
def get_data(path):
    print("get_cluster_data")

    industry = request.values.get('industry', path)

    if industry =='all':
        return jsonify({'total': 0, 'rows': []})

    if path != 'sz50' and path != 'zz500' and path != 'hs300': 
        print("compute industry cluster")
        instruments_cluster(industry)

    clusters = db.session.query(StockCluster).filter_by(section=industry).all()

    cluster_items = db.session.query(StockClusterItem).filter_by(section=industry).all()

    data = []

    index = 1
    for cluster in clusters:
        rsp_cluster = {}
        rsp_cluster['id'] = index
        rsp_cluster['code'] = cluster.code
        rsp_cluster['name'] = cluster.name
        rsp_cluster['items'] = []

        items = []

        rsp_cluster_item = {}
        rsp_cluster_item['code'] = cluster.code
        rsp_cluster_item['name'] = cluster.name
        rsp_cluster_item['corr'] = 1.0

        items.append(rsp_cluster_item)

        for cluster_item in cluster_items:
            if cluster.code == cluster_item.parent_code:
                rsp_cluster_item = {}
                rsp_cluster_item['code'] = cluster_item.code
                rsp_cluster_item['name'] = cluster_item.name
                rsp_cluster_item['corr'] = cluster_item.corr
                items.append(rsp_cluster_item)

        rsp_cluster['items'] = items

        data.append(rsp_cluster)

        index += 1

    return jsonify({'total': len(data), 'rows': data})


# 处理首页的导航
@cluster_analysis_blueprint.route('/cluster/<path>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def index(path):
    template_filename = 'cluster_analysis/cluster.html'

    title = ''
    if path == 'sz50':
        title = '上证50'
    elif path == 'hs300':
        title = '沪深300'
    elif path == 'zz500':
        title = '中证500'
    else:
        template_filename = 'cluster_analysis/industry_cluster.html'
        title = '全部股票'

    return render_template(template_filename, title=title, path=path)

