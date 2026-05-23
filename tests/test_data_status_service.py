# -*- coding: utf-8 -*-

import datetime
import unittest
from unittest import mock

from app.models import AnalysisJobRun, AnalysisRun
from app.services.data_status_service import get_data_status


class DataStatusServiceTestCase(unittest.TestCase):
    def test_get_data_status_reads_db_artifacts_and_jobs(self):
        job_run = AnalysisJobRun("daily_pipeline")
        job_run.status = AnalysisJobRun.STATUS_SUCCESS

        pe_run = AnalysisRun(
            AnalysisRun.CATEGORY_RANKING,
            "pe",
            datetime.date(2026, 5, 21),
            row_count=2,
            source_file="stock_pe.csv",
        )

        with mock.patch(
            "app.services.data_status_service.get_latest_run",
            return_value=job_run,
        ), mock.patch(
            "app.services.data_status_service.get_latest_analysis_run",
            return_value=pe_run,
        ):
            status = get_data_status({})

        self.assertIn("rankings", status["artifacts"])
        self.assertTrue(status["artifacts"]["rankings"]["pe"]["exists"])
        self.assertEqual("2026-05-21", status["artifacts"]["rankings"]["pe"]["update_time"])
        self.assertEqual("success", status["jobs"]["daily_pipeline"]["status"])


if __name__ == "__main__":
    unittest.main()
