# -*- coding: utf-8 -*-

import datetime
import json
import os
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.db.models import (
    AnalysisRun,
    Base,
    FundamentalSnapshot,
    IndustryFundamentalBenchmark,
    Instrument,
    RankingResult,
    TechnicalScreenResult,
)
from api.main import create_app
from api.services.research_context import get_research_context
from fastapi.testclient import TestClient


class ResearchContextServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        now = datetime.datetime.now()
        trade_date = datetime.date(2026, 5, 21)

        self.session.add(
            Instrument(
                code='600000',
                name='Test Bank',
                industry='Bank',
            )
        )
        self.session.add(
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
            )
        )
        self.session.add(
            IndustryFundamentalBenchmark(
                trade_date=trade_date,
                industry='Bank',
                stock_count=10,
                median_pe_ttm=9.0,
                median_pb_lf=0.9,
                median_roe=11.0,
                median_dividend_yield=3.5,
                create_time=now,
                update_time=now,
            )
        )

        ranking_run = AnalysisRun(
            category=AnalysisRun.CATEGORY_RANKING,
            result_key='pe',
            as_of_date=trade_date,
            row_count=1,
            create_time=now,
        )
        self.session.add(ranking_run)
        self.session.flush()
        self.session.add(
            RankingResult(
                run_id=ranking_run.id,
                rank_order=15,
                code='600000',
                name='Test Bank',
                data=json.dumps({'per': 8.0}),
            )
        )

        technical_run = AnalysisRun(
            category=AnalysisRun.CATEGORY_TECHNICAL,
            result_key='ma_long',
            as_of_date=trade_date,
            row_count=1,
            create_time=now,
        )
        self.session.add(technical_run)
        self.session.flush()
        self.session.add(
            TechnicalScreenResult(
                run_id=technical_run.id,
                rank_order=1,
                code='600000',
                name='Test Bank',
                data=json.dumps({'close': 10.0}),
            )
        )
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_get_research_context_includes_fundamentals_and_signals(self):
        payload = get_research_context(self.session, '600000')
        self.assertEqual('600000', payload['code'])
        self.assertEqual('Test Bank', payload['name'])
        self.assertEqual('2026-05-21', payload['data_as_of'])
        self.assertEqual(8.0, payload['fundamentals']['pe_ttm'])
        self.assertEqual(9.0, payload['industry_benchmark']['median_pe_ttm'])
        self.assertIn('ma_long', payload['technical_signals'])
        self.assertEqual(15, payload['rankings']['pe'])


class ResearchContextHttpTestCase(unittest.TestCase):
    def setUp(self):
        self._env_patch = patch.dict(os.environ, {}, clear=False)
        self._env_patch.start()
        os.environ.pop('TW_RESEARCH_API_KEY', None)

    def tearDown(self):
        self._env_patch.stop()

    def test_invalid_code_returns_error_payload(self):
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        try:
            payload = get_research_context(session, '')
            self.assertEqual('invalid stock code', payload['error'])
        finally:
            session.close()
            Base.metadata.drop_all(engine)


class ResearchApiKeyMiddlewareTestCase(unittest.TestCase):
    def test_missing_key_when_required(self):
        with patch.dict(os.environ, {'TW_RESEARCH_API_KEY': 'secret-key'}, clear=False):
            app_instance = create_app()
            client = TestClient(app_instance)
            response = client.get('/api/v1/data-status')
            self.assertEqual(401, response.status_code)

            ok = client.get(
                '/api/v1/data-status',
                headers={'X-Twelvewin-Api-Key': 'secret-key'},
            )
            self.assertEqual(200, ok.status_code)

            health = client.get('/api/v1/health')
            self.assertEqual(200, health.status_code)


if __name__ == '__main__':
    unittest.main()
