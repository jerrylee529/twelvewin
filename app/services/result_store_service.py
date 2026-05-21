# -*- coding: utf-8 -*-

"""Import generated CSV artifacts into Postgres and read them back for the Web UI."""

import datetime
import json

from flask import has_app_context
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import AnalysisRun, RankingResult, TechnicalScreenResult
from app.services.csv_store import CsvReadResult, read_rows
from app.services.analysis_artifacts import (
    BUSINESS_RANKING_FILE,
    PRICE_CHANGE_FILE,
    STOCK_RANKING_FILES,
    TECHNICAL_ANALYSIS_FILES,
)


def read_analysis_from_db_enabled(config):
    value = config.get('READ_ANALYSIS_FROM_DB', True)
    if isinstance(value, str):
        return value.lower() not in ('0', 'false', 'no', 'off')
    return bool(value)


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
    csv_filename = STOCK_RANKING_FILES.get(ranking_key)
    if csv_filename is None:
        return {'status': 'skipped', 'reason': 'unknown ranking key'}

    csv_result = read_rows(config['RESULT_PATH'], csv_filename)
    if csv_result.error or csv_result.missing:
        return {'status': 'skipped', 'reason': csv_result.error or 'file not found'}

    return _import_rows(
        AnalysisRun.CATEGORY_RANKING,
        ranking_key,
        csv_result,
        csv_filename,
        RankingResult,
        job_run_id=job_run_id,
    )


def import_technical_screen_results(config, screen_key, *, job_run_id=None):
    csv_filename = TECHNICAL_ANALYSIS_FILES.get(screen_key)
    if csv_filename is None:
        return {'status': 'skipped', 'reason': 'unknown technical key'}

    csv_result = read_rows(config['RESULT_PATH'], csv_filename)
    if csv_result.error or csv_result.missing:
        return {'status': 'skipped', 'reason': csv_result.error or 'file not found'}

    return _import_rows(
        AnalysisRun.CATEGORY_TECHNICAL,
        screen_key,
        csv_result,
        csv_filename,
        TechnicalScreenResult,
        job_run_id=job_run_id,
    )


def import_price_change_results(config, *, job_run_id=None):
    csv_result = read_rows(config['RESULT_PATH'], PRICE_CHANGE_FILE)
    if csv_result.error or csv_result.missing:
        return {'status': 'skipped', 'reason': csv_result.error or 'file not found'}

    return _import_rows(
        AnalysisRun.CATEGORY_PRICE_CHANGE,
        'price_change',
        csv_result,
        PRICE_CHANGE_FILE,
        TechnicalScreenResult,
        job_run_id=job_run_id,
    )


def import_business_ranking_results(config, *, job_run_id=None):
    csv_result = read_rows(config['RESULT_PATH'], BUSINESS_RANKING_FILE)
    if csv_result.error or csv_result.missing:
        return {'status': 'skipped', 'reason': csv_result.error or 'file not found'}

    return _import_rows(
        AnalysisRun.CATEGORY_RANKING,
        'business',
        csv_result,
        BUSINESS_RANKING_FILE,
        RankingResult,
        job_run_id=job_run_id,
    )


def _import_rows(category, result_key, csv_result, source_file, result_model, *, job_run_id=None):
    as_of_date = _parse_as_of_date(csv_result.update_time)
    run = AnalysisRun(
        category,
        result_key,
        as_of_date,
        row_count=len(csv_result.rows),
        source_file=source_file,
        job_run_id=job_run_id,
    )
    db.session.add(run)
    db.session.flush()

    objects = []
    for index, row in enumerate(csv_result.rows, start=1):
        code = str(row.get('code', '')).strip()
        if not code:
            continue
        objects.append(
            result_model(
                run.id,
                index,
                code,
                row.get('name'),
                _serialize_row_payload(row),
            )
        )

    if objects:
        db.session.bulk_save_objects(objects)

    run.row_count = len(objects)
    db.session.commit()

    return {
        'status': 'imported',
        'run_id': run.id,
        'category': category,
        'result_key': result_key,
        'row_count': run.row_count,
        'as_of_date': as_of_date.isoformat(),
    }


def sync_all_results_to_db(config, *, job_run_id=None):
    """Import all known ranking and technical CSV files into the database."""
    summary = {}

    for ranking_key in STOCK_RANKING_FILES:
        summary['ranking_' + ranking_key] = import_ranking_results(
            config, ranking_key, job_run_id=job_run_id
        )

    summary['ranking_business'] = import_business_ranking_results(
        config, job_run_id=job_run_id
    )

    for screen_key in TECHNICAL_ANALYSIS_FILES:
        summary['technical_' + screen_key] = import_technical_screen_results(
            config, screen_key, job_run_id=job_run_id
        )

    summary['price_change'] = import_price_change_results(
        config, job_run_id=job_run_id
    )

    return summary


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
