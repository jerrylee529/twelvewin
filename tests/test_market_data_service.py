# -*- coding: utf-8 -*-

import datetime
import unittest

from app import app, db
from app.models import DailyBar
from app.services.market_data_service import get_candlestick_data


class MarketDataServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_get_candlestick_data_reads_db_and_appends_realtime_quote(self):
        db.session.add(
            DailyBar(
                '600000',
                datetime.date(2026, 5, 16),
                open=10.0,
                high=12.0,
                low=9.0,
                close=11.0,
            )
        )
        db.session.commit()

        def quote_provider(code):
            self.assertEqual("600000", code)
            return {
                "update_time": "2026-05-17 15:00:00",
                "open": "11",
                "trade": "12",
                "low": "10",
                "high": "13",
            }

        result = get_candlestick_data({}, "600000", quote_provider=quote_provider)

        self.assertIsNone(result.error)
        self.assertEqual([
            ["2026-05-16", 10.0, 11.0, 9.0, 12.0],
            ["2026-05-17", 11.0, 12.0, 10.0, 13.0],
        ], result.rows)

    def test_get_candlestick_data_returns_empty_when_no_bars(self):
        result = get_candlestick_data({}, "600000")
        self.assertEqual([], result.rows)
        self.assertTrue(result.missing)


if __name__ == "__main__":
    unittest.main()
