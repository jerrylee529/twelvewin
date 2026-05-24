# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db_session
from api.routers.helpers import to_table_response
from api.schemas.responses import TableResponse
from api.services.clusters import get_cluster_payload

router = APIRouter(prefix='/clusters', tags=['clusters'])


@router.get('/{section}', response_model=TableResponse)
def get_cluster(section: str, session: Session = Depends(get_db_session)):
    return to_table_response(get_cluster_payload(session, section))
