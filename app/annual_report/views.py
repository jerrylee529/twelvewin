# -*- coding: utf-8 -*-


from flask import request, jsonify, Blueprint, render_template, current_app
from flask_login import login_required, current_user
import json
from app import db
from app.models import SelfSelectedStock
from app.decorators import check_confirmed
from app.util import model_to_json
from app.services.annual_report_service import get_annual_industry_rows, get_annual_stock_rows

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

    result = get_annual_stock_rows(current_app.config, year)

    if result.error:
        current_app.logger.warning(
            "Could not read annual stock report for %s: %s",
            year,
            result.error,
        )

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

    result = get_annual_industry_rows(current_app.config, year)

    if result.error:
        current_app.logger.warning(
            "Could not read annual industry report for %s: %s",
            year,
            result.error,
        )

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


