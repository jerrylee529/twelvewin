# -*- coding: utf-8 -*-

"""Sync filing PDFs from Qiniu and extract text for AI analysis."""

import logging
import os
import sys

from jobs.base import JobRunner
from jobs.config import load_service_config

logger = logging.getLogger(__name__)

FILING_PIPELINE_JOB = 'filing_pipeline'


def _ensure_project_path():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    return project_root


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == '':
        return default
    return int(raw)


def _step_filing_sync(_config) -> dict:
    _ensure_project_path()
    from compute.filing_store import sync_filings_from_qiniu

    code = os.environ.get('TW_FILING_SYNC_CODE', '').strip() or None
    limit = _env_int('TW_FILING_SYNC_LIMIT', 0)
    return sync_filings_from_qiniu(code=code, limit=limit)


def _step_filing_extract(_config) -> dict:
    _ensure_project_path()
    from compute.filing_store import extract_pending_filings

    code = os.environ.get('TW_FILING_SYNC_CODE', '').strip() or None
    batch_size = _env_int('TW_FILING_EXTRACT_BATCH', 20)
    return extract_pending_filings(batch_size=batch_size, code=code)


def build_filing_pipeline_steps(config):
    return [
        ('filing_sync', lambda: _step_filing_sync(config)),
        ('filing_extract', lambda: _step_filing_extract(config)),
    ]


def run_filing_pipeline(service_config=None) -> dict:
    config = service_config or load_service_config()
    runner = JobRunner(FILING_PIPELINE_JOB)
    return runner.run_steps(
        build_filing_pipeline_steps(config),
        parameters={
            'code': os.environ.get('TW_FILING_SYNC_CODE', ''),
            'extract_batch': _env_int('TW_FILING_EXTRACT_BATCH', 20),
        },
    )
