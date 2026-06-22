# -*- coding: utf-8 -*-

import unittest

from analysis.filing.qiniu_client import _is_s3_domain, _object_resource_url, _s3_region_from_domain


class QiniuClientTestCase(unittest.TestCase):
    def test_object_resource_url_encodes_non_ascii_key(self):
        url = _object_resource_url(
            'https://cdn.example.com',
            '000001_第一季度季报_2026_20260425.pdf',
        )
        self.assertTrue(url.startswith('https://cdn.example.com/'))
        self.assertNotIn('第一季度', url)
        self.assertIn('%E7%AC%AC', url)

    def test_is_s3_domain(self):
        self.assertTrue(_is_s3_domain('twelvewin.s3.cn-south-1.qiniucs.com'))
        self.assertFalse(_is_s3_domain('cdn.example.com'))

    def test_s3_region_from_domain(self):
        region = _s3_region_from_domain('twelvewin.s3.cn-south-1.qiniucs.com')
        self.assertEqual('cn-south-1', region)


if __name__ == '__main__':
    unittest.main()
