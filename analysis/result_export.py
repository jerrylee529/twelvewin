# -*- coding: utf-8 -*-

"""Publish analysis outputs to Postgres; optional CSV backup via TW_WRITE_RESULT_CSV."""

import os
import sys
from datetime import date

_ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_ANALYSIS_DIR, '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from compute.publish import (
    publish_annual_industry_dataframe,
    publish_annual_stock_dataframe,
    publish_price_change_dataframe,
    publish_ranking_by_title,
    publish_screen_by_basename,
)
from core.artifacts import annual_industry_report_filename, annual_stock_report_filename
from core.schema import ensure_analysis_schema
from csv_output import atomic_export_pair, get_result_path
from jobs.io import atomic_dataframe_to_csv


def _write_result_csv_enabled():
    return os.environ.get('TW_WRITE_RESULT_CSV', '').lower() in ('1', 'true', 'yes', 'on')


def export_ranking_report(dataframe, title, *, config=None):
    """Publish ranking rows to DB; optionally mirror to CSV."""
    ensure_analysis_schema()
    summary = publish_ranking_by_title(dataframe, title)

    if _write_result_csv_enabled():
        result_path = get_result_path(config)
        if result_path:
            atomic_export_pair(
                dataframe,
                result_path,
                title,
                date_suffix=date.today().strftime('%Y%m%d'),
                encoding='utf-8',
                index=False,
                float_format='%.2f',
            )

    return summary


def export_screen_report(dataframe, basename, *, config=None, required_columns=None):
    """Publish technical screen rows to DB; optionally mirror to CSV."""
    ensure_analysis_schema()
    summary = publish_screen_by_basename(dataframe, basename)

    if _write_result_csv_enabled():
        result_path = get_result_path(config)
        if result_path:
            atomic_export_pair(
                dataframe,
                result_path,
                basename,
                date_suffix=date.today().strftime('%Y-%m-%d'),
                required_columns=required_columns,
                index=False,
                float_format='%.2f',
            )

    return summary


def export_price_change_report(dataframe, *, config=None):
    ensure_analysis_schema()
    summary = publish_price_change_dataframe(
        dataframe,
        source_file='price_change.csv',
    )

    if _write_result_csv_enabled():
        result_path = get_result_path(config)
        if result_path:
            atomic_export_pair(
                dataframe,
                result_path,
                'price_change',
                date_suffix=date.today().strftime('%Y-%m-%d'),
                index=False,
                float_format='%.2f',
            )

    return summary


def export_annual_stock_report(dataframe, year, *, config=None):
    ensure_analysis_schema()
    summary = publish_annual_stock_dataframe(dataframe, year)

    if _write_result_csv_enabled():
        result_path = get_result_path(config)
        if result_path:
            path = os.path.join(result_path, annual_stock_report_filename(year))
            atomic_dataframe_to_csv(
                dataframe,
                path,
                index=False,
                float_format='%.2f',
            )

    return summary


def export_annual_industry_report(dataframe, year, *, config=None):
    ensure_analysis_schema()
    summary = publish_annual_industry_dataframe(dataframe, year)

    if _write_result_csv_enabled():
        result_path = get_result_path(config)
        if result_path:
            path = os.path.join(result_path, annual_industry_report_filename(year))
            atomic_dataframe_to_csv(
                dataframe,
                path,
                index=False,
                float_format='%.2f',
            )

    return summary
