# -*- coding: utf-8 -*-

"""Job runner with DB-backed tracking (no Flask app or request context)."""

import logging
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple

from core import job_run as job_run_service
from core.db import session_scope
from core.schema import ensure_analysis_schema

logger = logging.getLogger(__name__)

Step = Tuple[str, Callable[[], Any]]


class JobRunner:
    def __init__(self, job_name: str):
        self.job_name = job_name

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
                job_run_service.mark_success(job_run, output=output, session=session)
                return output
            except Exception as exc:
                job_run_service.mark_failure(
                    job_run,
                    error={
                        'message': str(exc),
                        'type': type(exc).__name__,
                        'traceback': traceback.format_exc(),
                        'completed_steps': list(step_outputs.keys()),
                    },
                    session=session,
                )
                session.commit()
                raise
