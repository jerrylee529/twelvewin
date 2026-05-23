# -*- coding: utf-8 -*-

"""Ranking data service: Postgres only (CSV fallback in local DEBUG)."""

from app.services.analysis_artifacts import STOCK_RANKING_FILES
from app.services.analysis_access import resolve_published_rows
from app.services.csv_store import CsvReadResult
from app.services.result_store_service import get_ranking_rows_from_db


def get_stock_ranking(config, ranking_key, *, is_anonymous=False) -> CsvReadResult:
    """Return stock ranking rows for the public ranking pages."""
    csv_filename = STOCK_RANKING_FILES.get(ranking_key)
    if csv_filename is None:
        return CsvReadResult(rows=[], path="", error="unknown ranking key")

    max_rows = 20 if is_anonymous else None

    return resolve_published_rows(
        config,
        db_fetch=lambda: get_ranking_rows_from_db(ranking_key, max_rows=max_rows),
        csv_filename=csv_filename,
        csv_kwargs={
            'add_id': True,
            'add_update_time': True,
            'max_rows': max_rows,
        },
    )
