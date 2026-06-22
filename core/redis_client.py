# -*- coding: utf-8 -*-

"""Shared Redis connection pool (quotes, AI cache, etc.)."""

from __future__ import annotations

from urllib.parse import urlparse

import redis

from core.config import load_core_settings

_pools: dict[bool, redis.ConnectionPool] = {}


def get_redis_pool(*, decode_responses: bool = True) -> redis.ConnectionPool:
    pool_key = decode_responses
    pool = _pools.get(pool_key)
    if pool is not None:
        return pool

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

    pool = redis.ConnectionPool(
        host=host,
        password=password,
        port=port,
        db=db,
        decode_responses=decode_responses,
    )
    _pools[pool_key] = pool
    return pool


def get_redis_client(*, decode_responses: bool = True) -> redis.Redis:
    return redis.Redis(connection_pool=get_redis_pool(decode_responses=decode_responses))
