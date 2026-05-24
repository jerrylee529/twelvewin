# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db_session
from api.services.data_status import get_data_status

router = APIRouter(tags=['data-status'])


@router.get('/data-status')
def data_status(session: Session = Depends(get_db_session)):
    return get_data_status(session)
