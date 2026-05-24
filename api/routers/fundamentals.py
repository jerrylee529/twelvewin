# -*- coding: utf-8 -*-

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.db.session import get_db_session
from api.routers.helpers import to_table_response
from api.schemas.responses import TableResponse
from api.services.fundamentals import SORT_COLUMNS, search_fundamentals

router = APIRouter(prefix='/fundamentals', tags=['fundamentals'])


@router.get('/screener', response_model=TableResponse)
def screener(
    trade_date: date | None = Query(None, description='Snapshot date; defaults to latest'),
    pe_min: float | None = None,
    pe_max: float | None = None,
    pb_min: float | None = None,
    pb_max: float | None = None,
    roe_min: float | None = None,
    roe_3y_min: float | None = None,
    dividend_yield_min: float | None = None,
    market_cap_min: float | None = None,
    market_cap_max: float | None = None,
    float_market_cap_min: float | None = None,
    float_market_cap_max: float | None = None,
    industry: str | None = None,
    search: str | None = None,
    exclude_st: bool = True,
    sort: str = Query('pe_discount_to_industry'),
    order: str = Query('asc', pattern='^(asc|desc)$'),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_db_session),
):
    if sort not in SORT_COLUMNS:
        sort = 'pe_discount_to_industry'

    return to_table_response(
        search_fundamentals(
            session,
            trade_date=trade_date,
            pe_min=pe_min,
            pe_max=pe_max,
            pb_min=pb_min,
            pb_max=pb_max,
            roe_min=roe_min,
            roe_3y_min=roe_3y_min,
            dividend_yield_min=dividend_yield_min,
            market_cap_min=market_cap_min,
            market_cap_max=market_cap_max,
            float_market_cap_min=float_market_cap_min,
            float_market_cap_max=float_market_cap_max,
            industry=industry,
            search=search,
            exclude_st=exclude_st,
            sort=sort,
            order=order,
            page=page,
            page_size=page_size,
        )
    )
