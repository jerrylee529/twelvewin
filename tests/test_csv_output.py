# -*- coding: utf-8 -*-

import csv
import os
import sys
import tempfile
import unittest

ANALYSIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "analysis"))
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)

from csv_output import atomic_export_pair


class CsvOutputTestCase(unittest.TestCase):
    def test_atomic_export_pair_writes_dated_and_stable_files(self):
        class FakeDataFrame:
            def to_csv(self, path, **kwargs):
                with open(path, "w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=["code", "name"])
                    writer.writeheader()
                    writer.writerow({"code": "000001", "name": "Ping An"})

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = atomic_export_pair(
                FakeDataFrame(),
                tmpdir,
                "stock_pe",
                date_suffix="20260519",
                index=False,
            )

            self.assertEqual(2, len(paths))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "stock_pe_20260519.csv")))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "stock_pe.csv")))


if __name__ == "__main__":
    unittest.main()
