# -*- coding: utf-8 -*-

import os
import sys
import unittest
from unittest import mock

os.environ.setdefault('TWELVEWIN_DISABLE_ANALYZER', '1')

ANALYSIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)

import importlib.util

_ak_path = os.path.join(ANALYSIS_DIR, 'providers', 'akshare_market.py')
_spec = importlib.util.spec_from_file_location('akshare_market', _ak_path)
_ak_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ak_mod)

_registry_path = os.path.join(ANALYSIS_DIR, 'providers', 'market_registry.py')
_spec2 = importlib.util.spec_from_file_location('market_registry', _registry_path)
_registry = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(_registry)


class AkShareMarketProviderTestCase(unittest.TestCase):
    def test_normalize_em_spot_maps_columns(self):
        import pandas as pd

        raw = pd.DataFrame({
            '代码': ['600000', '000001'],
            '名称': ['浦发银行', '平安银行'],
            '最新价': [9.0, 11.0],
            '昨收': [9.1, 10.9],
            '市盈率-动态': [5.0, 8.0],
            '市净率': [0.4, 0.9],
            '总市值': [1.0e11, 2.0e11],
            '流通市值': [8.0e10, 1.5e11],
            '换手率': [0.5, 1.2],
        })
        frame = _ak_mod._normalize_em_spot(raw)
        self.assertEqual(frame['code'].tolist(), ['600000', '000001'])
        self.assertAlmostEqual(frame['mktcap'].iloc[0], 1.0e11 / 10000.0)

    @mock.patch.object(_ak_mod, '_fetch_spot_em')
    def test_fetch_today_quotes_uses_em_when_available(self, mock_em):
        import pandas as pd

        mock_em.return_value = pd.DataFrame({
            '代码': ['600000'],
            '名称': ['浦发银行'],
            '最新价': [9.0],
            '昨收': [9.1],
            '市盈率-动态': [5.0],
            '市净率': [0.4],
            '总市值': [1.0e11],
            '流通市值': [8.0e10],
            '换手率': [0.5],
        })
        with mock.patch.object(_ak_mod, '_load_fhps', return_value=(None, '20241231')):
            frame = _ak_mod.fetch_today_quotes_dataframe(enrich=False)
        self.assertEqual(frame['code'].iloc[0], '600000')
        self.assertIn('trade', frame.columns)

    def test_market_registry_auto_without_token(self):
        with mock.patch.object(_registry, 'get_tushare_token', return_value=''):
            chain = _registry.get_market_provider_chain('auto')
        self.assertEqual(chain, ('akshare', 'yahoo', 'tushare'))

    def test_market_registry_auto_with_token(self):
        with mock.patch.object(_registry, 'get_tushare_token', return_value='test-token'):
            chain = _registry.get_market_provider_chain('auto')
        self.assertEqual(chain, ('tushare', 'akshare', 'yahoo'))

    def test_fetch_today_quotes_uses_in_process_cache(self):
        import pandas as pd

        _registry.clear_quotes_cache()
        frame = pd.DataFrame({'code': ['600000'], 'close': [9.0]})

        with mock.patch.object(_registry, '_fetch', return_value=frame) as mock_fetch:
            first = _registry.fetch_today_quotes_dataframe(enrich=False)
            second = _registry.fetch_today_quotes_dataframe(enrich=False)

        self.assertIs(first, second)
        self.assertEqual(1, mock_fetch.call_count)
        _registry.clear_quotes_cache()

    def test_fetch_today_quotes_with_retry_waits_on_empty_response(self):
        import pandas as pd

        _registry.clear_quotes_cache()
        frame = pd.DataFrame({'code': ['600000'], 'close': [9.0]})

        with mock.patch.object(_registry, '_fetch', side_effect=[None, frame]):
            with mock.patch.object(_registry.time, 'sleep') as mock_sleep:
                result = _registry.fetch_today_quotes_with_retry(
                    max_attempts=2,
                    backoff_sec=5,
                    use_cache=False,
                )

        self.assertIsNotNone(result)
        self.assertEqual(['600000'], result['code'].tolist())
        mock_sleep.assert_called_once_with(5)
        _registry.clear_quotes_cache()

    def test_code_to_yahoo_symbol(self):
        _base_path = os.path.join(ANALYSIS_DIR, 'providers', 'base.py')
        _spec = importlib.util.spec_from_file_location('providers_base', _base_path)
        base = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(base)

        self.assertEqual(base.code_to_yahoo_symbol('600000'), '600000.SS')
        self.assertEqual(base.code_to_yahoo_symbol('000001'), '000001.SZ')
        self.assertEqual(base.code_to_yahoo_symbol('920873'), '920873.BJ')
        self.assertEqual(base.code_to_yahoo_symbol('830799'), '830799.BJ')
        self.assertEqual(base.code_to_yahoo_symbol('430047'), '430047.BJ')
        self.assertEqual(base.yahoo_symbol_to_code('600000.SS'), '600000')
        self.assertEqual(base.yahoo_symbol_to_code('920873.BJ'), '920873')


if __name__ == '__main__':
    unittest.main()
