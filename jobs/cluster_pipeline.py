# -*- coding: utf-8 -*-

"""Precompute stock clusters into stock_cluster / stock_cluster_item tables."""

import logging
import sys

from jobs.base import JobRunner
from jobs.config import config_get, load_service_config

logger = logging.getLogger(__name__)

CLUSTER_PIPELINE_JOB = 'cluster_pipeline'


def _ensure_analysis_path():
    import os

    analysis_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
    if analysis_dir not in sys.path:
        sys.path.insert(0, analysis_dir)
    return analysis_dir


def _step_run_clusters(config) -> dict:
    _ensure_analysis_path()
    from cluster_compute import run_cluster_pipeline

    return run_cluster_pipeline(
        day_file_path=config_get(config, 'DAY_FILE_PATH'),
        index_file_path=config_get(config, 'INDEX_FILE_PATH')
        or config_get(config, 'DAY_FILE_PATH'),
    )


def build_cluster_pipeline_steps(config):
    return [
        ('cluster_sections', lambda: _step_run_clusters(config)),
    ]


def run_cluster_pipeline(service_config=None) -> dict:
    config = service_config or load_service_config()
    runner = JobRunner(CLUSTER_PIPELINE_JOB)
    return runner.run_steps(
        build_cluster_pipeline_steps(config),
        parameters={
            'day_file_path': config_get(config, 'DAY_FILE_PATH'),
            'index_file_path': config_get(config, 'INDEX_FILE_PATH'),
        },
    )
