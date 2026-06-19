# -*- coding: utf-8 -*-

from flask import render_template, jsonify, Blueprint, request
from app.models import Instrument, Report
from app import db
from app import log
from app.services.industry_cluster_service import (
    get_industry_cluster_payload,
    get_industry_stock_payload,
)

industry_analysis_blueprint = Blueprint('industry_analysis', __name__,)


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
def index():
    template_filename = 'industry_analysis/industry.html'
    return render_template(template_filename, title='行业分析')


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
