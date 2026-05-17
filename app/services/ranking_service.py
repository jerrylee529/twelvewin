# -*- coding: utf-8 -*-

"""Ranking data service backed by generated CSV artifacts."""

from app.services.csv_store import CsvReadResult, read_rows


STOCK_RANKING_FILES = {
    'pe': 'stock_pe.csv',
    'pb': 'stock_pb.csv',
    'roe': 'stock_roe.csv',
    'divi': 'stock_dividence.csv',
}


def get_stock_ranking(config, ranking_key, *, is_anonymous=False) -> CsvReadResult:
    """Return stock ranking rows for the public ranking pages."""
    csv_filename = STOCK_RANKING_FILES.get(ranking_key)
    if csv_filename is None:
        return CsvReadResult(rows=[], path="", error="unknown ranking key")

    max_rows = 20 if is_anonymous else None
    return read_rows(
        config['RESULT_PATH'],
        csv_filename,
        add_id=True,
        add_update_time=True,
        max_rows=max_rows,
    )
