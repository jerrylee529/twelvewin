# -*- coding: utf-8 -*-

import csv
import os
import tempfile
import unittest

from app import app, db
from app.models import AnalysisRun, RankingResult
from app.services.ranking_service import get_stock_ranking
from app.services.result_store_service import (
    get_latest_analysis_run,
    import_ranking_results,
    sync_all_results_to_db,
)


class ResultStoreServiceTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite://',
            READ_ANALYSIS_FROM_DB=True,
            WTF_CSRF_ENABLED=False,
        )
        self._context = app.app_context()
        self._context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self._context.pop()

    def test_import_ranking_results_and_read_from_db(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'stock_pe.csv')
            with open(path, 'w', encoding='utf-8', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=['code', 'name', 'per'])
                writer.writeheader()
                writer.writerow({'code': '600000', 'name': '浦发银行', 'per': '8.5'})

            app.config['RESULT_PATH'] = tmpdir
            summary = import_ranking_results(app.config, 'pe')

            self.assertEqual('imported', summary['status'])
            self.assertEqual(1, summary['row_count'])

            run = get_latest_analysis_run(AnalysisRun.CATEGORY_RANKING, 'pe')
            self.assertIsNotNone(run)
            self.assertEqual(1, RankingResult.query.filter_by(run_id=run.id).count())

            os.remove(path)
            result = get_stock_ranking(app.config, 'pe')

            self.assertIsNone(result.error)
            self.assertEqual(1, len(result.rows))
            self.assertEqual('600000', result.rows[0]['code'])
            self.assertEqual('8.5', result.rows[0]['per'])

    def test_sync_all_results_skips_missing_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            app.config['RESULT_PATH'] = tmpdir
            summary = sync_all_results_to_db(app.config)

            self.assertIn('ranking_pe', summary)
            self.assertEqual('skipped', summary['ranking_pe']['status'])


if __name__ == '__main__':
    unittest.main()
