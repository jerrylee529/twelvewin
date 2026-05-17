# -*- coding: utf-8 -*-

import csv
import os
import tempfile
import unittest

from app.services.market_data_service import get_candlestick_data


class MarketDataServiceTestCase(unittest.TestCase):
    def test_get_candlestick_data_reads_day_csv_and_appends_realtime_quote(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "600000.csv")
            with open(path, "w", encoding="utf-8", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["date", "open", "close", "low", "high"])
                writer.writeheader()
                writer.writerow({
                    "date": "2026-05-16",
                    "open": "10",
                    "close": "11",
                    "low": "9",
                    "high": "12",
                })

            def quote_provider(code):
                self.assertEqual("600000", code)
                return {
                    "update_time": "2026-05-17 15:00:00",
                    "open": "11",
                    "trade": "12",
                    "low": "10",
                    "high": "13",
                }

            result = get_candlestick_data(
                {"DAY_FILE_PATH": tmpdir},
                "600000",
                quote_provider=quote_provider,
            )

            self.assertIsNone(result.error)
            self.assertEqual([
                ["2026-05-16", 10.0, 11.0, 9.0, 12.0],
                ["2026-05-17", 11.0, 12.0, 10.0, 13.0],
            ], result.rows)

    def test_get_candlestick_data_skips_invalid_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "600000.csv")
            with open(path, "w", encoding="utf-8", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["date", "open", "close", "low", "high"])
                writer.writeheader()
                writer.writerow({
                    "date": "2026-05-16",
                    "open": "bad",
                    "close": "11",
                    "low": "9",
                    "high": "12",
                })

            result = get_candlestick_data({"DAY_FILE_PATH": tmpdir}, "600000")

            self.assertEqual([], result.rows)


if __name__ == "__main__":
    unittest.main()
