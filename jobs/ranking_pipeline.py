# -*- coding: utf-8 -*-

"""Ranking and business-screen CSV generation with job run tracking."""

import logging
import sys

from jobs.base import JobRunner
from jobs.config import config_get, load_service_config

logger = logging.getLogger(__name__)

RANKING_PIPELINE_JOB = "ranking_pipeline"

RANKING_OUTPUT_FILES = (
    "stock_dividence.csv",
    "stock_roe.csv",
    "stock_pe.csv",
    "stock_pb.csv",
    "stock_value.csv",
    "stock_business.csv",
)


def _ensure_analysis_path():
    import os

    analysis_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "analysis"))
    if analysis_dir not in sys.path:
        sys.path.insert(0, analysis_dir)
    return analysis_dir


def _step_valuation_rankings(config) -> dict:
    _ensure_analysis_path()
    from getvaluation import get_profit_report

    get_profit_report()
    return {
        "status": "ok",
        "outputs": list(RANKING_OUTPUT_FILES[:5]),
    }


def _step_business_screen(config) -> dict:
    _ensure_analysis_path()
    from get_value_4_business import get_profit_report as get_business_report

    get_business_report()
    return {
        "status": "ok",
        "outputs": ["stock_business.csv"],
    }


def build_ranking_pipeline_steps(config):
    return [
        ("valuation_rankings", lambda: _step_valuation_rankings(config)),
        ("business_screen", lambda: _step_business_screen(config)),
    ]


def run_ranking_pipeline(service_config=None) -> dict:
    config = service_config or load_service_config()
    runner = JobRunner(RANKING_PIPELINE_JOB)
    return runner.run_steps(
        build_ranking_pipeline_steps(config),
        parameters={
            "result_path": config_get(config, "RESULT_PATH") or config_get(config, "RESULT_FILE_PATH"),
        },
    )
