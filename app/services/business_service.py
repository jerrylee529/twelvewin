# -*- coding: utf-8 -*-

"""Business stock ranking service."""

from app.services.csv_store import CsvReadResult, read_rows
from app.services.result_store_service import (
    get_ranking_rows_from_db,
    read_analysis_from_db_enabled,
)


def _labels_match(stock_labels, requested_labels):
    if not requested_labels:
        return True
    if stock_labels is None:
        return False

    stock_label_set = set(stock_labels.split())
    return bool(stock_label_set.intersection(requested_labels))


def get_business_rows(config, labels="", *, label_lookup=None, add_id=True) -> CsvReadResult:
    """Read stock_business.csv and merge optional DB-backed labels."""
    if read_analysis_from_db_enabled(config):
        db_result = get_ranking_rows_from_db('business')
        if db_result is not None and db_result.rows:
            result = db_result
        else:
            result = read_rows(config['RESULT_PATH'], 'stock_business.csv')
    else:
        result = read_rows(config['RESULT_PATH'], 'stock_business.csv')
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
