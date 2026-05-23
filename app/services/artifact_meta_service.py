# -*- coding: utf-8 -*-

"""Lookup update times for generated CSV artifacts shown in the UI."""

from app.models import AnalysisRun
from app.services.analysis_artifacts import STOCK_RANKING_FILES, TECHNICAL_ANALYSIS_FILES
from app.services.result_store_service import get_latest_analysis_run

FILTER_SCREEN_FILE = "price_change.csv"


def _update_time_from_analysis_run(category, result_key):
    run = get_latest_analysis_run(category, result_key)
    if run is not None:
        return run.as_of_date.strftime("%Y-%m-%d")
    return None


def get_artifact_update_time(config, *, ranking_key=None, technical_key=None, filename=None):
    if ranking_key == "business":
        db_time = _update_time_from_analysis_run(AnalysisRun.CATEGORY_RANKING, "business")
        if db_time:
            return db_time
    elif ranking_key is not None:
        db_time = _update_time_from_analysis_run(AnalysisRun.CATEGORY_RANKING, ranking_key)
        if db_time:
            return db_time
    elif technical_key == "filter":
        db_time = _update_time_from_analysis_run(AnalysisRun.CATEGORY_PRICE_CHANGE, "price_change")
        if db_time:
            return db_time
    elif technical_key is not None:
        db_time = _update_time_from_analysis_run(AnalysisRun.CATEGORY_TECHNICAL, technical_key)
        if db_time:
            return db_time

    return None
