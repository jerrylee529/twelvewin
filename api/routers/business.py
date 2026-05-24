# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.db.session import get_db_session
from api.routers.helpers import to_table_response
from api.schemas.responses import TableResponse
from api.services.business import get_business_rows

router = APIRouter(prefix='/business', tags=['business'])


@router.get('', response_model=TableResponse)
def get_business(
    labels: str = Query('', description='Space-separated label filter'),
    session: Session = Depends(get_db_session),
):
    return to_table_response(get_business_rows(session, labels))
