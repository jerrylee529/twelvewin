# -*- coding: utf-8 -*-

"""Precomputed cluster chart payloads for visualization."""

import json

from sqlalchemy.orm import Session

from api.db.models import StockClusterChart


def get_cluster_chart_payload(session: Session, section: str) -> dict:
    if not section or section == 'all':
        return {}

    record = session.query(StockClusterChart).filter_by(section=section).one_or_none()
    if record is None or not record.payload:
        return {}

    try:
        payload = json.loads(record.payload)
    except json.JSONDecodeError:
        return {}

    if isinstance(payload, dict):
        payload['updateTime'] = (
            record.update_time.isoformat() if record.update_time is not None else None
        )
        return payload

    return {}
