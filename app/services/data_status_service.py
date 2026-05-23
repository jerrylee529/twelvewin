# -*- coding: utf-8 -*-

"""Expose published artifact freshness and job run status for the web UI."""

import logging

from sqlalchemy.exc import SQLAlchemyError

from app.models import AnalysisRun
from app.services.analysis_artifacts import STOCK_RANKING_FILES, TECHNICAL_ANALYSIS_FILES
from app.services.job_run_service import get_latest_run, serialize_job_run
from app.services.result_store_service import get_latest_analysis_run

logger = logging.getLogger(__name__)

TRACKED_JOBS = ("eod_all", "daily_pipeline", "ranking_pipeline")

TRACKED_DB_ARTIFACTS = {
    "rankings": {
        key: (AnalysisRun.CATEGORY_RANKING, key)
        for key in STOCK_RANKING_FILES
    },
    "technical": {
        key: (AnalysisRun.CATEGORY_TECHNICAL, key)
        for key in TECHNICAL_ANALYSIS_FILES
    },
    "business": {
        "business": (AnalysisRun.CATEGORY_RANKING, "business"),
    },
    "price_change": {
        "price_change": (AnalysisRun.CATEGORY_PRICE_CHANGE, "price_change"),
    },
}


def _db_artifact_status(category, result_key):
    run = get_latest_analysis_run(category, result_key)
    if run is None or run.row_count == 0:
        return {
            "result_key": result_key,
            "category": category,
            "exists": False,
            "update_time": None,
            "row_count": 0,
        }

    return {
        "result_key": result_key,
        "category": category,
        "exists": True,
        "update_time": run.as_of_date.strftime("%Y-%m-%d"),
        "row_count": run.row_count,
        "source_file": run.source_file,
    }


def get_data_status(config):
    artifacts = {}

    for group_name, mapping in TRACKED_DB_ARTIFACTS.items():
        artifacts[group_name] = {
            key: _db_artifact_status(category, result_key)
            for key, (category, result_key) in mapping.items()
        }

    jobs = {}
    for job_name in TRACKED_JOBS:
        try:
            jobs[job_name] = serialize_job_run(get_latest_run(job_name))
        except SQLAlchemyError as exc:
            logger.warning("could not load job run for %s: %r", job_name, exc)
            jobs[job_name] = None

    return {
        "artifacts": artifacts,
        "jobs": jobs,
    }
