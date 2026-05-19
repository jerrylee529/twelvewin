# -*- coding: utf-8 -*-

import tempfile
import unittest

from app import app


class AppSmokeTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        self.client = app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(200, response.status_code)

    def test_missing_stock_ranking_csv_returns_empty_result(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_result_path = app.config["RESULT_PATH"]
            app.config["RESULT_PATH"] = tmpdir
            try:
                response = self.client.get("/pe/data")
            finally:
                app.config["RESULT_PATH"] = old_result_path

        self.assertEqual(200, response.status_code)
        self.assertEqual({"rows": [], "total": 0}, response.get_json())

    def test_data_status_endpoint_returns_files_and_jobs(self):
        response = self.client.get("/main/data_status")

        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertIn("files", payload)
        self.assertIn("jobs", payload)
        self.assertIn("daily_pipeline", payload["jobs"])
        self.assertIsNone(payload["jobs"]["daily_pipeline"])


if __name__ == "__main__":
    unittest.main()
