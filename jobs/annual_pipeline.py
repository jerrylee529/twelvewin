# -*- coding: utf-8 -*-

"""Annual stock/industry report pipeline (publishes to Postgres)."""

import logging
import os
import sys
from datetime import date

from jobs.base import JobRunner
from jobs.config import load_service_config

logger = logging.getLogger(__name__)

ANNUAL_PIPELINE_JOB = 'annual_pipeline'


def _ensure_analysis_path():
    analysis_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
    if analysis_dir not in sys.path:
        sys.path.insert(0, analysis_dir)
    return analysis_dir


def _report_year():
    raw = os.environ.get('TW_ANNUAL_REPORT_YEAR', '')
    if raw:
        return int(raw)
    return date.today().year


def _step_annual_reports(config) -> dict:
    _ensure_analysis_path()
    from annual_report import compute

    return compute(year=_report_year())


def build_annual_pipeline_steps(config):
    return [
        ('annual_reports', lambda: _step_annual_reports(config)),
    ]


def run_annual_pipeline(service_config=None) -> dict:
    config = service_config or load_service_config()
    runner = JobRunner(ANNUAL_PIPELINE_JOB)
    return runner.run_steps(
        build_annual_pipeline_steps(config),
        parameters={'year': _report_year()},
    )
