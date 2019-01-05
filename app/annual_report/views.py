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
from app.util import model_to_json

import sys   #reload()之前必须要引入模块
reload(sys)
sys.setdefaultencoding('utf-8')

annual_report_blueprint = Blueprint('annual_report', __name__,)


@annual_report_blueprint.route('/annual_report/<path>', methods=['POST', 'GET'])
@login_required
def index(path):
    print("annual report: " + path)

    return render_template('annual_report/annual_report.html', year=path)


#
@annual_report_blueprint.route('/annual_report_stock/<year>/<amporchange>/<highorlow>', methods=['POST', 'GET'])
@login_required
def get_stock_report(year, amporchange, highorlow):
    print("annual report for stock: {}, {}, {}".format(year, amporchange, highorlow))

    data = []

    pic_path = current_app.config['RESULT_PATH'] + '/' + "annual_technique_report_" + year + ".csv"

    filemt = time.localtime(os.stat(pic_path).st_mtime)
    #print time.strftime("%Y-%m-%d", filemt)

    # 读取csv至字典
    csvFile = open(pic_path, "r")

    field_types = [('change_rate', float), ('amplitude', float)]

    index = 1
    for row in csv.DictReader(csvFile):
        row['id'] = index
        row['updateTime'] = time.strftime("%Y-%m-%d", filemt)
        row.update((key, conversion(row[key])) for key, conversion in field_types)
        index += 1
        data.append(row)

    if int(amporchange) == 0:
        field = 'change_rate'
    else:
        field = 'amplitude'

    data.sort(key=lambda e: e.__getitem__(field), reverse=True)

    if int(highorlow) == 0:
        return jsonify({'total': 10, 'rows': data[0:10]})
    else:
        return jsonify({'total': 10, 'rows': data[:-11:-1]})


#
@annual_report_blueprint.route('/annual_report_industry/<year>/<amporchange>/<highorlow>', methods=['POST', 'GET'])
@login_required
def get_industry_report(year, amporchange, highorlow):
    print("annual report for industry: " + year)

    data = []

    pic_path = current_app.config['RESULT_PATH'] + '/' + "annual_industry_report_" + year + ".csv"

    filemt = time.localtime(os.stat(pic_path).st_mtime)
    #print time.strftime("%Y-%m-%d", filemt)

    field_types = [('avg_change_rate', float), ('avg_amplitude', float)]

    # 读取csv至字典
    csvFile = open(pic_path, "r")

    index = 1
    for row in csv.DictReader(csvFile):
        row['id'] = index
        row['updateTime'] = time.strftime("%Y-%m-%d", filemt)
        index += 1
        row.update((key, conversion(row[key])) for key, conversion in field_types)
        data.append(row)

    if int(amporchange) == 0:
        field = 'avg_change_rate'
    else:
        field = 'avg_amplitude'

    data.sort(key=lambda e: e.__getitem__(field), reverse=True)

    if int(highorlow) == 0:
        return jsonify({'total': 10, 'rows': data[0:10]})
    else:
        return jsonify({'total': 10, 'rows': data[:-11:-1]})


