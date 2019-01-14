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

    return jsonify({'instruments': analyzer.instruments})


@main_blueprint.route('/main/predict', methods=['GET', 'POST'])
def predict():
    code = request.values.get('code-search', '600000').split()[0]

    # 获取行情数据
    quot = analyzer.get_quotation(code)

    try:
        dates, reals, predicts = analyzer.get_prediction(code)
    except Exception as e:
        print("could not get prediction, %s" % code)
        
    predictions = []

    if len(dates) > 0:
        for i in range(1, len(dates)):
            item = {}
            item['date'] = dates[i]
            item['real'] = u"涨" if reals[i] > 0.0 else u"跌"
            item['predict'] = u"涨" if predicts[i-1] > 0.0 else u"跌"
            predictions.append(item)

        last_item = {}
        last_item['date'] = "下个交易日"
        last_item['real'] = u""
        last_item['predict'] = u"涨" if predicts[len(dates)-1] > 0.0 else u"跌"
        predictions.append(last_item)

    quot['predictions'] = predictions

    print quot

    return render_template('main/index.html', current_user=current_user, quot=quot)


