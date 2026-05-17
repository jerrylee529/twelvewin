# -*- coding: utf-8 -*-


from flask import request, jsonify, Blueprint, render_template, current_app
from flask_login import login_required, current_user
import json
from app import db
from app.models import SelfSelectedStock
from app.decorators import check_confirmed
from app.util import model_to_json
from app.services.csv_store import convert_fields, read_rows

annual_report_blueprint = Blueprint('annual_report', __name__,)


@annual_report_blueprint.route('/annual_report/<path>', methods=['POST', 'GET'])
#@login_required
def index(path):
    print("annual report: " + path)

    return render_template('annual_report/annual_report.html', year=path)


#
@annual_report_blueprint.route('/annual_report_stock/<year>/<amporchange>/<highorlow>', methods=['POST', 'GET'])
#@login_required
def get_stock_report(year, amporchange, highorlow):
    print("annual report for stock: {}, {}, {}".format(year, amporchange, highorlow))

    data = []

    field_types = [('change_rate', float), ('amplitude', float)]

    result = read_rows(
        current_app.config['RESULT_PATH'],
        "annual_technique_report_" + year + ".csv",
        add_id=True,
        add_update_time=True,
        row_transform=lambda row: convert_fields(row, field_types),
    )

    if result.error:
        current_app.logger.warning("Could not read annual stock report CSV %s: %s", result.path, result.error)

    data = result.rows

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
#@login_required
def get_industry_report(year, amporchange, highorlow):
    print("annual report for industry: " + year)

    data = []

    field_types = [('avg_change_rate', float), ('avg_amplitude', float)]

    result = read_rows(
        current_app.config['RESULT_PATH'],
        "annual_industry_report_" + year + ".csv",
        add_id=True,
        add_update_time=True,
        row_transform=lambda row: convert_fields(row, field_types),
    )

    if result.error:
        current_app.logger.warning("Could not read annual industry report CSV %s: %s", result.path, result.error)

    data = result.rows

    if int(amporchange) == 0:
        field = 'avg_change_rate'
    else:
        field = 'avg_amplitude'

    data.sort(key=lambda e: e.__getitem__(field), reverse=True)

    if int(highorlow) == 0:
        return jsonify({'total': 10, 'rows': data[0:10]})
    else:
        return jsonify({'total': 10, 'rows': data[:-11:-1]})


