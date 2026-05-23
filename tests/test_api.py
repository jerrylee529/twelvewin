# -*- coding: utf-8 -*-

import datetime
import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.db.models import AnalysisRun, Base, FundamentalSnapshot, RankingResult
from api.main import app
from api.services.fundamentals import search_fundamentals
from api.services.published_results import get_ranking_rows
from fastapi.testclient import TestClient


class ApiRankingTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

        run = AnalysisRun(
            category=AnalysisRun.CATEGORY_RANKING,
            result_key='pe',
            as_of_date=datetime.date(2026, 5, 21),
            row_count=1,
            source_file='stock_pe.csv',
            create_time=datetime.datetime.now(),
        )
        self.session.add(run)
        self.session.flush()

        self.session.add(
            RankingResult(
                run_id=run.id,
                rank_order=1,
                code='600000',
                name='Test Bank',
                data=json.dumps({'per': 8.5, 'close': 10.2, 'pb': 1.1}, ensure_ascii=False),
            )
        )
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_get_ranking_rows_from_sqlite(self):
        result = get_ranking_rows(self.session, 'pe')
        self.assertIsNone(result.error)
        self.assertEqual(1, len(result.rows))
        self.assertEqual('600000', result.rows[0]['code'])
        self.assertEqual(8.5, result.rows[0]['per'])
        self.assertEqual('2026-05-21', result.update_time)

    def test_unknown_ranking_key(self):
        result = get_ranking_rows(self.session, 'unknown')
        self.assertEqual([], result.rows)
        self.assertEqual('unknown ranking key', result.error)


class ApiFundamentalScreenerTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

        now = datetime.datetime.now()
        trade_date = datetime.date(2026, 5, 21)
        self.session.add_all([
            FundamentalSnapshot(
                trade_date=trade_date,
                code='600000',
                name='Test Bank',
                industry='Bank',
                is_st=False,
                close=10.0,
                pe_ttm=8.0,
                pb_lf=0.8,
                roe=12.0,
                roe_y1=12.0,
                roe_y2=11.0,
                roe_y3=10.5,
                dividend_yield=4.0,
                market_cap=1000000,
                float_market_cap=800000,
                pe_discount_to_industry=0.7,
                pb_discount_to_industry=0.8,
                create_time=now,
                update_time=now,
            ),
            FundamentalSnapshot(
                trade_date=trade_date,
                code='000001',
                name='Growth Co',
                industry='Tech',
                is_st=False,
                close=20.0,
                pe_ttm=35.0,
                pb_lf=4.0,
                roe=8.0,
                dividend_yield=0.5,
                market_cap=2000000,
                float_market_cap=1500000,
                pe_discount_to_industry=1.4,
                pb_discount_to_industry=1.2,
                create_time=now,
                update_time=now,
            ),
        ])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_screener_filters_and_counts_before_pagination(self):
        result = search_fundamentals(
            self.session,
            pe_min=5,
            pe_max=20,
            pb_max=2,
            roe_3y_min=10,
            dividend_yield_min=3,
            page_size=1,
        )
        self.assertIsNone(result.error)
        self.assertEqual(1, result.total)
        self.assertEqual('600000', result.rows[0]['code'])


class ApiHttpTestCase(unittest.TestCase):
    def test_health_endpoint(self):
        client = TestClient(app)
        response = client.get('/api/v1/health')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'status': 'ok'}, response.json())


if __name__ == '__main__':
    unittest.main()
