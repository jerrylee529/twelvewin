# -*- coding: utf-8 -*-

import datetime
import unittest

import pandas as pd

from app import app, db
from app.models import AnalysisRun, RankingResult
from compute.publish import publish_ranking_dataframe


class PublishTestCase(unittest.TestCase):
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

    def test_publish_ranking_dataframe(self):
        frame = pd.DataFrame([
            {'code': '600000', 'name': 'Test', 'pe': 8.5},
            {'code': '000001', 'name': 'Test2', 'pe': 12.0},
        ])

        summary = publish_ranking_dataframe(
            frame,
            ranking_key='pe',
            as_of_date=datetime.date(2026, 5, 21),
            session=db.session,
        )
        db.session.commit()

        self.assertEqual('published', summary['status'])
        self.assertEqual(2, summary['row_count'])

        run = AnalysisRun.query.filter_by(
            category=AnalysisRun.CATEGORY_RANKING,
            result_key='pe',
        ).one()
        rows = RankingResult.query.filter_by(run_id=run.id).order_by(RankingResult.rank_order).all()
        self.assertEqual(2, len(rows))
        self.assertEqual('600000', rows[0].code)


if __name__ == '__main__':
    unittest.main()
