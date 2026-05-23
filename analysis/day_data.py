# -*- coding: utf-8 -*-

"""Load instruments and daily bars from Postgres for offline analysis."""

import os
import sys

_ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_ANALYSIS_DIR, '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from core.db import session_scope
from core.day_bars import load_bars_dataframe, get_last_trade_date
from core.schema import ensure_analysis_schema


def _write_day_csv_enabled():
    value = os.environ.get('TW_WRITE_DAY_CSV', '')
    return str(value).lower() in ('1', 'true', 'yes', 'on')


def load_instruments_dataframe(*, include_industry=False):
    """Instrument list from database."""
    from instruments import load_instruments_dataframe as _load

    ensure_analysis_schema()
    return _load(include_industry=include_industry)


def load_day_dataframe(code, session=None):
    """OHLCV history for one code in legacy CSV column layout."""
    if session is not None:
        return load_bars_dataframe(session, code)

    ensure_analysis_schema()
    with session_scope() as sess:
        return load_bars_dataframe(sess, code)


def day_data_available(code, session=None):
    if session is not None:
        return get_last_trade_date(session, code) is not None

    ensure_analysis_schema()
    with session_scope() as sess:
        return get_last_trade_date(sess, code) is not None


def write_day_csv_enabled():
    return _write_day_csv_enabled()
