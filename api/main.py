# -*- coding: utf-8 -*-

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import (
    business,
    clusters,
    data_status,
    fundamentals,
    health,
    industries,
    rankings,
    stocks,
    technical,
)

API_PREFIX = '/api/v1'


def _cors_origins():
    raw = os.environ.get('API_CORS_ORIGINS', 'http://localhost:3000')
    return [origin.strip() for origin in raw.split(',') if origin.strip()]


def create_app() -> FastAPI:
    app = FastAPI(
        title='Twelvewin API',
        version='1.0.0',
        docs_url='/docs',
        openapi_url='/openapi.json',
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.include_router(health.router, prefix=API_PREFIX)
    app.include_router(data_status.router, prefix=API_PREFIX)
    app.include_router(fundamentals.router, prefix=API_PREFIX)
    app.include_router(rankings.router, prefix=API_PREFIX)
    app.include_router(technical.router, prefix=API_PREFIX)
    app.include_router(business.router, prefix=API_PREFIX)
    app.include_router(clusters.router, prefix=API_PREFIX)
    app.include_router(industries.router, prefix=API_PREFIX)
    app.include_router(stocks.router, prefix=API_PREFIX)

    return app


app = create_app()
