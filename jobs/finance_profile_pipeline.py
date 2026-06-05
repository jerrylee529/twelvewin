# -*- coding: utf-8 -*-

"""Sync annual finance profile metrics from Tushare into Postgres."""

import logging
import os
import sys

from jobs.base import JobRunner
from jobs.config import load_service_config

logger = logging.getLogger(__name__)

FINANCE_PROFILE_PIPELINE_JOB = 'finance_profile_pipeline'


def _ensure_analysis_path():
    analysis_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
    if analysis_dir not in sys.path:
        sys.path.insert(0, analysis_dir)
    return analysis_dir


def _step_sync_finance_profiles(_config) -> dict:
    from compute.finance_profile_store import sync_finance_profiles

    return sync_finance_profiles()


def build_finance_profile_pipeline_steps(config):
    return [
        ('sync_finance_profiles', lambda: _step_sync_finance_profiles(config)),
    ]


def run_finance_profile_pipeline(service_config=None) -> dict:
    config = service_config or load_service_config()
    runner = JobRunner(FINANCE_PROFILE_PIPELINE_JOB)
    return runner.run_steps(
        build_finance_profile_pipeline_steps(config),
        parameters={
            'years': os.environ.get('TW_FINANCE_PROFILE_YEARS', '5'),
            'max_codes': os.environ.get('TW_FINANCE_PROFILE_MAX_CODES', '0'),
        },
    )


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )
    os.environ.setdefault('TWELVEWIN_DISABLE_ANALYZER', '1')
    run_finance_profile_pipeline()
