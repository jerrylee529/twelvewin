# -*- coding: utf-8 -*-

"""Helpers for recording offline analysis job runs (Flask session adapter)."""

from app import db
from core import job_run as _core_job_run


def deserialize_json_field(value):
    return _core_job_run.deserialize_json_field(value)


def start_job(job_name, *, parameters=None, session=None):
    session = session or db.session
    return _core_job_run.start_job(job_name, parameters=parameters, session=session)


def mark_success(job_run, *, output=None, session=None):
    session = session or db.session
    return _core_job_run.mark_success(job_run, output=output, session=session)


def mark_failure(job_run, *, error=None, session=None):
    session = session or db.session
    return _core_job_run.mark_failure(job_run, error=error, session=session)


def get_latest_run(job_name, *, session=None):
    session = session or db.session
    from app.models import AnalysisJobRun

    return (
        session.query(AnalysisJobRun)
        .filter_by(job_name=job_name)
        .order_by(AnalysisJobRun.started_at.desc())
        .first()
    )


def list_recent_runs(job_name, *, limit=10, session=None):
    session = session or db.session
    from app.models import AnalysisJobRun

    return (
        session.query(AnalysisJobRun)
        .filter_by(job_name=job_name)
        .order_by(AnalysisJobRun.started_at.desc())
        .limit(limit)
        .all()
    )


def serialize_job_run(job_run):
    return _core_job_run.serialize_job_run(job_run)
