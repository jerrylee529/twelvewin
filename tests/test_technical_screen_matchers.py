# -*- coding: utf-8 -*-

import unittest

import sys
import os

import pandas as pd

_ANALYSIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
if _ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, _ANALYSIS_DIR)

from technical_screens import match_above_ma, match_break_ma, match_ma_long


class TechnicalScreenMatchersTestCase(unittest.TestCase):
    def _frame(self, closes, opens=None):
        dates = ['2026-05-{:02d}'.format(index + 1) for index in range(len(closes))]
        if opens is None:
            opens = closes
        return pd.DataFrame({'date': dates, 'open': opens, 'close': closes})

    def test_match_ma_long_detects_bullish_alignment(self):
        closes = list(range(1, 21))
        result = match_ma_long(self._frame(closes), ma1=5, ma2=10, ma3=20)
        self.assertEqual(20.0, result)

    def test_match_ma_long_rejects_non_bullish_alignment(self):
        closes = list(range(20, 0, -1))
        result = match_ma_long(self._frame(closes), ma1=5, ma2=10, ma3=20)
        self.assertIsNone(result)

    def test_match_break_ma_detects_cross_up(self):
        closes = [10.0] * 19 + [12.0]
        opens = [10.0] * 19 + [9.5]
        result = match_break_ma(self._frame(closes, opens=opens), ma1=20)
        self.assertEqual(12.0, result)

    def test_match_above_ma_detects_price_above_ma(self):
        closes = [10.0] * 249 + [20.0]
        result = match_above_ma(self._frame(closes), ma1=250)
        self.assertEqual(20.0, result)


if __name__ == '__main__':
    unittest.main()
