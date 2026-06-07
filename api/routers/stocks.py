# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.db.session import get_db_session
from api.routers.helpers import to_table_response
from api.schemas.responses import (
    BarsResponse,
    InstrumentsListResponse,
    InstrumentsResponse,
    ProfileResponse,
    QuoteResponse,
    ResearchContextResponse,
)
from api.services.research_context import get_research_context
from api.services.stocks import (
    get_daily_bars,
    get_profile,
    get_quote,
    list_instruments,
    search_instruments,
)

router = APIRouter(prefix='/stocks', tags=['stocks'])


@router.get('/list', response_model=InstrumentsListResponse)
def instrument_list(
    offset: int = Query(0, ge=0),
    limit: int | None = Query(
        None,
        ge=1,
        le=10000,
        description='Max rows to return; omit for all instruments',
    ),
    session: Session = Depends(get_db_session),
):
    instruments, total = list_instruments(session, offset=offset, limit=limit)
    return InstrumentsListResponse(total=total, instruments=instruments)


@router.get('/search', response_model=InstrumentsResponse)
def search(
    q: str = Query('', description='Code or name prefix/substring'),
    limit: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_db_session),
):
    return InstrumentsResponse(instruments=search_instruments(session, q, limit=limit))


@router.get('/{code}/bars', response_model=BarsResponse)
def bars(
    code: str,
    include_quote: bool = Query(
        False,
        description='Append latest Redis quote bar when available',
    ),
    days: int | None = Query(
        None,
        ge=1,
        le=5000,
        description='Limit to the most recent N trading days',
    ),
    session: Session = Depends(get_db_session),
):
    result = get_daily_bars(
        session,
        code,
        include_quote=include_quote,
        days=days,
    )
    return BarsResponse(
        rows=result.rows,
        updateTime=result.update_time,
        error=result.error,
    )


@router.get('/{code}/quote', response_model=QuoteResponse)
def quote(code: str, session: Session = Depends(get_db_session)):
    return QuoteResponse(**get_quote(session, code))


@router.get('/{code}/profile', response_model=ProfileResponse)
def profile(
    code: str,
    include_quote: bool = Query(
        False,
        description='Include Redis or daily-bar quote fields in the profile payload',
    ),
    session: Session = Depends(get_db_session),
):
    return ProfileResponse(**get_profile(session, code, include_quote=include_quote))


@router.get('/{code}/research-context', response_model=ResearchContextResponse)
def research_context(code: str, session: Session = Depends(get_db_session)):
    payload = get_research_context(session, code)
    if payload.get('error'):
        return ResearchContextResponse(error=payload['error'])
    return ResearchContextResponse(**payload)
