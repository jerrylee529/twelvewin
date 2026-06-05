# -*- coding: utf-8 -*-

"""Optional shared-secret auth for Research API (Dify HTTP tools)."""

import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


def expected_research_api_key() -> str:
    return os.environ.get('TW_RESEARCH_API_KEY', '').strip()


def is_research_api_key_required() -> bool:
    return bool(expected_research_api_key())


def _is_exempt_path(path: str) -> bool:
    return path in ('/api/v1/health', '/docs', '/openapi.json', '/redoc')


class ResearchApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        expected = expected_research_api_key()
        path = request.url.path

        if expected and path.startswith('/api/v1') and not _is_exempt_path(path):
            provided = request.headers.get('X-Twelvewin-Api-Key', '').strip()
            if provided != expected:
                return JSONResponse(
                    status_code=401,
                    content={'detail': 'invalid or missing X-Twelvewin-Api-Key'},
                )

        return await call_next(request)
