# -*- coding: utf-8 -*-

"""Job runner with DB-backed tracking (no Flask app or request context)."""

import logging
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple

from app.models import AnalysisJobRun
from core import job_run as job_run_service
from core.db import session_scope
from core.schema import ensure_analysis_schema

logger = logging.getLogger(__name__)

Step = Tuple[str, Callable[[], Any]]


class JobRunner:
    def __init__(self, job_name: str):
        self.job_name = job_name

    def _load_job_run(self, session, job_run_id: int) -> AnalysisJobRun:
        job_run = session.get(AnalysisJobRun, job_run_id)
        if job_run is None:
            raise RuntimeError('analysis job run {} not found'.format(job_run_id))
        return job_run

    def run_steps(
        self,
        steps: List[Step],
        *,
        parameters: Optional[dict] = None,
    ) -> dict:
        ensure_analysis_schema()
        step_outputs: Dict[str, Any] = {}

        with session_scope() as session:
            job_run = job_run_service.start_job(
                self.job_name,
                parameters=parameters,
                session=session,
            )
            job_run_id = job_run.id

        try:
            for step_name, step_fn in steps:
                logger.info('job %s: starting step %s', self.job_name, step_name)
                step_outputs[step_name] = step_fn()
                logger.info('job %s: finished step %s', self.job_name, step_name)

            output = {'steps': step_outputs}
            with session_scope() as session:
                job_run = self._load_job_run(session, job_run_id)
                job_run_service.mark_success(job_run, output=output, session=session)
            return output
        except Exception as exc:
            error_payload = {
                'message': str(exc),
                'type': type(exc).__name__,
                'traceback': traceback.format_exc(),
                'completed_steps': list(step_outputs.keys()),
            }
            try:
                with session_scope() as session:
                    job_run = self._load_job_run(session, job_run_id)
                    job_run_service.mark_failure(job_run, error=error_payload, session=session)
            except Exception:
                logger.exception(
                    'job %s: failed to persist failure status for run %s',
                    self.job_name,
                    job_run_id,
                )
            raise
