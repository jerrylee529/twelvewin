# -*- coding: utf-8 -*-

"""Business stock ranking service."""

from app.services.analysis_access import resolve_published_rows
from app.services.csv_store import CsvReadResult
from app.services.result_store_service import get_ranking_rows_from_db


def _labels_match(stock_labels, requested_labels):
    if not requested_labels:
        return True
    if stock_labels is None:
        return False

    stock_label_set = set(stock_labels.split())
    return bool(stock_label_set.intersection(requested_labels))


def get_business_rows(config, labels="", *, label_lookup=None, add_id=True) -> CsvReadResult:
    """Read business ranking from DB; CSV only when CSV_DEV_FALLBACK is enabled."""
    result = resolve_published_rows(
        config,
        db_fetch=lambda: get_ranking_rows_from_db('business'),
        csv_filename='stock_business.csv',
        csv_kwargs={'add_id': False, 'add_update_time': True},
    )

    requested_labels = set(labels.split())
    rows = []

    for row in result.rows:
        stock_labels = None

        if label_lookup is not None:
            stock_labels = label_lookup(row.get('code'))

        if stock_labels is not None:
            row['labels'] = stock_labels

        if not _labels_match(stock_labels, requested_labels):
            continue

        if add_id:
            row['id'] = len(rows) + 1

        rows.append(row)

    return CsvReadResult(
        rows=rows,
        path=result.path,
        update_time=result.update_time,
        missing=result.missing,
        error=result.error,
    )
