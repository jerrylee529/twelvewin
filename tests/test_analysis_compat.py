# -*- coding: utf-8 -*-

import os
import sys
import unittest

ANALYSIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "analysis"))
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)

try:
    import pandas as pd
except ImportError:
    pd = None

from compat import apply_close_price


class AnalysisCompatTestCase(unittest.TestCase):
    @unittest.skipUnless(pd is not None, "pandas not installed")
    def test_apply_close_price_uses_settlement_when_trade_is_zero(self):
        df = pd.DataFrame(
            [
                {"trade": 0.0, "settlement": 9.5},
                {"trade": 10.2, "settlement": 10.0},
            ]
        )

        apply_close_price(df)

        self.assertEqual(9.5, float(df.loc[0, "close"]))
        self.assertEqual(10.2, float(df.loc[1, "close"]))


if __name__ == "__main__":
    unittest.main()
