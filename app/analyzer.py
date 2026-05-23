# -*- coding: utf-8 -*-

"""Lightweight web-facing analyzer (no sklearn/tushare offline compute)."""

__author__ = 'Jerry Lee'

import json
import time

from app.redis_op import RedisOP
from app.models import Instrument, XueQiuReportInfo


class Analyzer(object):
    """Read-only helpers for instruments, Redis quotes, and stored finance data."""

    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.securities = []
        self.instruments = []
        self.__get_instruments()

    def __get_instruments(self):
        try:
            self.securities = self.db.session.query(Instrument).all()

            index = 1
            for security in self.securities:
                if not security.code:
                    continue
                item = {
                    'id': index,
                    'code': security.code,
                    'name': security.name,
                    'industry': security.industry,
                }
                self.instruments.append(item)
                index += 1
        except Exception as exc:
            print(str(exc))

    def get_quotation(self, code):
        try:
            redis_op = RedisOP()
            return redis_op.get_hash(code)
        except Exception as exc:
            print(str(exc))
            return None

    def get_prediction(self, code):
        """Prediction is produced offline; web tier returns empty series."""
        return [], [], []

    def get_finance_indicators(self, code):
        query_result = (
            self.db.session.query(XueQiuReportInfo)
            .filter_by(security_code=code, report_type=3)
            .first()
        )

        reports = {}
        if query_result is None:
            return reports

        json_data = json.loads(query_result.report_data)

        for item in json_data['data']['list']:
            year = time.strftime('%Y', time.localtime(item['report_date'] / 1000))
            report = reports.get(year)
            if report is None:
                report = {}
                reports[year] = report

            for key in item.keys():
                if isinstance(item[key], list):
                    report[key] = item[key][0]
                else:
                    report[key] = item[key]

        return reports

    def industry_cluster_basic(self, industry):
        return None

    def industry_cluster_by_tech(self, industry, begin_date):
        return None

    def industry_cluster_profit(self, industry):
        return None

    def industry_cluster_operation(self, industry):
        return None

    def industry_cluster_debtpaying(self, industry):
        return None

    def industry_cluster_growth(self, industry):
        return None

    def industry_cluster_cashflow(self, industry):
        return None
