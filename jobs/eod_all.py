# -*- coding: utf-8 -*-

"""Run all end-of-day offline jobs in a single tracked pipeline."""

import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from jobs.base import JobRunner
from jobs.config import config_get, load_service_config
from jobs.daily_pipeline import build_daily_pipeline_steps
from jobs.ranking_pipeline import build_ranking_pipeline_steps

EOD_ALL_JOB = "eod_all"


def _step_sync_results_to_db(config) -> dict:
    from app.services.result_store_service import sync_all_results_to_db

    return sync_all_results_to_db(config)


def build_eod_all_steps(config):
    steps = build_daily_pipeline_steps(config) + build_ranking_pipeline_steps(config)
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
