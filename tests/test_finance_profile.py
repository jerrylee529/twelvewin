# -*- coding: utf-8 -*-

import json
import os
import sys
import unittest

os.environ.setdefault('TWELVEWIN_DISABLE_ANALYZER', '1')

ANALYSIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)

from finance_profile import (
    build_finance_profile_list_item,
    build_finance_profile_report_data,
    period_to_report_date_ms,
)
from api.services.stocks import get_profile


class FinanceProfileBuildTestCase(unittest.TestCase):
    def test_period_to_report_date_ms(self):
        self.assertEqual(
            period_to_report_date_ms('20241231'),
            period_to_report_date_ms('2024-12-31'.replace('-', '')),
        )

    def test_build_finance_profile_list_item(self):
        item = build_finance_profile_list_item(
            {
                'end_date': '20241231',
                'roe': 9.0457,
                'eps': 0.3176,
                'dt_eps': 0.3176,
                'grossprofit_margin': 54.9693,
                'dt_netprofit_yoy': 3.9,
                'profit_dedt': 463191833.42,
            }
        )
        self.assertEqual(item['avg_roe'], [9.0457])
        self.assertEqual(item['basic_eps'], [0.3176])
        self.assertEqual(item['gross_selling_rate'], [54.9693])
        self.assertEqual(item['np_atsopc_nrgal_yoy'], [3.9])
        self.assertEqual(item['net_profit_after_nrgal_atsolc'], [463191833.42])
        self.assertEqual(item['np_per_share'], [0.3176])

    def test_build_finance_profile_report_data(self):
        payload = build_finance_profile_report_data(
            [
                {
                    'report_date': period_to_report_date_ms('20241231'),
                    'avg_roe': [9.05],
                    'basic_eps': [0.32],
                }
            ]
        )
        parsed = json.loads(payload)
        self.assertEqual(len(parsed['data']['list']), 1)
        self.assertEqual(parsed['data']['list'][0]['avg_roe'], [9.05])


class FinanceProfileServiceTestCase(unittest.TestCase):
    def test_get_profile_reads_tushare_shaped_payload(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from api.db.models import Base, XueQiuReportInfo

        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()

        report_data = build_finance_profile_report_data(
            [
                {
                    'report_date': period_to_report_date_ms('20231231'),
                    'avg_roe': [9.67],
                    'basic_eps': [0.31],
                    'gross_selling_rate': [53.25],
                    'np_atsopc_nrgal_yoy': [8.93],
                    'net_profit_after_nrgal_atsolc': [458734600.0],
                    'np_per_share': [0.31],
                },
                {
                    'report_date': period_to_report_date_ms('20241231'),
                    'avg_roe': [9.05],
                    'basic_eps': [0.32],
                    'gross_selling_rate': [54.97],
                    'np_atsopc_nrgal_yoy': [3.9],
                    'net_profit_after_nrgal_atsolc': [463191833.42],
                    'np_per_share': [0.32],
                },
            ]
        )
        session.add(
            XueQiuReportInfo(
                security_code='000755',
                security_name='000755',
                report_type=3,
                report_data=report_data,
            )
        )
        session.commit()

        profile = get_profile(session, '000755', include_quote=False)
        self.assertEqual(len(profile['avg_roe']), 2)
        self.assertEqual(profile['avg_roe'][0]['date'], '2023')
        self.assertEqual(profile['avg_roe'][0]['value'], 9.67)
        self.assertEqual(profile['avg_roe'][1]['date'], '2024')
        self.assertEqual(profile['avg_roe'][1]['value'], 9.05)
        self.assertEqual(profile['basic_eps'][1]['value'], 0.32)
        self.assertEqual(profile['net_profit_after_nrgal_atsolc'][1]['value'], 46319.18)

        session.close()


if __name__ == '__main__':
    unittest.main()
