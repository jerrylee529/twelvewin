# -*- coding: utf-8 -*-

import os
import sys
import unittest

import pandas as pd

ANALYSIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)

from cluster_compute import compute_rate_series


class ClusterComputeTestCase(unittest.TestCase):
    def test_compute_rate_series_from_close_changes(self):
        frame = pd.DataFrame(
            {
                'date': ['2026-05-20', '2026-05-21', '2026-05-22'],
                'close': [100.0, 110.0, 99.0],
            }
        )
        series = compute_rate_series(
            frame,
            begin_date='2026-05-20',
            end_date='2026-05-22',
        )
        self.assertIsNotNone(series)
        self.assertEqual(3, len(series))
        self.assertAlmostEqual(-11.0 / 99.0 * 100.0, float(series.iloc[-1]), places=5)

    def test_concat_series_map_avoids_fragmentation_pattern(self):
        first = pd.Series([1.0, 2.0], index=pd.to_datetime(['2026-05-20', '2026-05-21']))
        second = pd.Series([3.0, 4.0], index=pd.to_datetime(['2026-05-20', '2026-05-21']))
        data = pd.concat({'600000': first, '000001': second}, axis=1)
        self.assertEqual(['600000', '000001'], list(data.columns))
        self.assertEqual(2, len(data.columns))


if __name__ == '__main__':
    unittest.main()
