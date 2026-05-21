# -*- coding: utf-8 -*-

import csv
import os
import tempfile
import unittest

try:
    import pandas as pd
except ImportError:
    pd = None

from jobs.io import (
    atomic_append_dataframe_to_csv,
    atomic_dataframe_to_csv,
    atomic_write_file,
    validate_csv_columns,
)


class AtomicCsvTestCase(unittest.TestCase):
    def test_atomic_write_file_replaces_target_on_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            final_path = os.path.join(tmpdir, "stock_pe.csv")

            def _write(path):
                with open(path, "w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=["code", "name"])
                    writer.writeheader()
                    writer.writerow({"code": "000001", "name": "Ping An"})

            atomic_write_file(final_path, _write, required_columns=["code", "name"])

            self.assertTrue(os.path.exists(final_path))
            self.assertFalse(os.path.exists(final_path + ".tmp"))
            with open(final_path, encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(1, len(rows))

    def test_atomic_write_file_does_not_replace_target_on_validation_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            final_path = os.path.join(tmpdir, "stock_pe.csv")
            with open(final_path, "w", encoding="utf-8") as handle:
                handle.write("code,name\n000001,Ping An\n")

            def _write(path):
                with open(path, "w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=["code"])
                    writer.writeheader()
                    writer.writerow({"code": "000001"})

            with self.assertRaises(ValueError):
                atomic_write_file(final_path, _write, required_columns=["code", "name"])

            with open(final_path, encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual("000001", rows[0]["code"])
            self.assertEqual("Ping An", rows[0]["name"])

    def test_atomic_dataframe_to_csv_writes_expected_rows(self):
        class FakeDataFrame:
            def to_csv(self, path, **kwargs):
                with open(path, "w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=["code", "name", "close"])
                    writer.writeheader()
                    writer.writerow({"code": "000001", "name": "Ping An", "close": "10.5"})

        with tempfile.TemporaryDirectory() as tmpdir:
            final_path = os.path.join(tmpdir, "highest_in_history.csv")

            atomic_dataframe_to_csv(
                FakeDataFrame(),
                final_path,
                required_columns=["code", "name", "close"],
                index=False,
                float_format="%.2f",
            )

            validate_csv_columns(final_path, ["code", "name", "close"])


    @unittest.skipUnless(pd is not None, "pandas not installed")
    def test_atomic_append_dataframe_preserves_existing_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "000001.csv")
            pd.DataFrame([{"code": "000001", "close": 10.0}]).to_csv(path, index=False)
            new_rows = pd.DataFrame([{"code": "000001", "close": 10.5}])

            atomic_append_dataframe_to_csv(path, new_rows, index=False)

            merged = pd.read_csv(path)
            self.assertEqual(2, len(merged))

    @unittest.skipUnless(pd is not None, "pandas not installed")
    def test_atomic_append_creates_file_when_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "000002.csv")
            new_rows = pd.DataFrame([{"code": "000002", "close": 10.0}])
            atomic_append_dataframe_to_csv(path, new_rows, index=False)
            self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
