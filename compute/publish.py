# -*- coding: utf-8 -*-

"""Publish analysis result dataframes directly to Postgres (no CSV required)."""

import datetime
import json

import pandas as pd

from app.models import AnalysisRun, RankingResult, TechnicalScreenResult
from core.db import session_scope
from core.stock_codes import normalize_stock_code

SCREEN_BASENAME_TO_KEY = {
    'highest_in_history': 'highest',
    'lowest_in_history': 'lowest',
    'ma_long': 'ma_long',
    'break_ma': 'break_ma',
    'above_ma': 'above_ma',
}

RANKING_TITLE_TO_KEY = {
    'stock_pe': 'pe',
    'stock_pb': 'pb',
    'stock_roe': 'roe',
    'stock_dividence': 'divi',
    'stock_value': 'value',
    'stock_business': 'business',
}


def _serialize_row_payload(row, *, code_key='code', name_key='name'):
    if hasattr(row, 'to_dict'):
        payload = row.to_dict()
    else:
        payload = dict(row)
    payload.pop(code_key, None)
    if name_key:
        payload.pop(name_key, None)
    payload.pop('id', None)
    payload.pop('updateTime', None)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)


def _dataframe_records(frame):
    if frame is None or frame.empty:
        return []
    return frame.to_dict(orient='records')


def publish_rows(
    session,
    category,
    result_key,
    records,
    result_model,
    *,
    as_of_date=None,
    source_file=None,
    job_run_id=None,
    code_key='code',
    name_key='name',
):
    as_of_date = as_of_date or datetime.date.today()
    run = AnalysisRun(
        category,
        result_key,
        as_of_date,
        row_count=0,
        source_file=source_file,
        job_run_id=job_run_id,
    )
    session.add(run)
    session.flush()

    objects = []
    for index, row in enumerate(records, start=1):
        code = normalize_stock_code(row.get(code_key))
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
        'status': 'published',
        'run_id': run.id,
        'category': category,
        'result_key': result_key,
        'row_count': run.row_count,
        'as_of_date': as_of_date.isoformat(),
    }


def publish_ranking_dataframe(
    dataframe,
    *,
    ranking_key,
    as_of_date=None,
    source_file=None,
    job_run_id=None,
    session=None,
):
    records = _dataframe_records(dataframe)

    def _run(sess):
        return publish_rows(
            sess,
            AnalysisRun.CATEGORY_RANKING,
            ranking_key,
            records,
            RankingResult,
            as_of_date=as_of_date,
            source_file=source_file,
            job_run_id=job_run_id,
        )

    if session is not None:
        return _run(session)
    with session_scope() as sess:
        return _run(sess)


def publish_technical_screen_dataframe(
    dataframe,
    *,
    screen_key,
    as_of_date=None,
    source_file=None,
    job_run_id=None,
    session=None,
):
    records = _dataframe_records(dataframe)

    def _run(sess):
        return publish_rows(
            sess,
            AnalysisRun.CATEGORY_TECHNICAL,
            screen_key,
            records,
            TechnicalScreenResult,
            as_of_date=as_of_date,
            source_file=source_file,
            job_run_id=job_run_id,
        )

    if session is not None:
        return _run(session)
    with session_scope() as sess:
        return _run(sess)


def publish_price_change_dataframe(
    dataframe,
    *,
    as_of_date=None,
    source_file=None,
    job_run_id=None,
    session=None,
):
    records = _dataframe_records(dataframe)

    def _run(sess):
        return publish_rows(
            sess,
            AnalysisRun.CATEGORY_PRICE_CHANGE,
            'price_change',
            records,
            TechnicalScreenResult,
            as_of_date=as_of_date,
            source_file=source_file,
            job_run_id=job_run_id,
        )

    if session is not None:
        return _run(session)
    with session_scope() as sess:
        return _run(sess)


def publish_ranking_by_title(dataframe, title, **kwargs):
    ranking_key = RANKING_TITLE_TO_KEY.get(title)
    if ranking_key is None:
        return {'status': 'skipped', 'reason': 'unknown ranking title'}
    return publish_ranking_dataframe(
        dataframe,
        ranking_key=ranking_key,
        source_file='{}.csv'.format(title),
        **kwargs,
    )


def publish_annual_stock_dataframe(
    dataframe,
    year,
    *,
    as_of_date=None,
    job_run_id=None,
    session=None,
):
    from core.artifacts import annual_stock_report_filename

    records = _dataframe_records(dataframe)

    def _run(sess):
        return publish_rows(
            sess,
            AnalysisRun.CATEGORY_ANNUAL_STOCK,
            str(year),
            records,
            RankingResult,
            as_of_date=as_of_date,
            source_file=annual_stock_report_filename(year),
            job_run_id=job_run_id,
        )

    if session is not None:
        return _run(session)
    with session_scope() as sess:
        return _run(sess)


def publish_annual_industry_dataframe(
    dataframe,
    year,
    *,
    as_of_date=None,
    job_run_id=None,
    session=None,
):
    from core.artifacts import annual_industry_report_filename

    records = _dataframe_records(dataframe)

    def _run(sess):
        return publish_rows(
            sess,
            AnalysisRun.CATEGORY_ANNUAL_INDUSTRY,
            str(year),
            records,
            RankingResult,
            as_of_date=as_of_date,
            source_file=annual_industry_report_filename(year),
            job_run_id=job_run_id,
            code_key='industry',
            name_key=None,
        )

    if session is not None:
        return _run(session)
    with session_scope() as sess:
        return _run(sess)


def publish_screen_by_basename(dataframe, basename, **kwargs):
    screen_key = SCREEN_BASENAME_TO_KEY.get(basename, basename)
    return publish_technical_screen_dataframe(
        dataframe,
        screen_key=screen_key,
        source_file='{}.csv'.format(basename),
        **kwargs,
    )
