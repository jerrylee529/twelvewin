# -*- coding: utf-8 -*-


from flask import jsonify, request, render_template, Blueprint
import json
from app.models import StockLabels
from app import db
from flask_login import login_required
from flask import current_app
from app.services.business_service import get_business_rows

business_blueprint = Blueprint('business', __name__)


class LabelResult:
    code = ''
    labels = ''

    def __init__(self, code, labels):
        self.code = code
        self.labels = labels


# 处理精选排行
def handle_business(labels):
    result = get_business_rows(
        current_app.config,
        labels,
        label_lookup=_get_stock_labels,
        add_id=False,
    )

    if result.error:
        current_app.logger.warning("Could not read business CSV %s: %s", result.path, result.error)

    template_filename = "business.html"

    return render_template(template_filename, title='精选股票', stockdata=result.rows)


def _get_stock_labels(code):
    stock_labels = db.session.query(StockLabels).filter_by(code=code).first()
    if stock_labels is None:
        return None
    return stock_labels.labels


# 获取精选排行数据
def create_business_data(labels):
    result = get_business_rows(
        current_app.config,
        labels,
        label_lookup=_get_stock_labels,
        add_id=True,
    )

    if result.error:
        current_app.logger.warning("Could not read business CSV %s: %s", result.path, result.error)

    return result.rows


# 处理精选排行的ajax数据请求
@business_blueprint.route('/data', methods=['POST', 'GET'])
@login_required
def get_business_data():
    print("get business data")

    info = request.values
    limit = info.get('limit', 10)  # 每页显示的条数
    offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
    labels = info.get('labels', '')

    data = create_business_data(labels)
    # return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
    return jsonify({'total': len(data), 'rows': data})
