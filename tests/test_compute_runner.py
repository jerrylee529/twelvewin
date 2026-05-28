# -*- coding: utf-8 -*-

import os
import sys
import unittest
from unittest import mock

os.environ.setdefault('TWELVEWIN_DISABLE_ANALYZER', '1')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from compute.runner import JobRunner


class FakeJobRun:
    def __init__(self, job_run_id):
        self.id = job_run_id


class SessionScopeContext:
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeSession:
    def __init__(self, job_run):
        self.job_run = job_run
        self.get_calls = 0

    def get(self, model, job_run_id):
        self.get_calls += 1
        return self.job_run


class ComputeRunnerTestCase(unittest.TestCase):
    def test_failure_is_persisted_with_fresh_session(self):
        job_run = FakeJobRun(job_run_id=18)
        start_session = FakeSession(job_run)
        failure_session = FakeSession(job_run)
        sessions = iter([start_session, failure_session])

        def fake_session_scope():
            return SessionScopeContext(next(sessions))

        runner = JobRunner('eod_all')

        with mock.patch('compute.runner.ensure_analysis_schema'):
            with mock.patch('compute.runner.session_scope', side_effect=fake_session_scope):
                with mock.patch('compute.runner.job_run_service.start_job', return_value=job_run):
                    with mock.patch('compute.runner.job_run_service.mark_failure') as mark_failure:
                        with self.assertRaises(RuntimeError):
                            runner.run_steps([
                                ('ok_step', lambda: {'status': 'ok'}),
                                ('bad_step', lambda: (_ for _ in ()).throw(RuntimeError('boom'))),
                            ])

        mark_failure.assert_called_once()
        self.assertIs(failure_session, mark_failure.call_args.kwargs['session'])
        self.assertEqual(1, failure_session.get_calls)


if __name__ == '__main__':
    unittest.main()
