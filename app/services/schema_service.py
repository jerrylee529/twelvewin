# -*- coding: utf-8 -*-

"""Ensure analysis-related DB tables exist before offline jobs run."""

import logging

from sqlalchemy import inspect

logger = logging.getLogger(__name__)

# Tables required by job tracking and phase-6 result import.
REQUIRED_ANALYSIS_TABLES = (
    'analysis_job_run',
    'analysis_runs',
    'ranking_results',
    'technical_screen_results',
)


def missing_analysis_tables(engine):
    existing = set(inspect(engine).get_table_names())
    return [name for name in REQUIRED_ANALYSIS_TABLES if name not in existing]


def ensure_analysis_schema():
    """Create missing analysis tables (upgrade first, then create_all fallback).

    Returns True if any schema action was applied.
    """
    from app import app, db, migrate

    with app.app_context():
        missing = missing_analysis_tables(db.engine)
        if not missing:
            return False

        logger.warning(
            'Database missing analysis tables (%s); applying schema.',
            ', '.join(missing),
        )

        db.create_all()

        missing = missing_analysis_tables(db.engine)
        if missing and migrate is not None:
            try:
                from flask_migrate import upgrade

                upgrade()
            except Exception as exc:
                logger.warning('flask db upgrade failed: %s', exc)

            missing = missing_analysis_tables(db.engine)
            if missing:
                db.create_all()

        missing = missing_analysis_tables(db.engine)
        if missing:
            raise RuntimeError(
                'Database schema incomplete. Missing tables: {}. '
                'Run: TWELVEWIN_DISABLE_ANALYZER=1 flask db upgrade'.format(
                    ', '.join(missing)
                )
            )

        return True
