# -*- coding: utf-8 -*-

"""Ranking data service: Postgres first, CSV fallback."""

from app.services.analysis_artifacts import STOCK_RANKING_FILES
from app.services.csv_store import CsvReadResult, read_rows
from app.services.result_store_service import (
    get_ranking_rows_from_db,
    read_analysis_from_db_enabled,
)


def get_stock_ranking(config, ranking_key, *, is_anonymous=False) -> CsvReadResult:
    """Return stock ranking rows for the public ranking pages."""
    csv_filename = STOCK_RANKING_FILES.get(ranking_key)
    if csv_filename is None:
        return CsvReadResult(rows=[], path="", error="unknown ranking key")

    max_rows = 20 if is_anonymous else None

    if read_analysis_from_db_enabled(config):
        db_result = get_ranking_rows_from_db(ranking_key, max_rows=max_rows)
        if db_result is not None and db_result.rows:
            return db_result

    return read_rows(
        config['RESULT_PATH'],
        csv_filename,
        add_id=True,
        add_update_time=True,
        max_rows=max_rows,
    )
