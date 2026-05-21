# -*- coding: utf-8 -*-

"""Expose generated artifact freshness and job run status for the web UI."""

import logging
import os

from sqlalchemy.exc import SQLAlchemyError

from app.services.csv_store import format_mtime, resolve_under_base
from app.services.job_run_service import get_latest_run, serialize_job_run

logger = logging.getLogger(__name__)
from app.services.analysis_artifacts import STOCK_RANKING_FILES

TRACKED_JOBS = ("eod_all", "daily_pipeline", "ranking_pipeline")

TRACKED_RESULT_FILES = {
    "rankings": dict(STOCK_RANKING_FILES),
    "technical": {
        "highest_in_history": "highest_in_history.csv",
        "lowest_in_history": "lowest_in_history.csv",
        "ma_long": "ma_long.csv",
        "break_ma": "break_ma.csv",
        "above_ma": "above_ma.csv",
    },
    "business": {
        "business": "stock_business.csv",
    },
}


def _file_status(result_path, filename):
    try:
        path = resolve_under_base(result_path, filename)
    except ValueError as exc:
        return {"filename": filename, "exists": False, "error": str(exc)}

    return {
        "filename": filename,
        "path": path,
        "exists": os.path.exists(path),
        "update_time": format_mtime(path),
    }


def get_data_status(config):
    result_path = config.get("RESULT_PATH")
    files = {}

    for group_name, mapping in TRACKED_RESULT_FILES.items():
        files[group_name] = {
            key: _file_status(result_path, filename)
            for key, filename in mapping.items()
        }

    jobs = {}
    for job_name in TRACKED_JOBS:
        try:
            jobs[job_name] = serialize_job_run(get_latest_run(job_name))
        except SQLAlchemyError as exc:
            logger.warning("could not load job run for %s: %r", job_name, exc)
            jobs[job_name] = None

    return {
        "result_path": result_path,
        "files": files,
        "jobs": jobs,
    }
