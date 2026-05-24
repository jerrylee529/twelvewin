# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.db.session import get_db_session
from api.routers.helpers import to_table_response
from api.schemas.responses import TableResponse
from api.services.published_results import get_price_change_rows, get_technical_rows
from core.artifacts import TECHNICAL_ANALYSIS_FILES

router = APIRouter(prefix='/technical', tags=['technical'])


@router.get('/filter/price-change', response_model=TableResponse)
def get_price_change(
    days: str = Query('近一周'),
    low: float = Query(-30),
    high: float = Query(0),
    session: Session = Depends(get_db_session),
):
    return to_table_response(
        get_price_change_rows(session, days=days, low=low, high=high)
    )


@router.get('/{screen_key}', response_model=TableResponse)
def get_technical_screen(
    screen_key: str,
    preview: bool = Query(False, description='Return a limited preview set'),
    session: Session = Depends(get_db_session),
):
    if screen_key not in TECHNICAL_ANALYSIS_FILES:
        raise HTTPException(status_code=404, detail='unknown technical analysis key')

    max_rows = 10 if preview else None
    return to_table_response(get_technical_rows(session, screen_key, max_rows=max_rows))
