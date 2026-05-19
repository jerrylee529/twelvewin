# -*- coding: utf-8 -*-

import json
import unittest

from app.models import AnalysisJobRun
from app.services.job_run_service import (
    get_latest_run,
    mark_failure,
    mark_success,
    serialize_job_run,
    start_job,
)


class FakeQuery:
    def __init__(self, rows):
        self._rows = rows

    def filter_by(self, **kwargs):
        return self

    def order_by(self, *args):
        return self

    def first(self):
        return self._rows[0] if self._rows else None

    def limit(self, count):
        self._limit = count
        return self

    def all(self):
        return self._rows[: self._limit]


class FakeSession:
    def __init__(self, rows=None):
        self.added = []
        self.commit_count = 0
        self.rows = rows or []

    def add(self, item):
        self.added.append(item)

    def commit(self):
        self.commit_count += 1

    def query(self, model):
        return FakeQuery(self.rows)


class JobRunServiceTestCase(unittest.TestCase):
    def test_start_job_records_running_status_and_serialized_parameters(self):
        session = FakeSession()

        job_run = start_job("daily_history", parameters={"date": "2026-05-18"}, session=session)

        self.assertEqual(AnalysisJobRun.STATUS_RUNNING, job_run.status)
        self.assertEqual("daily_history", job_run.job_name)
        self.assertEqual({"date": "2026-05-18"}, json.loads(job_run.parameters))
        self.assertEqual([job_run], session.added)
        self.assertEqual(1, session.commit_count)

    def test_mark_success_records_output_and_duration(self):
        session = FakeSession()
        job_run = AnalysisJobRun("technical_screens")

        mark_success(job_run, output={"rows": 10}, session=session)

        self.assertEqual(AnalysisJobRun.STATUS_SUCCESS, job_run.status)
        self.assertEqual({"rows": 10}, json.loads(job_run.output))
        self.assertIsNone(job_run.error)
        self.assertIsNotNone(job_run.finished_at)
        self.assertGreaterEqual(job_run.duration_seconds, 0)
        self.assertEqual(1, session.commit_count)

    def test_mark_failure_records_error_and_duration(self):
        session = FakeSession()
        job_run = AnalysisJobRun("technical_screens")

        mark_failure(job_run, error={"message": "failed"}, session=session)

        self.assertEqual(AnalysisJobRun.STATUS_FAILED, job_run.status)
        self.assertEqual({"message": "failed"}, json.loads(job_run.error))
        self.assertIsNone(job_run.output)
        self.assertIsNotNone(job_run.finished_at)
        self.assertGreaterEqual(job_run.duration_seconds, 0)
        self.assertEqual(1, session.commit_count)

    def test_get_latest_run_returns_first_ordered_row(self):
        older = AnalysisJobRun("daily_pipeline")
        newer = AnalysisJobRun("daily_pipeline")
        session = FakeSession(rows=[newer, older])

        latest = get_latest_run("daily_pipeline", session=session)

        self.assertIs(newer, latest)

    def test_serialize_job_run_exposes_status_and_timestamps(self):
        job_run = AnalysisJobRun("daily_pipeline")
        job_run.status = AnalysisJobRun.STATUS_RUNNING

        payload = serialize_job_run(job_run)

        self.assertEqual("daily_pipeline", payload["job_name"])
        self.assertEqual("running", payload["status"])
        self.assertIsNotNone(payload["started_at"])

    def test_analysis_job_run_table_is_registered_in_metadata(self):
        self.assertIn("analysis_job_run", AnalysisJobRun.metadata.tables)


if __name__ == "__main__":
    unittest.main()
