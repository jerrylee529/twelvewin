# -*- coding: utf-8 -*-

import datetime
import unittest

from core.filing_names import parse_filing_filename


class FilingNameParseTestCase(unittest.TestCase):
    def test_annual_report(self):
        parsed = parse_filing_filename('000001_年报_2024_20250315.pdf')
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual('000001', parsed.code)
        self.assertEqual('annual', parsed.report_kind)
        self.assertEqual(0, parsed.season)
        self.assertEqual(2024, parsed.year)
        self.assertEqual(datetime.date(2025, 3, 15), parsed.publish_date)
        self.assertEqual('2024 年报', parsed.display_label)

    def test_semi_annual_report(self):
        parsed = parse_filing_filename('000001_半年报_2024_20240816.pdf')
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual('semi_annual', parsed.report_kind)
        self.assertEqual(2, parsed.season)
        self.assertEqual('2024 半年报', parsed.display_label)

    def test_q1_report(self):
        parsed = parse_filing_filename('000001_第一季度季报_2024_20240420.pdf')
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual('quarterly', parsed.report_kind)
        self.assertEqual(1, parsed.season)

    def test_q3_report(self):
        parsed = parse_filing_filename('000001_第三季度季报_2024_20241025.pdf')
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(3, parsed.season)

    def test_key_with_prefix(self):
        parsed = parse_filing_filename('filings/000001/000001_年报_2023_20240315.pdf')
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(2023, parsed.year)

    def test_invalid_filename(self):
        self.assertIsNone(parse_filing_filename('random.pdf'))
        self.assertIsNone(parse_filing_filename('000001_未知类型_2024_20250315.pdf'))


if __name__ == '__main__':
    unittest.main()
