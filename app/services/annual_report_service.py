# -*- coding: utf-8 -*-

"""Annual stock/industry report rows from Postgres."""

from app.models import AnalysisRun
from app.services.analysis_access import resolve_published_rows
from app.services.csv_store import CsvReadResult, convert_fields
from app.services.result_store_service import (
    get_annual_industry_rows_from_db,
    get_annual_stock_rows_from_db,
)
from core.artifacts import annual_industry_report_filename, annual_stock_report_filename


def get_annual_stock_rows(config, year, *, field_types=None) -> CsvReadResult:
    field_types = field_types or [('change_rate', float), ('amplitude', float)]

    def _transform(row):
        return convert_fields(row, field_types)

    return resolve_published_rows(
        config,
        db_fetch=lambda: get_annual_stock_rows_from_db(year),
        csv_filename=annual_stock_report_filename(year),
        csv_kwargs={
            'add_id': True,
            'add_update_time': True,
            'row_transform': _transform,
        },
    )


def get_annual_industry_rows(config, year, *, field_types=None) -> CsvReadResult:
    field_types = field_types or [('avg_change_rate', float), ('avg_amplitude', float)]

    def _transform(row):
        return convert_fields(row, field_types)

    return resolve_published_rows(
        config,
        db_fetch=lambda: get_annual_industry_rows_from_db(year),
        csv_filename=annual_industry_report_filename(year),
        csv_kwargs={
            'add_id': True,
            'add_update_time': True,
            'row_transform': _transform,
        },
    )


def get_annual_report_update_time(year, *, report_kind='stock'):
    from app.services.result_store_service import get_latest_analysis_run

    category = (
        AnalysisRun.CATEGORY_ANNUAL_STOCK
        if report_kind == 'stock'
        else AnalysisRun.CATEGORY_ANNUAL_INDUSTRY
    )
    run = get_latest_analysis_run(category, str(year))
    if run is not None:
        return run.as_of_date.strftime('%Y-%m-%d')
    return None
