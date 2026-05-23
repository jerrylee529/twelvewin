# -*- coding: utf-8 -*-

"""Ensure phase-6 and job-tracking tables exist (compute-side, no Flask request)."""

import logging
import os

from sqlalchemy import inspect

from core.db import get_engine

logger = logging.getLogger(__name__)

REQUIRED_ANALYSIS_TABLES = (
    'analysis_job_run',
    'analysis_runs',
    'ranking_results',
    'technical_screen_results',
    'daily_bars',
    'fundamental_snapshots',
    'industry_fundamental_benchmarks',
)


def missing_analysis_tables(engine=None):
    engine = engine or get_engine()
    existing = set(inspect(engine).get_table_names())
    return [name for name in REQUIRED_ANALYSIS_TABLES if name not in existing]


def ensure_analysis_schema(engine=None):
    """Ensure analysis tables exist; prefer Alembic upgrade over ad-hoc create_all."""
    engine = engine or get_engine()
    missing = missing_analysis_tables(engine)
    if not missing:
        return False

    logger.warning(
        'Database missing analysis tables (%s); running flask db upgrade.',
        ', '.join(missing),
    )

    try:
        from flask_migrate import upgrade as migrate_upgrade

        os.environ.setdefault('TWELVEWIN_DISABLE_ANALYZER', '1')
        migrate_upgrade()
    except Exception as exc:
        logger.warning('flask db upgrade failed: %s', exc)

    still_missing = missing_analysis_tables(engine)
    if still_missing:
        raise RuntimeError(
            'Database schema incomplete. Missing tables: {}. '
            'Run: TWELVEWIN_DISABLE_ANALYZER=1 flask db upgrade'.format(
                ', '.join(still_missing)
            )
        )

    return True
