# -*- coding: utf-8 -*-

"""Business ranking with optional label filtering."""

from sqlalchemy.orm import Session

from api.db.models import StockLabels
from api.services.published_results import get_ranking_rows
from api.services.types import QueryResult


def _labels_match(stock_labels, requested_labels):
    if not requested_labels:
        return True
    if stock_labels is None:
        return False
    return bool(set(stock_labels.split()).intersection(requested_labels))


def get_business_rows(session: Session, labels: str = '', *, add_id=True) -> QueryResult:
    result = get_ranking_rows(session, 'business')
    if result.error and not result.rows:
        return result

    requested_labels = set(labels.split())
    rows = []

    for row in result.rows:
        stock_labels = None
        code = row.get('code')
        if code:
            label_row = session.query(StockLabels).filter_by(code=code).first()
            if label_row is not None:
                stock_labels = label_row.labels
                row['labels'] = stock_labels

        if not _labels_match(stock_labels, requested_labels):
            continue

        if add_id:
            row = dict(row)
            row['id'] = len(rows) + 1

        rows.append(row)

    return QueryResult(
        rows=rows,
        update_time=result.update_time,
        error=result.error,
    )
