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

from price_change_analysis import price_change


class PriceChangeAnalysisTestCase(unittest.TestCase):
    @unittest.skipUnless(pd is not None, "pandas not installed")
    def test_rate_columns_accept_float_values(self):
        instruments = pd.DataFrame({"code": ["920299"]})
        instruments["rate7"] = -9999.0

        instruments.at[0, "rate7"] = -8.181818181818187

        self.assertAlmostEqual(-8.181818181818187, instruments.at[0, "rate7"])

    @unittest.skipUnless(pd is not None, "pandas not installed")
    def test_price_change_returns_decimal_rate(self):
        df = pd.DataFrame(
            [
                {"date": "2026-06-01", "high": 11.0, "low": 10.0, "close": 11.0},
                {"date": "2026-06-10", "high": 10.2, "low": 9.8, "close": 10.1},
            ]
        )

        rate, close, update_date = price_change(df, "2026-06-01", "2026-06-10")

        self.assertAlmostEqual(-8.181818181818187, rate)
        self.assertEqual(11.0, close)
        self.assertEqual("2026-06-10", update_date)


if __name__ == "__main__":
    unittest.main()
