# -*- coding: utf-8 -*-

import unittest

from app.services.analysis_access import csv_dev_fallback_enabled, resolve_published_rows
from app.services.csv_store import CsvReadResult


class AnalysisAccessTestCase(unittest.TestCase):
    def test_csv_fallback_is_opt_in(self):
        self.assertFalse(csv_dev_fallback_enabled({'DEBUG': True, 'CSV_DEV_FALLBACK': False}))
        self.assertTrue(csv_dev_fallback_enabled({'DEBUG': False, 'CSV_DEV_FALLBACK': True}))
        self.assertFalse(csv_dev_fallback_enabled({'DEBUG': False, 'CSV_DEV_FALLBACK': 'false'}))

    def test_resolve_returns_empty_when_no_db_and_no_fallback(self):
        result = resolve_published_rows(
            {'DEBUG': False, 'READ_ANALYSIS_FROM_DB': True, 'RESULT_PATH': '/tmp'},
            db_fetch=lambda: None,
            csv_filename='stock_pe.csv',
        )
        self.assertEqual([], result.rows)
        self.assertTrue(result.missing)


if __name__ == '__main__':
    unittest.main()
