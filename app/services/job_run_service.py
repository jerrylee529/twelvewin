# -*- coding: utf-8 -*-

"""Helpers for recording offline analysis job runs."""

import datetime
import json

from app import db
from app.models import AnalysisJobRun


def _serialize(value):
    if value is None or isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def deserialize_json_field(value):
    if value in (None, ""):
        return None
    if isinstance(value, dict):
        return value
    return json.loads(value)


def _finish(job_run, status, *, output=None, error=None):
    now = datetime.datetime.now()
    job_run.status = status
    job_run.output = _serialize(output)
    job_run.error = _serialize(error)
    job_run.finished_at = now
    job_run.duration_seconds = (now - job_run.started_at).total_seconds()
    job_run.update_time = now
    return job_run


def start_job(job_name, *, parameters=None, session=None):
    session = session or db.session
    job_run = AnalysisJobRun(job_name, parameters=_serialize(parameters))
    session.add(job_run)
    session.commit()
    return job_run


def mark_success(job_run, *, output=None, session=None):
    session = session or db.session
    _finish(job_run, AnalysisJobRun.STATUS_SUCCESS, output=output)
    session.add(job_run)
    session.commit()
    return job_run


def mark_failure(job_run, *, error=None, session=None):
    session = session or db.session
    _finish(job_run, AnalysisJobRun.STATUS_FAILED, error=error)
    session.add(job_run)
    session.commit()
    return job_run


def get_latest_run(job_name, *, session=None):
    session = session or db.session
    return (
        session.query(AnalysisJobRun)
        .filter_by(job_name=job_name)
        .order_by(AnalysisJobRun.started_at.desc())
        .first()
    )


def list_recent_runs(job_name, *, limit=10, session=None):
    session = session or db.session
    return (
        session.query(AnalysisJobRun)
        .filter_by(job_name=job_name)
        .order_by(AnalysisJobRun.started_at.desc())
        .limit(limit)
        .all()
    )


def serialize_job_run(job_run):
    if job_run is None:
        return None

    return {
        "job_name": job_run.job_name,
        "status": job_run.status,
        "parameters": deserialize_json_field(job_run.parameters),
        "output": deserialize_json_field(job_run.output),
        "error": deserialize_json_field(job_run.error),
        "started_at": job_run.started_at.isoformat(sep=" ") if job_run.started_at else None,
        "finished_at": job_run.finished_at.isoformat(sep=" ") if job_run.finished_at else None,
        "duration_seconds": job_run.duration_seconds,
    }
