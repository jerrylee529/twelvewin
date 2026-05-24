# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db_session
from api.schemas.responses import IndustriesResponse
from api.services.industries import (
    get_industry_cluster_payload,
    get_industry_stock_payload,
    list_industries,
)

router = APIRouter(prefix='/industries', tags=['industries'])


@router.get('', response_model=IndustriesResponse)
def get_industries(session: Session = Depends(get_db_session)):
    return IndustriesResponse(industries=list_industries(session))


@router.get('/{industry}/data')
def industry_data(industry: str, session: Session = Depends(get_db_session)):
    return get_industry_cluster_payload(session, industry)


@router.get('/{industry}/stocks/{code}')
def industry_stock(
    industry: str,
    code: str,
    session: Session = Depends(get_db_session),
):
    return get_industry_stock_payload(session, industry, code)
