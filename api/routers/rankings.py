# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.db.session import get_db_session
from api.routers.helpers import to_table_response
from api.schemas.responses import TableResponse
from api.services.published_results import get_ranking_rows
from core.artifacts import STOCK_RANKING_FILES

router = APIRouter(prefix='/rankings', tags=['rankings'])


@router.get('/{ranking_key}', response_model=TableResponse)
def get_ranking(
    ranking_key: str,
    preview: bool = Query(False, description='Return a limited preview set'),
    session: Session = Depends(get_db_session),
):
    if ranking_key not in STOCK_RANKING_FILES:
        raise HTTPException(status_code=404, detail='unknown ranking key')

    max_rows = 20 if preview else None
    return to_table_response(get_ranking_rows(session, ranking_key, max_rows=max_rows))
