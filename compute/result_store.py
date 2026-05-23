# -*- coding: utf-8 -*-

"""Import generated CSV artifacts into Postgres (compute-owned write path)."""

import datetime
import json

from core.artifacts import (
    BUSINESS_RANKING_FILE,
    PRICE_CHANGE_FILE,
    STOCK_RANKING_FILES,
    TECHNICAL_ANALYSIS_FILES,
    annual_industry_report_filename,
    annual_stock_report_filename,
)
from core.db import session_scope

from app.models import AnalysisRun, RankingResult, TechnicalScreenResult
from app.services.csv_store import read_rows


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
    if name_key:
        payload.pop(name_key, None)
    payload.pop('id', None)
    payload.pop('updateTime', None)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _import_rows(
    session,
    category,
    result_key,
    csv_result,
    source_file,
    result_model,
    *,
    job_run_id=None,
    code_key='code',
    name_key='name',
):
    as_of_date = _parse_as_of_date(csv_result.update_time)
    run = AnalysisRun(
        category,
        result_key,
        as_of_date,
        row_count=len(csv_result.rows),
        source_file=source_file,
        job_run_id=job_run_id,
    )
    session.add(run)
    session.flush()

    objects = []
    for index, row in enumerate(csv_result.rows, start=1):
        code = str(row.get(code_key, '')).strip()
        if not code:
            continue
        objects.append(
            result_model(
                run.id,
                index,
                code,
                row.get(name_key) if name_key else None,
                _serialize_row_payload(row, code_key=code_key, name_key=name_key),
            )
        )

    if objects:
        session.bulk_save_objects(objects)

    run.row_count = len(objects)

    return {
        'status': 'imported',
        'run_id': run.id,
        'category': category,
        'result_key': result_key,
        'row_count': run.row_count,
        'as_of_date': as_of_date.isoformat(),
    }


def import_ranking_results(config, ranking_key, *, job_run_id=None, session=None):
    csv_filename = STOCK_RANKING_FILES.get(ranking_key)
    if csv_filename is None:
        return {'status': 'skipped', 'reason': 'unknown ranking key'}

    csv_result = read_rows(config['RESULT_PATH'], csv_filename)
    if csv_result.error or csv_result.missing:
        return {'status': 'skipped', 'reason': csv_result.error or 'file not found'}

    def _run(sess):
        return _import_rows(
            sess,
            AnalysisRun.CATEGORY_RANKING,
            ranking_key,
            csv_result,
            csv_filename,
            RankingResult,
            job_run_id=job_run_id,
        )

    if session is not None:
        return _run(session)
    with session_scope() as sess:
        return _run(sess)


def import_technical_screen_results(config, screen_key, *, job_run_id=None, session=None):
    csv_filename = TECHNICAL_ANALYSIS_FILES.get(screen_key)
    if csv_filename is None:
        return {'status': 'skipped', 'reason': 'unknown technical key'}

    csv_result = read_rows(config['RESULT_PATH'], csv_filename)
    if csv_result.error or csv_result.missing:
        return {'status': 'skipped', 'reason': csv_result.error or 'file not found'}

    def _run(sess):
        return _import_rows(
            sess,
            AnalysisRun.CATEGORY_TECHNICAL,
            screen_key,
            csv_result,
            csv_filename,
            TechnicalScreenResult,
            job_run_id=job_run_id,
        )

    if session is not None:
        return _run(session)
    with session_scope() as sess:
        return _run(sess)


def import_price_change_results(config, *, job_run_id=None, session=None):
    csv_result = read_rows(config['RESULT_PATH'], PRICE_CHANGE_FILE)
    if csv_result.error or csv_result.missing:
        return {'status': 'skipped', 'reason': csv_result.error or 'file not found'}

    def _run(sess):
        return _import_rows(
            sess,
            AnalysisRun.CATEGORY_PRICE_CHANGE,
            'price_change',
            csv_result,
            PRICE_CHANGE_FILE,
            TechnicalScreenResult,
            job_run_id=job_run_id,
        )

    if session is not None:
        return _run(session)
    with session_scope() as sess:
        return _run(sess)


def import_business_ranking_results(config, *, job_run_id=None, session=None):
    csv_result = read_rows(config['RESULT_PATH'], BUSINESS_RANKING_FILE)
    if csv_result.error or csv_result.missing:
        return {'status': 'skipped', 'reason': csv_result.error or 'file not found'}

    def _run(sess):
        return _import_rows(
            sess,
            AnalysisRun.CATEGORY_RANKING,
            'business',
            csv_result,
            BUSINESS_RANKING_FILE,
            RankingResult,
            job_run_id=job_run_id,
        )

    if session is not None:
        return _run(session)
    with session_scope() as sess:
        return _run(sess)


def import_annual_stock_report(config, year, *, job_run_id=None, session=None):
    source_file = annual_stock_report_filename(year)
    csv_result = read_rows(config['RESULT_PATH'], source_file, add_update_time=True)
    if csv_result.error or csv_result.missing:
        return {'status': 'skipped', 'reason': csv_result.error or 'file not found'}

    def _run(sess):
        return _import_rows(
            sess,
            AnalysisRun.CATEGORY_ANNUAL_STOCK,
            str(year),
            csv_result,
            source_file,
            RankingResult,
            job_run_id=job_run_id,
        )

    if session is not None:
        return _run(session)
    with session_scope() as sess:
        return _run(sess)


def import_annual_industry_report(config, year, *, job_run_id=None, session=None):
    source_file = annual_industry_report_filename(year)
    csv_result = read_rows(config['RESULT_PATH'], source_file, add_update_time=True)
    if csv_result.error or csv_result.missing:
        return {'status': 'skipped', 'reason': csv_result.error or 'file not found'}

    def _run(sess):
        return _import_rows(
            sess,
            AnalysisRun.CATEGORY_ANNUAL_INDUSTRY,
            str(year),
            csv_result,
            source_file,
            RankingResult,
            job_run_id=job_run_id,
            code_key='industry',
            name_key=None,
        )

    if session is not None:
        return _run(session)
    with session_scope() as sess:
        return _run(sess)


def sync_all_results_to_db(config, *, job_run_id=None, session=None):
    """Import all known ranking and technical CSV files into the database."""
    summary = {}

    def _import_all(sess):
        out = {}
        for ranking_key in STOCK_RANKING_FILES:
            out['ranking_' + ranking_key] = import_ranking_results(
                config, ranking_key, job_run_id=job_run_id, session=sess
            )
        out['ranking_business'] = import_business_ranking_results(
            config, job_run_id=job_run_id, session=sess
        )
        for screen_key in TECHNICAL_ANALYSIS_FILES:
            out['technical_' + screen_key] = import_technical_screen_results(
                config, screen_key, job_run_id=job_run_id, session=sess
            )
        out['price_change'] = import_price_change_results(
            config, job_run_id=job_run_id, session=sess
        )
        return out

    if session is not None:
        return _import_all(session)

    with session_scope() as sess:
        return _import_all(sess)
