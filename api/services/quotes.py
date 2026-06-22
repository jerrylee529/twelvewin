# -*- coding: utf-8 -*-

"""Optional Redis quote lookup (no Flask dependency)."""

from core.redis_client import get_redis_client


def get_quotation(code: str):
    try:
        client = get_redis_client()
        return client.hgetall(code)
    except Exception:
        return None
