# -*- coding: utf-8 -*-


from flask import request, jsonify, Blueprint, render_template, current_app
from flask_login import login_required, current_user
from app.services.csv_store import read_rows

strategy_analysis_blueprint = Blueprint('strategy_analysis', __name__,)


# 处理市盈率排行的ajax数据请求
@strategy_analysis_blueprint.route('/<path>/data', methods=['POST', 'GET'])
#@login_required
def get_data(path):
    print("get stock data")

    info = request.values
    limit = info.get('limit', 10)  # 每页显示的条数
    offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点

    data = []

    if (path == 'pe'):
        csv_filename = "stock_pe.csv"
        title = "市盈率排名"
    elif (path == 'pb'):
        csv_filename = "stock_pb.csv"
        title = "市净率排名"
    elif (path == 'roe'):
        csv_filename = "stock_roe.csv"
        title = "净资产收益率排名"
    elif (path == 'divi'):
        csv_filename = "stock_dividence.csv"
        title = "股息率排名"
    else:
        return jsonify({'total': len(data), 'rows': data})

    result = read_rows(current_app.config['RESULT_PATH'], csv_filename, add_id=True)

    if result.error:
        current_app.logger.warning("Could not read strategy analysis CSV %s: %s", result.path, result.error)

    data = result.rows

    #return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
    return jsonify({'total': len(data), 'rows': data})

# 处理首页的导航
@strategy_analysis_blueprint.route('/strategy', methods=['GET', 'POST'])
def index():
    return render_template('errors/400.html')

