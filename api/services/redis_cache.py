# -*- coding: utf-8 -*-

"""Redis JSON cache helpers for AI analysis results."""

from __future__ import annotations

import json
import os

from core.redis_client import get_redis_client

DEFAULT_TTL_SECONDS = int(os.environ.get('TW_AI_CACHE_TTL_SECONDS', '7776000') or '7776000')
FILING_ANALYSIS_PREFIX = 'twelvewin:filing:analysis'
STOCK_SCORE_PREFIX = 'twelvewin:stock:score'


def filing_analysis_cache_key(
    code: str,
    year: int,
    season: int,
    *,
    analysis_version: str,
) -> str:
    return f'{FILING_ANALYSIS_PREFIX}:{code}:{year}:{season}:{analysis_version}'


def stock_score_cache_key(
    code: str,
    data_as_of: str,
    *,
    score_version: str,
) -> str:
    return f'{STOCK_SCORE_PREFIX}:{code}:{data_as_of}:{score_version}'


def cache_get_json(key: str) -> dict | None:
    try:
        client = get_redis_client()
        raw = client.get(key)
        if not raw:
            return None
        payload = json.loads(raw)
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def cache_set_json(key: str, payload: dict, *, ttl_seconds: int | None = None) -> bool:
    try:
        client = get_redis_client()
        encoded = json.dumps(payload, ensure_ascii=False)
        ttl = DEFAULT_TTL_SECONDS if ttl_seconds is None else ttl_seconds
        if ttl > 0:
            client.setex(key, ttl, encoded)
        else:
            client.set(key, encoded)
        return True
    except Exception:
        return False


def cache_delete(key: str) -> None:
    try:
        client = get_redis_client()
        client.delete(key)
    except Exception:
        return None
