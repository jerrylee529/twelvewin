# -*- coding: utf-8 -*-

"""Fundamental stock screener queries."""

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from api.db.models import FundamentalSnapshot
from api.services.types import QueryResult

SORT_COLUMNS = {
    'pe_ttm': FundamentalSnapshot.pe_ttm,
    'pb_lf': FundamentalSnapshot.pb_lf,
    'roe': FundamentalSnapshot.roe,
    'dividend_yield': FundamentalSnapshot.dividend_yield,
    'market_cap': FundamentalSnapshot.market_cap,
    'float_market_cap': FundamentalSnapshot.float_market_cap,
    'pe_discount_to_industry': FundamentalSnapshot.pe_discount_to_industry,
    'pb_discount_to_industry': FundamentalSnapshot.pb_discount_to_industry,
    'code': FundamentalSnapshot.code,
}


def _latest_trade_date(session: Session):
    return session.query(func.max(FundamentalSnapshot.trade_date)).scalar()


def _row(snapshot: FundamentalSnapshot) -> dict:
    return {
        'code': snapshot.code,
        'name': snapshot.name,
        'industry': snapshot.industry,
        'is_st': snapshot.is_st,
        'close': snapshot.close,
        'pe_ttm': snapshot.pe_ttm,
        'pb_lf': snapshot.pb_lf,
        'roe': snapshot.roe,
        'roe_y1': snapshot.roe_y1,
        'roe_y2': snapshot.roe_y2,
        'roe_y3': snapshot.roe_y3,
        'dividend_yield': snapshot.dividend_yield,
        'market_cap': snapshot.market_cap,
        'float_market_cap': snapshot.float_market_cap,
        'revenue_growth': snapshot.revenue_growth,
        'profit_growth': snapshot.profit_growth,
        'pe_discount_to_industry': snapshot.pe_discount_to_industry,
        'pb_discount_to_industry': snapshot.pb_discount_to_industry,
        'updateTime': snapshot.trade_date.strftime('%Y-%m-%d'),
    }


def _apply_range(query, column, min_value=None, max_value=None):
    if min_value is not None:
        query = query.filter(column >= min_value)
    if max_value is not None:
        query = query.filter(column <= max_value)
    return query


def search_fundamentals(
    session: Session,
    *,
    trade_date=None,
    pe_min=None,
    pe_max=None,
    pb_min=None,
    pb_max=None,
    roe_min=None,
    roe_3y_min=None,
    dividend_yield_min=None,
    market_cap_min=None,
    market_cap_max=None,
    float_market_cap_min=None,
    float_market_cap_max=None,
    industry=None,
    search=None,
    exclude_st=True,
    sort='pe_discount_to_industry',
    order='asc',
    page=1,
    page_size=50,
) -> QueryResult:
    trade_date = trade_date or _latest_trade_date(session)
    if trade_date is None:
        return QueryResult(error='no fundamental snapshots in database')

    query = session.query(FundamentalSnapshot).filter_by(trade_date=trade_date)

    query = _apply_range(query, FundamentalSnapshot.pe_ttm, pe_min, pe_max)
    query = _apply_range(query, FundamentalSnapshot.pb_lf, pb_min, pb_max)
    query = _apply_range(query, FundamentalSnapshot.roe, roe_min, None)
    query = _apply_range(query, FundamentalSnapshot.dividend_yield, dividend_yield_min, None)
    query = _apply_range(query, FundamentalSnapshot.market_cap, market_cap_min, market_cap_max)
    query = _apply_range(
        query,
        FundamentalSnapshot.float_market_cap,
        float_market_cap_min,
        float_market_cap_max,
    )

    if roe_3y_min is not None:
        query = query.filter(
            FundamentalSnapshot.roe_y1 >= roe_3y_min,
            FundamentalSnapshot.roe_y2 >= roe_3y_min,
            FundamentalSnapshot.roe_y3 >= roe_3y_min,
        )

    if industry:
        query = query.filter(FundamentalSnapshot.industry == industry)

    if search:
        pattern = '%{}%'.format(search.strip())
        query = query.filter(
            or_(
                FundamentalSnapshot.code.like(pattern),
                FundamentalSnapshot.name.like(pattern),
            )
        )

    if exclude_st:
        query = query.filter(FundamentalSnapshot.is_st.is_(False))

    total = query.count()

    sort_column = SORT_COLUMNS.get(sort, FundamentalSnapshot.pe_discount_to_industry)
    if order == 'desc':
        query = query.order_by(sort_column.is_(None), sort_column.desc())
    else:
        query = query.order_by(sort_column.is_(None), sort_column.asc())

    page = max(page, 1)
    page_size = min(max(page_size, 1), 200)
    rows = query.offset((page - 1) * page_size).limit(page_size).all()

    return QueryResult(
        rows=[_row(item) for item in rows],
        update_time=trade_date.strftime('%Y-%m-%d'),
        total_count=total,
    )
