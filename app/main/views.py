# -*- coding: utf-8 -*-


#################
#### imports ####
#################

from flask import render_template
from flask import Blueprint, request, jsonify
from flask_login import current_user
from flask_login import login_required
from app.models import SelfSelectedStock, Instrument, Report
from app import db
from app import analyzer

################
#### config ####
################

import sys   #reload()之前必须要引入模块
reload(sys)
sys.setdefaultencoding('utf-8')

main_blueprint = Blueprint('main', __name__,)


################
#### routes ####
################

@main_blueprint.route('/')
def home():
    return render_template('main/index.html', current_user=current_user)


@main_blueprint.route('/main/instruments', methods=['GET', 'POST'])
def get_instruments():
    query = request.form.get('query')
    if query is not None:
        print(u"get instruments %s" % query)

    instruments = db.session.query(Instrument).all()

    items = []

    id = 1
    for instrument in instruments:
        if (instrument.code is None) or (instrument.code == ''):
            continue
        item = {}
        item['id'] = id
        item['code'] = instrument.code
        item['name'] = instrument.name
        items.append(item)
        id += 1

    return jsonify({'instruments': items})


@main_blueprint.route('/main/predict', methods=['GET', 'POST'])
def predict():
    code = request.values.get('code-search', '600000').split()[0]

    # 获取行情数据
    quot = analyzer.get_quotation(code)

    print quot

    return render_template('main/result.html', current_user=current_user, quot=quot)