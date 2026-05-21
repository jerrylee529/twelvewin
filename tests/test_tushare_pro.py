# -*- coding: utf-8 -*-

import os
import sys
import unittest

os.environ.setdefault('TWELVEWIN_DISABLE_ANALYZER', '1')

ANALYSIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)

from providers.tushare_pro import code_to_ts_code, normalize_trade_date, ts_code_to_code


class TushareProTestCase(unittest.TestCase):
    def test_code_to_ts_code(self):
        self.assertEqual(code_to_ts_code('600000'), '600000.SH')
        self.assertEqual(code_to_ts_code('000001'), '000001.SZ')
        self.assertEqual(code_to_ts_code('920873'), '920873.BJ')

    def test_ts_code_to_code(self):
        self.assertEqual(ts_code_to_code('600000.SH'), '600000')

    def test_normalize_trade_date(self):
        self.assertEqual(normalize_trade_date('2024-12-31'), '20241231')
        self.assertEqual(normalize_trade_date('20241231'), '20241231')


if __name__ == '__main__':
    unittest.main()
