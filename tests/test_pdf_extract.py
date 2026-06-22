# -*- coding: utf-8 -*-

import unittest

from analysis.filing.pdf_extract import sanitize_extracted_text


class PdfExtractSanitizeTestCase(unittest.TestCase):
    def test_sanitize_extracted_text_strips_nul_bytes(self):
        raw = '神州数码\x00集团股份有限公司'
        self.assertEqual('神州数码集团股份有限公司', sanitize_extracted_text(raw))

    def test_sanitize_extracted_text_preserves_normal_text(self):
        text = '第一节 管理层讨论与分析'
        self.assertEqual(text, sanitize_extracted_text(text))


if __name__ == '__main__':
    unittest.main()
