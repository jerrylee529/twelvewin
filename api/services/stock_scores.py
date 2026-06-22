# -*- coding: utf-8 -*-

"""Stock AI investment score read/write with Redis + Postgres cache."""

from __future__ import annotations

import datetime
import json
import os

from sqlalchemy.orm import Session

from api.db.models import StockAiScore
from api.services.redis_cache import (
    cache_get_json,
    cache_set_json,
    stock_score_cache_key,
)
from core.stock_codes import normalize_stock_code

DEFAULT_SCORE_VERSION = os.environ.get('TW_STOCK_SCORE_VERSION', 'v1')


def _load_json_field(raw: str | None):
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _serialize_score_row(row: StockAiScore) -> dict:
    score = _load_json_field(row.score_json)
    return {
        'code': row.code,
        'data_as_of': row.data_as_of,
        'score_version': row.score_version,
        'model': row.model,
        'status': row.status,
        'score': score,
        'markdown': row.markdown or '',
        'created_at': row.created_at.isoformat() if row.created_at else None,
    }


def get_stock_score(
    session: Session,
    code: str,
    data_as_of: str,
    *,
    score_version: str | None = None,
) -> dict | None:
    normalized = normalize_stock_code(code)
    as_of = (data_as_of or '').strip()
    if not normalized or not as_of:
        return None

    version = score_version or DEFAULT_SCORE_VERSION
    cache_key = stock_score_cache_key(normalized, as_of, score_version=version)
    cached = cache_get_json(cache_key)
    if cached is not None:
        return cached

    row = (
        session.query(StockAiScore)
        .filter_by(code=normalized, data_as_of=as_of, score_version=version)
        .first()
    )
    if row is None or row.status != StockAiScore.STATUS_DONE:
        return None

    payload = _serialize_score_row(row)
    cache_set_json(cache_key, payload)
    return payload


def upsert_stock_score(
    session: Session,
    code: str,
    data_as_of: str,
    payload: dict,
    *,
    score_version: str | None = None,
) -> dict:
    normalized = normalize_stock_code(code)
    as_of = (data_as_of or '').strip()
    if not normalized or not as_of:
        return {'error': 'code and data_as_of are required'}

    version = score_version or payload.get('score_version') or DEFAULT_SCORE_VERSION
    now = datetime.datetime.now()
    row = (
        session.query(StockAiScore)
        .filter_by(code=normalized, data_as_of=as_of, score_version=version)
        .first()
    )

    score = payload.get('score')
    fields = {
        'model': payload.get('model'),
        'status': payload.get('status') or StockAiScore.STATUS_DONE,
        'score_json': json.dumps(score, ensure_ascii=False) if score is not None else None,
        'markdown': payload.get('markdown') or '',
        'created_at': now,
    }

    if row is None:
        row = StockAiScore(
            code=normalized,
            data_as_of=as_of,
            score_version=version,
            **fields,
        )
        session.add(row)
    else:
        for key, value in fields.items():
            setattr(row, key, value)

    session.flush()
    result = _serialize_score_row(row)
    cache_key = stock_score_cache_key(normalized, as_of, score_version=version)
    cache_set_json(cache_key, result)
    return result
