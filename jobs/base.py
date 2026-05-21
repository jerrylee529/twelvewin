# -*- coding: utf-8 -*-

"""Base job runner with DB-backed run tracking."""

import logging
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple

from app import app
from app.services.job_run_service import mark_failure, mark_success, start_job
from app.services.schema_service import ensure_analysis_schema

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
        with app.app_context():
            ensure_analysis_schema()
            job_run = start_job(self.job_name, parameters=parameters)
            step_outputs: Dict[str, Any] = {}

            try:
                for step_name, step_fn in steps:
                    logger.info("job %s: starting step %s", self.job_name, step_name)
                    step_outputs[step_name] = step_fn()
                    logger.info("job %s: finished step %s", self.job_name, step_name)

                output = {"steps": step_outputs}
                mark_success(job_run, output=output)
                return output
            except Exception as exc:
                mark_failure(
                    job_run,
                    error={
                        "message": str(exc),
                        "type": type(exc).__name__,
                        "traceback": traceback.format_exc(),
                        "completed_steps": list(step_outputs.keys()),
                    },
                )
                raise
