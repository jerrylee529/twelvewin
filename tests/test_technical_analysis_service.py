# -*- coding: utf-8 -*-

import csv
import os
import tempfile
import unittest

from app.services.technical_analysis_service import get_price_change_rows, get_technical_rows


class TechnicalAnalysisServiceTestCase(unittest.TestCase):
    def test_get_technical_rows_reads_known_screen(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "highest_in_history.csv")
            with open(path, "w", encoding="utf-8", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["code", "close"])
                writer.writeheader()
                writer.writerow({"code": "600000", "close": "12.30"})

            result = get_technical_rows(
                {
                    "RESULT_PATH": tmpdir,
                    "CSV_DEV_FALLBACK": True,
                    "READ_ANALYSIS_FROM_DB": True,
                },
                "highest",
            )

            self.assertIsNone(result.error)
            self.assertEqual(1, len(result.rows))
            self.assertEqual(1, result.rows[0]["id"])
            self.assertEqual("600000", result.rows[0]["code"])

    def test_get_technical_rows_rejects_unknown_screen(self):
        result = get_technical_rows({"RESULT_PATH": "/tmp"}, "unknown")

        self.assertEqual([], result.rows)
        self.assertEqual("unknown technical analysis key", result.error)

    def test_get_price_change_rows_filters_requested_range(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "price_change.csv")
            with open(path, "w", encoding="utf-8", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["code", "rate7", "rate30"])
                writer.writeheader()
                writer.writerow({"code": "600000", "rate7": "-5", "rate30": "2"})
                writer.writerow({"code": "000001", "rate7": "3", "rate30": "4"})

            result = get_price_change_rows(
                {
                    "RESULT_PATH": tmpdir,
                    "CSV_DEV_FALLBACK": True,
                    "READ_ANALYSIS_FROM_DB": True,
                },
                days=u"近一周",
                low=-10,
                high=0,
            )

            self.assertEqual(1, len(result.rows))
            self.assertEqual("600000", result.rows[0]["code"])
            self.assertEqual(-5.0, result.rows[0]["rate"])


if __name__ == "__main__":
    unittest.main()
