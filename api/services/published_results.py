# -*- coding: utf-8 -*-

"""Read published ranking and technical screen rows from Postgres."""

import json

from sqlalchemy.orm import Session

from api.db.models import AnalysisRun, RankingResult, TechnicalScreenResult
from api.services.types import QueryResult
from core.artifacts import STOCK_RANKING_FILES, TECHNICAL_ANALYSIS_FILES
from core.stock_codes import normalize_stock_code

PRICE_CHANGE_PERIODS = {
    '近一周': 7,
    '近一月': 30,
    '近三月': 30 * 3,
    '近半年': 30 * 6,
    '近一年': 30 * 12,
}


def _deserialize_row(result_model, *, update_time=None):
    row = {'code': normalize_stock_code(result_model.code), 'name': result_model.name or ''}
    if result_model.data:
        try:
            row.update(json.loads(result_model.data))
        except json.JSONDecodeError:
            pass
    row['code'] = normalize_stock_code(row.get('code'))
    if update_time:
        row['updateTime'] = update_time
    return row


def get_latest_analysis_run(session: Session, category: str, result_key: str):
    return (
        session.query(AnalysisRun)
        .filter_by(category=category, result_key=result_key)
        .order_by(AnalysisRun.as_of_date.desc(), AnalysisRun.id.desc())
        .first()
    )


def get_ranking_rows(session: Session, ranking_key: str, *, max_rows=None) -> QueryResult:
    if ranking_key not in STOCK_RANKING_FILES:
        return QueryResult(error='unknown ranking key')

    run = get_latest_analysis_run(session, AnalysisRun.CATEGORY_RANKING, ranking_key)
    if run is None or run.row_count == 0:
        return QueryResult(error='no published analysis data in database')

    query = (
        session.query(RankingResult)
        .filter_by(run_id=run.id)
        .order_by(RankingResult.rank_order)
    )
    if max_rows is not None:
        query = query.limit(max_rows)

    update_time = run.as_of_date.strftime('%Y-%m-%d')
    rows = []
    for item in query.all():
        row = _deserialize_row(item, update_time=update_time)
        row['id'] = item.rank_order
        rows.append(row)

    return QueryResult(rows=rows, update_time=update_time)


def get_technical_rows(session: Session, screen_key: str, *, max_rows=None) -> QueryResult:
    if screen_key not in TECHNICAL_ANALYSIS_FILES:
        return QueryResult(error='unknown technical analysis key')

    run = get_latest_analysis_run(session, AnalysisRun.CATEGORY_TECHNICAL, screen_key)
    if run is None or run.row_count == 0:
        return QueryResult(error='no published analysis data in database')

    query = (
        session.query(TechnicalScreenResult)
        .filter_by(run_id=run.id)
        .order_by(TechnicalScreenResult.rank_order)
    )
    if max_rows is not None:
        query = query.limit(max_rows)

    update_time = run.as_of_date.strftime('%Y-%m-%d')
    rows = []
    for item in query.all():
        row = _deserialize_row(item, update_time=update_time)
        row['id'] = item.rank_order
        rows.append(row)

    return QueryResult(rows=rows, update_time=update_time)


def get_price_change_rows(
    session: Session,
    *,
    days='近一周',
    low=-30,
    high=0,
) -> QueryResult:
    days = ''.join((days or '近一周').split())
    period = PRICE_CHANGE_PERIODS.get(days, 7)
    rate_field = 'rate' + str(period)

    run = get_latest_analysis_run(session, AnalysisRun.CATEGORY_PRICE_CHANGE, 'price_change')
    if run is None or run.row_count == 0:
        return QueryResult(error='no published analysis data in database')

    query = (
        session.query(TechnicalScreenResult)
        .filter_by(run_id=run.id)
        .order_by(TechnicalScreenResult.rank_order)
    )

    try:
        low = float(low)
        high = float(high)
    except (TypeError, ValueError):
        low = -30.0
        high = 0.0

    update_time = run.as_of_date.strftime('%Y-%m-%d')
    rows = []
    for item in query.all():
        row = _deserialize_row(item, update_time=update_time)
        try:
            rate = float(row[rate_field])
        except (KeyError, TypeError, ValueError):
            continue

        if (rate > -9999) and (rate >= low) and (rate <= high):
            row['id'] = len(rows) + 1
            row['rate'] = rate
            rows.append(row)

    return QueryResult(rows=rows, update_time=update_time)
