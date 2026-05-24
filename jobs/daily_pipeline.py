# -*- coding: utf-8 -*-

"""End-of-day analysis pipeline with job run tracking."""

import logging
import os
import sys

from jobs.base import JobRunner
from jobs.config import config_get, load_service_config

logger = logging.getLogger(__name__)

DAILY_PIPELINE_JOB = "daily_pipeline"


def _ensure_analysis_path() -> str:
    analysis_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "analysis"))
    if analysis_dir not in sys.path:
        sys.path.insert(0, analysis_dir)
    return analysis_dir


def _step_update_instruments(config) -> dict:
    _ensure_analysis_path()
    from instruments import get_instrument_list

    frame = get_instrument_list()
    if frame is None:
        return {"status": "skipped", "reason": "no instrument list available"}
    return {
        "status": "ok",
        "provider": frame.attrs.get("provider"),
        "rows": len(frame),
    }


def _step_download_history(config) -> dict:
    _ensure_analysis_path()
    from history_data_service import HistoryDataService

    service = HistoryDataService()
    service.run()
    return {"status": "ok"}


def _step_technical_screens(config) -> dict:
    _ensure_analysis_path()
    from technical_analysis_service import run_all_technical_screens

    instrument_filename = config_get(config, "INSTRUMENT_FILENAME")
    day_file_path = config_get(config, "DAY_FILE_PATH")
    result_file_path = config_get(config, "RESULT_PATH") or config_get(config, "RESULT_FILE_PATH")

    published = run_all_technical_screens(
        instrument_filename,
        day_file_path,
        result_file_path,
    )

    return {
        "status": "ok",
        "published": sorted(published.keys()),
    }


def _step_price_change(config) -> dict:
    _ensure_analysis_path()
    from technical_analysis_service import price_change_computer

    instrument_filename = config_get(config, "INSTRUMENT_FILENAME")
    day_file_path = config_get(config, "DAY_FILE_PATH")
    result_file_path = config_get(config, "RESULT_PATH") or config_get(config, "RESULT_FILE_PATH")

    price_change_computer(instrument_filename, day_file_path, result_file_path)
    return {"status": "ok", "published": ["price_change"]}


def build_daily_pipeline_steps(config):
    return [
        ("update_instruments", lambda: _step_update_instruments(config)),
        ("download_history", lambda: _step_download_history(config)),
        ("technical_screens", lambda: _step_technical_screens(config)),
        ("price_change", lambda: _step_price_change(config)),
    ]


def run_daily_pipeline(service_config=None) -> dict:
    config = service_config or load_service_config()
    runner = JobRunner(DAILY_PIPELINE_JOB)
    return runner.run_steps(
        build_daily_pipeline_steps(config),
        parameters={
            "day_file_path": config_get(config, "DAY_FILE_PATH"),
            "result_path": config_get(config, "RESULT_PATH") or config_get(config, "RESULT_FILE_PATH"),
        },
    )
