# -*- coding: utf-8 -*-

import csv
import os
import tempfile
import unittest

from app.services.csv_store import convert_fields, read_rows, resolve_under_base


class CsvStoreTestCase(unittest.TestCase):
    def test_read_rows_adds_id_update_time_and_honors_limit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "ranking.csv")
            with open(path, "w", encoding="utf-8", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["code", "rate"])
                writer.writeheader()
                writer.writerow({"code": "600000", "rate": "1.25"})
                writer.writerow({"code": "000001", "rate": "2.50"})

            result = read_rows(
                tmpdir,
                "ranking.csv",
                add_id=True,
                add_update_time=True,
                max_rows=1,
            )

            self.assertFalse(result.missing)
            self.assertEqual(1, len(result.rows))
            self.assertEqual(1, result.rows[0]["id"])
            self.assertEqual("600000", result.rows[0]["code"])
            self.assertIn("updateTime", result.rows[0])

    def test_missing_file_returns_empty_result(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = read_rows(tmpdir, "missing.csv")

            self.assertTrue(result.missing)
            self.assertEqual([], result.rows)
            self.assertEqual("file not found", result.error)

    def test_resolve_under_base_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                resolve_under_base(tmpdir, "../outside.csv")

    def test_read_rows_rejects_path_traversal_as_empty_result(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = read_rows(tmpdir, "../outside.csv")

            self.assertEqual([], result.rows)
            self.assertIn("outside configured data directory", result.error)

    def test_convert_fields_skips_missing_and_empty_values(self):
        row = {"rate": "1.25", "empty": ""}

        result = convert_fields(row, [("rate", float), ("empty", float), ("missing", float)])

        self.assertEqual(1.25, result["rate"])
        self.assertEqual("", result["empty"])


if __name__ == "__main__":
    unittest.main()
