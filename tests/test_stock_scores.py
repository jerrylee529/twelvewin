# -*- coding: utf-8 -*-

import datetime
import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.db.models import Base, StockAiScore
from api.services.stock_scores import get_stock_score, upsert_stock_score


class StockScoreServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_upsert_and_get_stock_score(self):
        saved = upsert_stock_score(
            self.session,
            '000001',
            '2026-06-10',
            {
                'model': 'dify-workflow',
                'status': StockAiScore.STATUS_DONE,
                'score': {
                    'stock_code': '000001',
                    'stock_name': 'Ping An Bank',
                    'total_score': 78,
                    'grade': 'B',
                    'grade_label': '良好',
                    'data_as_of': '2026-06-10',
                    'dimensions': [],
                    'risk_adjustment': {'deduction': 0, 'reasons': []},
                    'summary': '稳健',
                    'strengths': ['ROE 稳定'],
                    'weaknesses': [],
                    'data_gaps': [],
                    'disclaimer': 'research only',
                },
                'markdown': '**综合评分**',
            },
        )
        self.session.commit()

        self.assertEqual('000001', saved['code'])
        self.assertEqual('2026-06-10', saved['data_as_of'])
        self.assertEqual(78, saved['score']['total_score'])

        cached = get_stock_score(self.session, '000001', '2026-06-10')
        self.assertIsNotNone(cached)
        assert cached is not None
        self.assertEqual('**综合评分**', cached['markdown'])

    def test_get_stock_score_miss(self):
        self.assertIsNone(get_stock_score(self.session, '000001', '2026-06-10'))


if __name__ == '__main__':
    unittest.main()
