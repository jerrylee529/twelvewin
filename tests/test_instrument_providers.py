# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import unittest

ANALYSIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)

try:
    import pandas as pd
except ImportError:
    pd = None

import importlib.util

_base_path = os.path.join(ANALYSIS_DIR, 'providers', 'base.py')
_spec = importlib.util.spec_from_file_location('providers_base', _base_path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

normalize_stock_code = _base.normalize_stock_code
read_instruments_csv = _base.read_instruments_csv
codes_from_day_csv_directory = _base.codes_from_day_csv_directory


class InstrumentProviderTestCase(unittest.TestCase):
    def test_normalize_stock_code_strips_suffix(self):
        self.assertEqual('600000', normalize_stock_code('600000.SH'))
        self.assertEqual('000001', normalize_stock_code('sz000001'))

    @unittest.skipUnless(pd is not None, "pandas not installed")
    def test_read_instruments_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'instruments.csv')
            with open(path, 'w', encoding='utf-8') as handle:
                handle.write('code,name\n600000,浦发银行\n')

            frame = read_instruments_csv(path)

            self.assertEqual(1, len(frame))
            self.assertEqual('600000', frame.iloc[0]['code'])

    def test_codes_from_day_csv_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, '600000.csv'), 'w').close()
            open(os.path.join(tmpdir, '000001.csv'), 'w').close()

            codes = codes_from_day_csv_directory(tmpdir)

            self.assertEqual(['000001', '600000'], codes)


if __name__ == '__main__':
    unittest.main()
