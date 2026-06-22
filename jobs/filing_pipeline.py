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


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw == '':
        return default
    return raw.lower() not in ('0', 'false', 'no', 'off')


def _filing_env() -> dict:
    resume = _env_bool('TW_FILING_RESUME', False)
    return {
        'code': os.environ.get('TW_FILING_SYNC_CODE', '').strip() or None,
        'sync_limit': _env_int('TW_FILING_SYNC_LIMIT', 0),
        'extract_batch': _env_int('TW_FILING_EXTRACT_BATCH', 20),
        'log_interval': _env_int('TW_FILING_LOG_INTERVAL', 0),
        'resume': resume,
        'skip_sync': _env_bool('TW_FILING_SKIP_SYNC', False),
        'extract_until_done': _env_bool('TW_FILING_EXTRACT_UNTIL_DONE', resume),
        'extract_max_rounds': _env_int('TW_FILING_EXTRACT_MAX_ROUNDS', 0),
    }


def _step_filing_sync(_config) -> dict:
    _ensure_project_path()
    from compute.filing_store import sync_filings_from_qiniu

    env = _filing_env()
    return sync_filings_from_qiniu(
        code=env['code'],
        limit=env['sync_limit'],
        resume=env['resume'],
        log_interval=env['log_interval'],
    )


def _step_filing_extract(_config) -> dict:
    _ensure_project_path()
    from compute.filing_store import (
        extract_pending_filings,
        extract_pending_filings_until_done,
    )

    env = _filing_env()
    if env['extract_until_done']:
        return extract_pending_filings_until_done(
            batch_size=env['extract_batch'],
            code=env['code'],
            max_rounds=env['extract_max_rounds'],
            reset_stuck=env['resume'],
        )

    return extract_pending_filings(
        batch_size=env['extract_batch'],
        code=env['code'],
    )


def build_filing_pipeline_steps(config):
    env = _filing_env()
    steps = []
    if not env['skip_sync']:
        steps.append(('filing_sync', lambda: _step_filing_sync(config)))
    else:
        logger.info('filing pipeline: skipping filing_sync (TW_FILING_SKIP_SYNC=1)')
    steps.append(('filing_extract', lambda: _step_filing_extract(config)))
    return steps


def run_filing_pipeline(service_config=None) -> dict:
    config = service_config or load_service_config()
    env = _filing_env()
    runner = JobRunner(FILING_PIPELINE_JOB)
    return runner.run_steps(
        build_filing_pipeline_steps(config),
        parameters={
            'code': env['code'] or '',
            'sync_limit': env['sync_limit'],
            'extract_batch': env['extract_batch'],
            'resume': env['resume'],
            'skip_sync': env['skip_sync'],
            'extract_until_done': env['extract_until_done'],
            'extract_max_rounds': env['extract_max_rounds'],
            'log_interval': env['log_interval'],
        },
    )
