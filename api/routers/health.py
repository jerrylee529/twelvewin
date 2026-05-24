# -*- coding: utf-8 -*-

from fastapi import APIRouter

from api.schemas.responses import HealthResponse

router = APIRouter(tags=['health'])


@router.get('/health', response_model=HealthResponse)
def health():
    return HealthResponse(status='ok')
