# -*- coding: utf-8 -*-

"""Ensure analysis-related DB tables exist before offline jobs run."""

from core.schema import (  # noqa: F401
    REQUIRED_ANALYSIS_TABLES,
    ensure_analysis_schema,
    missing_analysis_tables,
)
