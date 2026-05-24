# -*- coding: utf-8 -*-

"""Optional Redis quote lookup (no Flask dependency)."""

from urllib.parse import urlparse

import redis

from core.config import load_core_settings

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        settings = load_core_settings()
        url = settings.get('REDIS_URL') or 'redis://:@127.0.0.1:6379/0'
        parsed = urlparse(url)
        host = parsed.hostname or '127.0.0.1'
        port = parsed.port or 6379
        password = parsed.password or None
        db = 0
        path = (parsed.path or '').lstrip('/')
        if path.isdigit():
            db = int(path)
        _pool = redis.ConnectionPool(
            host=host,
            password=password,
            port=port,
            db=db,
            decode_responses=True,
        )
    return _pool


def get_quotation(code: str):
    try:
        client = redis.Redis(connection_pool=_get_pool())
        return client.hgetall(code)
    except Exception:
        return None
