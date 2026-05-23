# -*- coding: utf-8 -*-

import csv
import os
import tempfile
import unittest

from app.services.ranking_service import get_stock_ranking


class RankingServiceTestCase(unittest.TestCase):
    def test_get_stock_ranking_reads_known_ranking_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "stock_pe.csv")
            with open(path, "w", encoding="utf-8", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["code", "name"])
                writer.writeheader()
                writer.writerow({"code": "600000", "name": "浦发银行"})

            result = get_stock_ranking(
                {
                    "RESULT_PATH": tmpdir,
                    "CSV_DEV_FALLBACK": True,
                    "READ_ANALYSIS_FROM_DB": True,
                },
                "pe",
            )

            self.assertIsNone(result.error)
            self.assertEqual(1, len(result.rows))
            self.assertEqual(1, result.rows[0]["id"])
            self.assertEqual("600000", result.rows[0]["code"])

    def test_get_stock_ranking_rejects_unknown_key(self):
        result = get_stock_ranking({"RESULT_PATH": "/tmp"}, "unknown")

        self.assertEqual([], result.rows)
        self.assertEqual("unknown ranking key", result.error)


if __name__ == "__main__":
    unittest.main()
