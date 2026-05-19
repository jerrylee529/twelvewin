# -*- coding: utf-8 -*-

import os
import tempfile
import unittest
from unittest import mock

from app.models import AnalysisJobRun
from app.services.data_status_service import get_data_status


class DataStatusServiceTestCase(unittest.TestCase):
    def test_get_data_status_includes_file_and_job_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "stock_pe.csv")
            with open(csv_path, "w", encoding="utf-8") as handle:
                handle.write("code,name,pe\n000001,Ping An,10.5\n")

            job_run = AnalysisJobRun("daily_pipeline")
            job_run.status = AnalysisJobRun.STATUS_SUCCESS

            with mock.patch(
                "app.services.data_status_service.get_latest_run",
                return_value=job_run,
            ):
                status = get_data_status({"RESULT_PATH": tmpdir})

        self.assertEqual(tmpdir, status["result_path"])
        self.assertIn("rankings", status["files"])
        self.assertTrue(status["files"]["rankings"]["pe"]["exists"])
        self.assertEqual("success", status["jobs"]["daily_pipeline"]["status"])


if __name__ == "__main__":
    unittest.main()
