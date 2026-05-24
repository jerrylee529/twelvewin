# -*- coding: utf-8 -*-

import unittest

from core.stock_codes import normalize_stock_code


class StockCodeTestCase(unittest.TestCase):
    def test_normalize_stock_code_preserves_leading_zeroes(self):
        self.assertEqual('000001', normalize_stock_code(1))
        self.assertEqual('000001', normalize_stock_code('1.0'))
        self.assertEqual('000001', normalize_stock_code('000001'))
        self.assertEqual('600000', normalize_stock_code('600000'))

    def test_normalize_stock_code_keeps_suffix_codes(self):
        self.assertEqual('000001.SZ', normalize_stock_code('000001.SZ'))


if __name__ == '__main__':
    unittest.main()
