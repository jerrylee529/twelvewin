# -*- coding: utf-8 -*-


from flask import request, jsonify, Blueprint, render_template, current_app
from flask_login import login_required, current_user
from app import db
from app.models import SelfSelectedStock
from app.decorators import check_confirmed
from app import analyzer
from app.util import model_to_json
from app.services.market_data_service import get_candlestick_data
from app.services.ranking_service import get_stock_ranking

stock_blueprint = Blueprint('stock', __name__,)


# 处理市盈率排行的ajax数据请求
@stock_blueprint.route('/<path>/data', methods=['POST', 'GET'])
#@login_required
def get_stock_data(path):
    print("get_stock_data")

    info = request.values
    limit = info.get('limit', 10)  # 每页显示的条数
    offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点

    data = []

    if (path == 'pe'):
        title = "市盈率排名"
    elif (path == 'pb'):
        title = "市净率排名"
    elif (path == 'roe'):
        title = "净资产收益率排名"
    elif (path == 'divi'):
        title = "股息率排名"
    else:
        return jsonify({'total': len(data), 'rows': data})

    result = get_stock_ranking(current_app.config, path, is_anonymous=current_user.is_anonymous)

    if result.error:
        current_app.logger.warning("Could not read stock ranking CSV %s: %s", result.path, result.error)

    data = result.rows

    #return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
    return jsonify({'total': len(data), 'rows': data})


# 处理首页的导航
@stock_blueprint.route('/<path>', methods=['GET', 'POST'])
#@login_required
#@check_confirmed
def list_stock(path):
    template_filename = 'stock/rank.html'

    title = "团赢数据"
    if path == 'pe':
        title = "市盈率排名"
    elif path == 'pb':
        title = "市净率排名"
    elif path == 'roe':
        title = "净资产收益率排名"
    elif path == 'divi':
        title = "股息率排名"
    elif path == 'business':
        title = "精选股票"
        template_filename = "business/business.html"
    else:
        return render_template('errors/404.html')

    return render_template(template_filename, title=title, path=path)


# 处理k线图
@stock_blueprint.route('/candlestick/<code>', methods=['GET', 'POST'])
def show_stock(code):
    template_filename = 'common/candlestick.html'

    return render_template(template_filename, title=code)


# 获取历史行情数据
@stock_blueprint.route('/candlestick/<code>/hq', methods=['GET', 'POST'])
def get_history_quotation(code):
    print("get_history_quotation: " + code)
    data = []

    result = get_candlestick_data(current_app.config, code, quote_provider=analyzer.get_quotation)

    if result.error:
        current_app.logger.warning("Could not read day quotation CSV %s: %s", result.path, result.error)

    data = result.rows

    #del data[:-100]

    return jsonify({'rows': data, 'updateTime': result.update_time})


# 增加自选股
@stock_blueprint.route('/stock/add_self_selected_stock', methods=['POST'])
@login_required
def add_self_selected_stock():
    code = request.form.get('code')

    email = current_user.email

    stock = db.session.query(SelfSelectedStock).filter_by(email=email, code=code).first()

    if stock is None:
        stock = SelfSelectedStock(current_user.email, code=code, labels='')

        db.session.add(stock)
    else:
        stock.deleted = False

    db.session.commit()

    myClassJson = stock.to_json()

    return jsonify(myClassJson)

