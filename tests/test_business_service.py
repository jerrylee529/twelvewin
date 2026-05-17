# -*- coding: utf-8 -*-

import csv
import os
import tempfile
import unittest

from app.services.business_service import get_business_rows


class BusinessServiceTestCase(unittest.TestCase):
    def test_get_business_rows_merges_labels_and_filters(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "stock_business.csv")
            with open(path, "w", encoding="utf-8", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["code", "name"])
                writer.writeheader()
                writer.writerow({"code": "600000", "name": "浦发银行"})
                writer.writerow({"code": "000001", "name": "平安银行"})

            labels = {"600000": "银行 蓝筹", "000001": "银行"}

            result = get_business_rows(
                {"RESULT_PATH": tmpdir},
                "蓝筹",
                label_lookup=lambda code: labels.get(code),
            )

            self.assertIsNone(result.error)
            self.assertEqual(1, len(result.rows))
            self.assertEqual(1, result.rows[0]["id"])
            self.assertEqual("600000", result.rows[0]["code"])
            self.assertEqual("银行 蓝筹", result.rows[0]["labels"])

    def test_get_business_rows_includes_unlabeled_rows_when_no_filter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "stock_business.csv")
            with open(path, "w", encoding="utf-8", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["code", "name"])
                writer.writeheader()
                writer.writerow({"code": "600000", "name": "浦发银行"})

            result = get_business_rows({"RESULT_PATH": tmpdir}, "", label_lookup=lambda code: None)

            self.assertEqual(1, len(result.rows))
            self.assertNotIn("labels", result.rows[0])


if __name__ == "__main__":
    unittest.main()
