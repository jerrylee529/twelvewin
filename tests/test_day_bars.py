# -*- coding: utf-8 -*-

import datetime
import unittest

from app import app, db
from app.models import DailyBar
from core.day_bars import get_last_trade_date, load_bars_dataframe


class DayBarsTestCase(unittest.TestCase):
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

    def test_load_bars_and_last_trade_date(self):
        db.session.add_all([
            DailyBar('600000', datetime.date(2026, 5, 16), open=10, high=12, low=9, close=11),
            DailyBar('600000', datetime.date(2026, 5, 17), open=11, high=13, low=10, close=12),
        ])
        db.session.commit()

        last_date = get_last_trade_date(db.session, '600000')
        self.assertEqual(datetime.date(2026, 5, 17), last_date)

        loaded = load_bars_dataframe(db.session, '600000')
        self.assertEqual(2, len(loaded))
        self.assertEqual('2026-05-16', loaded.iloc[0]['date'])
        self.assertEqual(11.0, float(loaded.iloc[0]['close']))


if __name__ == '__main__':
    unittest.main()
