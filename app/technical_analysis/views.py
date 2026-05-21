# -*- coding: utf-8 -*-


from flask import request, jsonify, Blueprint, render_template, flash, current_app
from flask_login import current_user
import os
import datetime
from flask_login import login_required
from app.decorators import check_confirmed
from app.services.artifact_meta_service import get_artifact_update_time
from app.services.technical_analysis_service import get_price_change_rows, get_technical_rows

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

technical_analysis_blueprint = Blueprint('technical_analysis', __name__,)


# 突破历史最高价
@technical_analysis_blueprint.route('/tech/<path>/data', methods=['POST', 'GET'])
#@login_required
def get_data(path):
    print("get technical analysis data")

    info = request.values
    limit = info.get('limit',10)  # 每页显示的条数
    offset = info.get('offset',0)  # 分片数，(页码-1)*limit，它表示一段数据的起点

    result = get_technical_rows(current_app.config, path, is_anonymous=current_user.is_anonymous)

    if result.error:
        current_app.logger.warning("Could not read technical analysis CSV %s: %s", result.path, result.error)

    data = result.rows

    #return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
    return jsonify({'total': len(data), 'rows': data})


# 处理首页的导航
@technical_analysis_blueprint.route('/tech/<path>', methods=['GET', 'POST'])
#@login_required
#@check_confirmed
def index(path):
    if path == 'highest':
        flash('股价创历史新高的股票列表','历史新高')
        title = "历史新高"
    elif path == 'lowest':
        flash('股价创历史新低的股票列表', '历史新低')
        title = "历史新低"
    elif path == 'ma_long':
        flash('5日、10日、20日均线呈多头排列的个股列表','均线多头')
        title = "均线多头"
    elif path == 'break_ma':
        flash('突破20日均线的个股列表','突破均线')
        title = "突破均线"
    elif path == 'above_ma':
        flash('年线以上的个股列表','年线以上')
        title = "年线以上"
    elif path == 'filter':
        title = "涨跌幅分析"
        data_update_time = get_artifact_update_time(current_app.config, technical_key=path)
        return render_template(
            'technical_analysis/filter.html',
            title=title,
            path=path,
            data_update_time=data_update_time,
        )
    else:
        return render_template('errors/400.html')

    data_update_time = get_artifact_update_time(current_app.config, technical_key=path)
    return render_template(
        'technical_analysis/rank.html',
        title=title,
        path=path,
        data_update_time=data_update_time,
    )


@technical_analysis_blueprint.route('/tech/filter/data', methods=['POST', 'GET'])
#@login_required
def get_filter_data():
    print("get filter analysis data")

    info = request.values

    print(info)

    begin_date = request.values.get('begin_date', '2018-01-01')
    end_date = request.values.get('end_date', '2018-12-01')

    days = request.values.get('days', u'近一周')
    low = request.values.get('low', -30)
    high = request.values.get('high', 0)

    print("begin date: {}, end date: {}, days: {}, low: {}, high: {}".format(begin_date, end_date, days, low, high))

    result = get_price_change_rows(current_app.config, days=days, low=low, high=high)

    if result.error:
        current_app.logger.warning("Could not read price change CSV %s: %s", result.path, result.error)

    data = result.rows

    return jsonify({'total': len(data), 'rows': data})
