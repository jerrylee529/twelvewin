# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db_session
from api.routers.helpers import to_table_response
from api.schemas.responses import ClusterChartResponse, TableResponse
from api.services.cluster_chart import get_cluster_chart_payload
from api.services.clusters import get_cluster_payload

router = APIRouter(prefix='/clusters', tags=['clusters'])


@router.get('/{section}/chart', response_model=ClusterChartResponse)
def get_cluster_chart(section: str, session: Session = Depends(get_db_session)):
    payload = get_cluster_chart_payload(session, section)
    if not payload:
        return ClusterChartResponse(error='chart data not available')
    return ClusterChartResponse(**payload)


@router.get('/{section}', response_model=TableResponse)
def get_cluster(section: str, session: Session = Depends(get_db_session)):
    return to_table_response(get_cluster_payload(session, section))
