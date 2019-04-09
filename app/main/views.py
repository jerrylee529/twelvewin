# -*- coding: utf-8 -*-


#################
#### imports ####
#################

from flask import render_template
from flask import Blueprint, request, jsonify
from flask_login import current_user
from flask_login import login_required
from app.models import SelfSelectedStock, Instrument, Report, StockPrediction, InvestmentKnowledge
from app import db, analyzer, log

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


def convert_float(value, is_amount=False):
    result = 0.0

    if value is not None:
        result = round(value/10000 if is_amount else value, 2)

    return result


@main_blueprint.route('/main/profile/<code>', methods=['GET', 'POST'])
def get_profile(code):
    result = {}
    result['quot'] = None

    fields = ['net_profit_after_nrgal_atsolc', 'avg_roe', 'np_atsopc_nrgal_yoy', 'basic_eps', 'gross_selling_rate', 'np_per_share']

    for field in fields:
        result[field] = []

    try:
        result['quot'] = analyzer.get_quotation(code)

        reports = analyzer.get_finance_indicators(code)

        fields_amount_flag = {'net_profit_after_nrgal_atsolc': True, 'avg_roe': False, 'np_atsopc_nrgal_yoy': False, 'basic_eps': False, 'gross_selling_rate': False, 'np_per_share': False}

        #print reports

        for key in sorted(reports.keys(), reverse=False):
            row = reports[key]

            for field in fields:
                item = {}
                item['date'] = key
                item['value'] = convert_float(row[field], is_amount=fields_amount_flag[field])

                result[field].append(item)

        print result

    except Exception as e:
        log.error(repr(e))

    return jsonify(result)


@main_blueprint.route('/main/predict', methods=['GET', 'POST'])
def predict():
    code = request.values.get('code-search', '600000').split()[0]

    # 获取行情数据
    quot = analyzer.get_quotation(code)

    dates = []

    try:
        dates, reals, predicts = analyzer.get_prediction(code)

        stock = db.session.query(StockPrediction).filter_by(code=code).first()

        if stock:
            quot['accu_rate'] = stock.accu_rate
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


@main_blueprint.route('/main/knowledge', methods=['GET', 'POST'])
def get_investment_knowledge():
    page_index = request.values.get('page_index', default=1, type=int)
    page_size = request.values.get('page_size', default=10, type=int)

    page = []

    total_size = 0

    try:
        total_size = db.session.query(InvestmentKnowledge).count()

        result = db.session.query(InvestmentKnowledge).order_by(InvestmentKnowledge.priority).limit(page_size).offset((page_index-1)*page_size)

        for rec in result:
            item = {}
            item['id'] = rec.id
            item['title'] = rec.title
            item['category'] = rec.category
            item['content'] = rec.content

            page.append(item)

    except Exception as e:
        print("could not get investment knowledge, {}, {}, {}".format(page_index, page_size, repr(e)))

    ret = {"total": total_size, "page": page}

    log.debug(ret)

    return jsonify(ret)