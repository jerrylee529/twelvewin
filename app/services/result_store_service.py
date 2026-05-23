# -*- coding: utf-8 -*-

"""Import generated CSV artifacts into Postgres and read them back for the Web UI."""

import datetime
import json

from flask import has_app_context
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import AnalysisRun, RankingResult, TechnicalScreenResult
from app.services.csv_store import CsvReadResult, read_rows
from core.artifacts import (
    BUSINESS_RANKING_FILE,
    PRICE_CHANGE_FILE,
    STOCK_RANKING_FILES,
    TECHNICAL_ANALYSIS_FILES,
)


def read_analysis_from_db_enabled(config):
    from app.services.analysis_access import read_analysis_from_db_enabled as _enabled

    return _enabled(config)


def _parse_as_of_date(update_time):
    if not update_time:
        return datetime.date.today()
    try:
        return datetime.datetime.strptime(update_time, '%Y-%m-%d').date()
    except ValueError:
        return datetime.date.today()


def _serialize_row_payload(row, *, code_key='code', name_key='name'):
    payload = dict(row)
    payload.pop(code_key, None)
    payload.pop(name_key, None)
    payload.pop('id', None)
    payload.pop('updateTime', None)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _deserialize_row(result_model, *, update_time=None):
    row = {'code': result_model.code, 'name': result_model.name or ''}
    if result_model.data:
        try:
            row.update(json.loads(result_model.data))
        except json.JSONDecodeError:
            pass
    if update_time:
        row['updateTime'] = update_time
    return row


def get_latest_analysis_run(category, result_key):
    if not has_app_context():
        return None
    try:
        return (
            AnalysisRun.query.filter_by(category=category, result_key=result_key)
            .order_by(AnalysisRun.as_of_date.desc(), AnalysisRun.id.desc())
            .first()
        )
    except SQLAlchemyError:
        return None


def import_ranking_results(config, ranking_key, *, job_run_id=None):
    from compute.result_store import import_ranking_results as _import

    return _import(config, ranking_key, job_run_id=job_run_id)


def import_technical_screen_results(config, screen_key, *, job_run_id=None):
    from compute.result_store import import_technical_screen_results as _import

    return _import(config, screen_key, job_run_id=job_run_id)


def import_price_change_results(config, *, job_run_id=None):
    from compute.result_store import import_price_change_results as _import

    return _import(config, job_run_id=job_run_id)


def import_business_ranking_results(config, *, job_run_id=None):
    from compute.result_store import import_business_ranking_results as _import

    return _import(config, job_run_id=job_run_id)


def sync_all_results_to_db(config, *, job_run_id=None):
    """Import all known ranking and technical CSV files into the database."""
    from compute.result_store import sync_all_results_to_db as _sync

    return _sync(config, job_run_id=job_run_id)


def get_ranking_rows_from_db(ranking_key, *, max_rows=None):
    if not has_app_context():
        return None
    run = get_latest_analysis_run(AnalysisRun.CATEGORY_RANKING, ranking_key)
    if run is None or run.row_count == 0:
        return None

    query = RankingResult.query.filter_by(run_id=run.id).order_by(RankingResult.rank_order)
    if max_rows is not None:
        query = query.limit(max_rows)

    rows = []
    update_time = run.as_of_date.strftime('%Y-%m-%d')
    for item in query.all():
        row = _deserialize_row(item, update_time=update_time)
        row['id'] = item.rank_order
        rows.append(row)

    return CsvReadResult(
        rows=rows,
        path=run.source_file or '',
        update_time=update_time,
    )


def get_technical_rows_from_db(screen_key, *, max_rows=None):
    if not has_app_context():
        return None
    run = get_latest_analysis_run(AnalysisRun.CATEGORY_TECHNICAL, screen_key)
    if run is None or run.row_count == 0:
        return None

    query = TechnicalScreenResult.query.filter_by(run_id=run.id).order_by(
        TechnicalScreenResult.rank_order
    )
    if max_rows is not None:
        query = query.limit(max_rows)

    rows = []
    update_time = run.as_of_date.strftime('%Y-%m-%d')
    for item in query.all():
        row = _deserialize_row(item, update_time=update_time)
        row['id'] = item.rank_order
        rows.append(row)

    return CsvReadResult(
        rows=rows,
        path=run.source_file or '',
        update_time=update_time,
    )


def _get_published_rows_from_db(category, result_key, *, max_rows=None):
    if not has_app_context():
        return None
    run = get_latest_analysis_run(category, result_key)
    if run is None or run.row_count == 0:
        return None

    query = RankingResult.query.filter_by(run_id=run.id).order_by(RankingResult.rank_order)
    if max_rows is not None:
        query = query.limit(max_rows)

    rows = []
    update_time = run.as_of_date.strftime('%Y-%m-%d')
    for item in query.all():
        row = _deserialize_row(item, update_time=update_time)
        row['id'] = item.rank_order
        rows.append(row)

    return CsvReadResult(
        rows=rows,
        path=run.source_file or '',
        update_time=update_time,
    )


def get_annual_stock_rows_from_db(year, *, max_rows=None):
    return _get_published_rows_from_db(
        AnalysisRun.CATEGORY_ANNUAL_STOCK,
        str(year),
        max_rows=max_rows,
    )


def get_annual_industry_rows_from_db(year, *, max_rows=None):
    return _get_published_rows_from_db(
        AnalysisRun.CATEGORY_ANNUAL_INDUSTRY,
        str(year),
        max_rows=max_rows,
    )


def get_price_change_rows_from_db(*, max_rows=None):
    if not has_app_context():
        return None
    run = get_latest_analysis_run(AnalysisRun.CATEGORY_PRICE_CHANGE, 'price_change')
    if run is None or run.row_count == 0:
        return None

    query = TechnicalScreenResult.query.filter_by(run_id=run.id).order_by(
        TechnicalScreenResult.rank_order
    )
    if max_rows is not None:
        query = query.limit(max_rows)

    rows = []
    update_time = run.as_of_date.strftime('%Y-%m-%d')
    for item in query.all():
        row = _deserialize_row(item, update_time=update_time)
        row['id'] = item.rank_order
        rows.append(row)

    return CsvReadResult(
        rows=rows,
        path=run.source_file or '',
        update_time=update_time,
    )
