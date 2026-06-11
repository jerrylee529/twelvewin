# -*- coding: utf-8 -*-

import os
import sys
import unittest

import pandas as pd

ANALYSIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)

from cluster_compute import (
    assign_cluster_correlations,
    build_cluster_chart_payload,
    cluster_fundamentals,
    ClusterGroup,
    ClusterGroups,
    ClusterItem,
    _compute_embedding,
    compute_rate_series,
    lookup_instrument_name,
)


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

    def test_assign_cluster_correlations_uses_center_pearson(self):
        data = pd.DataFrame(
            {
                '600000': [1.0, 2.0, 3.0, 4.0],
                '000001': [1.0, 2.0, 3.0, 4.0],
                '000002': [4.0, 3.0, 2.0, 1.0],
            }
        )
        groups = ClusterGroups()
        center = ClusterGroup(code='600000', name='Center', label=0)
        center.add(ClusterItem(code='600000', name='Center', corr=1.0))
        center.add(ClusterItem(code='000001', name='Same Trend', corr=1.0))
        center.add(ClusterItem(code='000002', name='Opposite', corr=1.0))
        groups.add(center)

        assign_cluster_correlations(groups, data.corr())

        self.assertAlmostEqual(1.0, center.stocks['600000'].corr)
        self.assertAlmostEqual(1.0, center.stocks['000001'].corr)
        self.assertLess(center.stocks['000002'].corr, 0.0)

    def test_lookup_instrument_name_handles_duplicate_index_rows(self):
        instruments = pd.DataFrame(
            {
                'code': ['600845', '600845'],
                'name': ['宝信软件', '宝信软件'],
            }
        ).set_index('code')

        self.assertEqual('宝信软件', lookup_instrument_name(instruments, '600845'))
        self.assertEqual('000001', lookup_instrument_name(instruments, '000001'))

    def test_build_cluster_chart_payload_contains_visual_layers(self):
        data = pd.DataFrame(
            {
                '600000': [1.0, 2.0, 3.0, 4.0, 5.0],
                '000001': [1.0, 2.0, 3.0, 4.0, 5.0],
                '000002': [5.0, 4.0, 3.0, 2.0, 1.0],
            }
        )
        groups = ClusterGroups()
        center = ClusterGroup(code='600000', name='Center', label=0)
        center.add(ClusterItem(code='600000', name='Center', corr=1.0))
        center.add(ClusterItem(code='000001', name='Same Trend', corr=1.0))
        groups.add(center)
        opposite = ClusterGroup(code='000002', name='Opposite', label=1)
        opposite.add(ClusterItem(code='000002', name='Opposite', corr=1.0))
        groups.add(opposite)
        assign_cluster_correlations(groups, data.corr())

        payload = build_cluster_chart_payload(groups, data, value_mode='returns')

        self.assertEqual(3, len(payload['nodes']))
        self.assertGreater(len(payload['edges']), 0)
        self.assertEqual(3, len(payload['heatmap']['labels']))
        self.assertEqual(2, len(payload['clusters']))
        self.assertEqual('returns', payload['meta']['valueMode'])

    def test_compute_embedding_handles_degenerate_matrix_without_nan(self):
        import math

        matrix = [[0.0] * 8 for _ in range(6)]
        coords = _compute_embedding(matrix)

        self.assertEqual(6, len(coords))
        for point_x, point_y in coords:
            self.assertTrue(math.isfinite(point_x))
            self.assertTrue(math.isfinite(point_y))

    def test_cluster_fundamentals_uses_snapshot_style_columns(self):
        frame = pd.DataFrame(
            [
                {'code': '000001', 'name': 'A', 'pe': 8.0, 'pb': 1.2, 'roe': 12.0},
                {'code': '000002', 'name': 'B', 'pe': 9.0, 'pb': 1.3, 'roe': 11.0},
                {'code': '000003', 'name': 'C', 'pe': 20.0, 'pb': 3.5, 'roe': 4.0},
                {'code': '000004', 'name': 'D', 'pe': 21.0, 'pb': 3.8, 'roe': 3.5},
            ]
        ).set_index('code')

        groups, data = cluster_fundamentals(frame)

        self.assertGreater(len(groups.items), 0)
        self.assertIsNotNone(data)
        self.assertGreater(data.shape[1], 0)

    def test_build_cluster_chart_payload_handles_identical_return_series(self):
        data = pd.DataFrame({code: [0.01] * 12 for code in ('600000', '000001', '000002')})
        groups = ClusterGroups()
        center = ClusterGroup(code='600000', name='Center', label=0)
        for code, name in (('600000', 'Center'), ('000001', 'Peer A'), ('000002', 'Peer B')):
            center.add(ClusterItem(code=code, name=name, corr=1.0))
        groups.add(center)
        assign_cluster_correlations(groups, data.corr())

        payload = build_cluster_chart_payload(groups, data, value_mode='returns')

        self.assertEqual(3, len(payload['nodes']))
        for node in payload['nodes']:
            self.assertTrue(abs(node['x']) < 10.0)
            self.assertTrue(abs(node['y']) < 10.0)


if __name__ == '__main__':
    unittest.main()
