# -*- coding: utf-8 -*-

"""Ensure phase-6 and job-tracking tables exist (compute-side, no Flask request)."""

import logging

from sqlalchemy import inspect

from core.db import get_engine

logger = logging.getLogger(__name__)

REQUIRED_ANALYSIS_TABLES = (
    'analysis_job_run',
    'analysis_runs',
    'ranking_results',
    'technical_screen_results',
)


def missing_analysis_tables(engine=None):
    engine = engine or get_engine()
    existing = set(inspect(engine).get_table_names())
    return [name for name in REQUIRED_ANALYSIS_TABLES if name not in existing]


def ensure_analysis_schema(engine=None):
    """Create missing analysis tables from Flask-SQLAlchemy metadata."""
    engine = engine or get_engine()
    missing = missing_analysis_tables(engine)
    if not missing:
        return False

    logger.warning(
        'Database missing analysis tables (%s); creating from model metadata.',
        ', '.join(missing),
    )

    import app.models  # noqa: F401 — register all models
    from app import db

    tables = [
        db.metadata.tables[name]
        for name in missing
        if name in db.metadata.tables
    ]
    if tables:
        db.metadata.create_all(engine, tables=tables)

    still_missing = missing_analysis_tables(engine)
    if still_missing:
        raise RuntimeError(
            'Database schema incomplete. Missing tables: {}. '
            'Run: TWELVEWIN_DISABLE_ANALYZER=1 flask db upgrade'.format(
                ', '.join(still_missing)
            )
        )

    return True
