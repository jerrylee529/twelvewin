# -*- coding: utf-8 -*-

"""Published artifact freshness and job run status."""

import json

from sqlalchemy.orm import Session

from api.db.models import AnalysisJobRun, AnalysisRun
from api.services.published_results import get_latest_analysis_run
from core.artifacts import STOCK_RANKING_FILES, TECHNICAL_ANALYSIS_FILES

TRACKED_JOBS = ('eod_all', 'daily_pipeline', 'ranking_pipeline')

TRACKED_DB_ARTIFACTS = {
    'rankings': {
        key: (AnalysisRun.CATEGORY_RANKING, key)
        for key in STOCK_RANKING_FILES
    },
    'technical': {
        key: (AnalysisRun.CATEGORY_TECHNICAL, key)
        for key in TECHNICAL_ANALYSIS_FILES
    },
    'business': {
        'business': (AnalysisRun.CATEGORY_RANKING, 'business'),
    },
    'price_change': {
        'price_change': (AnalysisRun.CATEGORY_PRICE_CHANGE, 'price_change'),
    },
}


def _deserialize_json_field(value):
    if value in (None, ''):
        return None
    if isinstance(value, dict):
        return value
    return json.loads(value)


def serialize_job_run(job_run):
    if job_run is None:
        return None

    return {
        'job_name': job_run.job_name,
        'status': job_run.status,
        'parameters': _deserialize_json_field(job_run.parameters),
        'output': _deserialize_json_field(job_run.output),
        'error': _deserialize_json_field(job_run.error),
        'started_at': job_run.started_at.isoformat(sep=' ') if job_run.started_at else None,
        'finished_at': job_run.finished_at.isoformat(sep=' ') if job_run.finished_at else None,
        'duration_seconds': job_run.duration_seconds,
    }


def _db_artifact_status(session: Session, category: str, result_key: str):
    run = get_latest_analysis_run(session, category, result_key)
    if run is None or run.row_count == 0:
        return {
            'result_key': result_key,
            'category': category,
            'exists': False,
            'update_time': None,
            'row_count': 0,
        }

    return {
        'result_key': result_key,
        'category': category,
        'exists': True,
        'update_time': run.as_of_date.strftime('%Y-%m-%d'),
        'row_count': run.row_count,
        'source_file': run.source_file,
    }


def get_data_status(session: Session) -> dict:
    artifacts = {}
    for group_name, mapping in TRACKED_DB_ARTIFACTS.items():
        artifacts[group_name] = {
            key: _db_artifact_status(session, category, result_key)
            for key, (category, result_key) in mapping.items()
        }

    jobs = {}
    for job_name in TRACKED_JOBS:
        job_run = (
            session.query(AnalysisJobRun)
            .filter_by(job_name=job_name)
            .order_by(AnalysisJobRun.started_at.desc())
            .first()
        )
        jobs[job_name] = serialize_job_run(job_run)

    return {
        'artifacts': artifacts,
        'jobs': jobs,
    }
