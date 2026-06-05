# -*- coding: utf-8 -*-

"""Run all end-of-day offline jobs in a single tracked pipeline."""

import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from jobs.base import JobRunner
from jobs.config import config_get, load_service_config
from jobs.annual_pipeline import build_annual_pipeline_steps
from jobs.cluster_pipeline import build_cluster_pipeline_steps
from jobs.daily_pipeline import build_daily_pipeline_steps
from jobs.finance_profile_pipeline import build_finance_profile_pipeline_steps
from jobs.ranking_pipeline import build_ranking_pipeline_steps

EOD_ALL_JOB = "eod_all"


def _csv_sync_enabled():
    return os.environ.get('TW_SYNC_CSV_TO_DB', '').lower() in ('1', 'true', 'yes', 'on')


def _step_sync_results_to_db(config) -> dict:
    """Optional CSV→DB backfill when TW_WRITE_RESULT_CSV produced mirror files."""
    from compute.config import load_service_config_dict
    from compute.result_store import sync_all_results_to_db

    return sync_all_results_to_db(load_service_config_dict())


def _annual_report_enabled():
    return os.environ.get('TW_RUN_ANNUAL_REPORT', '').lower() in ('1', 'true', 'yes', 'on')


def _finance_profile_enabled():
    return os.environ.get('TW_RUN_FINANCE_PROFILE', '').lower() in ('1', 'true', 'yes', 'on')


def build_eod_all_steps(config):
    steps = build_daily_pipeline_steps(config) + build_ranking_pipeline_steps(config)
    steps += build_cluster_pipeline_steps(config)
    if _finance_profile_enabled():
        steps += build_finance_profile_pipeline_steps(config)
    if _annual_report_enabled():
        steps += build_annual_pipeline_steps(config)
    if _csv_sync_enabled():
        steps.append(("sync_results_to_db", lambda: _step_sync_results_to_db(config)))
    return steps


def run_eod_all(service_config=None) -> dict:
    config = service_config or load_service_config()
    runner = JobRunner(EOD_ALL_JOB)
    return runner.run_steps(
        build_eod_all_steps(config),
        parameters={
            "day_file_path": config_get(config, "DAY_FILE_PATH"),
            "result_path": config_get(config, "RESULT_PATH") or config_get(config, "RESULT_FILE_PATH"),
            "pipelines": ["daily_pipeline", "ranking_pipeline"],
        },
    )


if __name__ == "__main__":
    import logging

    os.environ.setdefault("TWELVEWIN_DISABLE_ANALYZER", "1")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    run_eod_all()
