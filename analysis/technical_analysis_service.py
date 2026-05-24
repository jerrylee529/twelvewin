# coding=utf8

"""End-of-day technical screen generation and publish service."""

__author__ = 'Administrator'

import logging

import pandas as pd

from datetime import timedelta, date

from config import config
from price_change_analysis import (
    PriceChangePeriod,
    compute_all_instruments,
    compute_all_instruments_amplitude,
)

from compat import set_display_precision
from core.db import session_scope
from core.day_bars import scan_historic_extreme_codes
from day_data import load_day_tail_dataframe, load_instruments_dataframe
from result_export import export_screen_report
from technical_screens import match_above_ma, match_break_ma, match_ma_long

set_display_precision(2)

logger = logging.getLogger(__name__)

SCREEN_RESULT_COLUMNS = ('code', 'name', 'close')
MA_TAIL_LIMIT = 250
MA_LONG_WINDOWS = (5, 10, 20)
BREAK_MA_WINDOW = 20
ABOVE_MA_WINDOW = 250

SCREEN_DEFINITIONS = (
    ('highest_in_history', 'highest'),
    ('lowest_in_history', 'lowest'),
    ('ma_long', 'ma_long'),
    ('break_ma', 'break_ma'),
    ('above_ma', 'above_ma'),
)


def _load_instruments():
    instruments = load_instruments_dataframe()
    if instruments is None or instruments.empty:
        logger.warning('Could not find any instruments, exit')
        return None
    instruments = instruments.copy()
    instruments['code'] = instruments['code'].astype(str)
    if 'name' not in instruments.columns:
        instruments['name'] = instruments['code']
    return instruments


def _write_screen_results(instruments, result_file_path, basename):
    instruments = instruments.copy()
    instruments['close'] = instruments['close'].astype('float64')
    return export_screen_report(
        instruments,
        basename,
        required_columns=SCREEN_RESULT_COLUMNS,
    )


def _rows_from_extreme_map(extreme_map, name_by_code):
    rows = []
    for code, close in extreme_map.items():
        name = name_by_code.get(code)
        if name is None:
            continue
        rows.append({'code': code, 'name': name, 'close': close})
    return rows


def _publish_rows(rows, result_file_path, basename):
    if not rows:
        logger.info('No qualified data for %s', basename)
        return None
    return _write_screen_results(pd.DataFrame(rows), result_file_path, basename)


def run_all_technical_screens(instrument_filename, day_file_path, result_file_path):
    """Run all technical screens in one DB session and publish results."""
    instruments = _load_instruments()
    if instruments is None:
        return {}

    name_by_code = dict(zip(instruments['code'], instruments['name']))
    valid_codes = set(name_by_code.keys())
    results = {basename: [] for basename, _ in SCREEN_DEFINITIONS}
    total = len(instruments)

    with session_scope() as session:
        high_map = scan_historic_extreme_codes(session, 'high')
        low_map = scan_historic_extreme_codes(session, 'low')
        results['highest_in_history'] = _rows_from_extreme_map(
            {code: close for code, close in high_map.items() if code in valid_codes},
            name_by_code,
        )
        results['lowest_in_history'] = _rows_from_extreme_map(
            {code: close for code, close in low_map.items() if code in valid_codes},
            name_by_code,
        )

        tail_columns = ('date', 'open', 'close')
        for index, code in enumerate(instruments['code'], start=1):
            if index % 500 == 0 or index == total:
                logger.info('technical screens: %d / %d', index, total)

            df = load_day_tail_dataframe(
                code,
                session=session,
                limit=MA_TAIL_LIMIT,
                columns=tail_columns,
            )
            if df.empty:
                continue

            name = name_by_code[code]
            close = match_ma_long(df, *MA_LONG_WINDOWS)
            if close is not None:
                results['ma_long'].append({'code': code, 'name': name, 'close': close})

            close = match_break_ma(df, BREAK_MA_WINDOW)
            if close is not None:
                results['break_ma'].append({'code': code, 'name': name, 'close': close})

            close = match_above_ma(df, ABOVE_MA_WINDOW)
            if close is not None:
                results['above_ma'].append({'code': code, 'name': name, 'close': close})

    published = {}
    for basename, _result_key in SCREEN_DEFINITIONS:
        summary = _publish_rows(results[basename], result_file_path, basename)
        if summary is not None:
            published[basename] = summary
    return published


def highest_in_history(instrument_filename, day_file_path, result_file_path):
    instruments = _load_instruments()
    if instruments is None:
        return

    name_by_code = dict(zip(instruments['code'], instruments['name']))
    valid_codes = set(name_by_code.keys())
    with session_scope() as session:
        high_map = scan_historic_extreme_codes(session, 'high')
    rows = _rows_from_extreme_map(
        {code: close for code, close in high_map.items() if code in valid_codes},
        name_by_code,
    )
    _publish_rows(rows, result_file_path, 'highest_in_history')


def lowest_in_history(instrument_filename, day_file_path, result_file_path):
    instruments = _load_instruments()
    if instruments is None:
        return

    name_by_code = dict(zip(instruments['code'], instruments['name']))
    valid_codes = set(name_by_code.keys())
    with session_scope() as session:
        low_map = scan_historic_extreme_codes(session, 'low')
    rows = _rows_from_extreme_map(
        {code: close for code, close in low_map.items() if code in valid_codes},
        name_by_code,
    )
    _publish_rows(rows, result_file_path, 'lowest_in_history')


def ma_long_history(instrument_filename, day_file_path, result_file_path, ma1, ma2, ma3):
    instruments = _load_instruments()
    if instruments is None:
        return

    rows = []
    with session_scope() as session:
        for code, name in zip(instruments['code'], instruments['name']):
            df = load_day_tail_dataframe(
                code,
                session=session,
                limit=MA_TAIL_LIMIT,
                columns=('date', 'open', 'close'),
            )
            close = match_ma_long(df, ma1, ma2, ma3)
            if close is not None:
                rows.append({'code': code, 'name': name, 'close': close})
    _publish_rows(rows, result_file_path, 'ma_long')


def break_ma(instrument_filename, day_file_path, result_file_path, ma1):
    instruments = _load_instruments()
    if instruments is None:
        return

    rows = []
    with session_scope() as session:
        for code, name in zip(instruments['code'], instruments['name']):
            df = load_day_tail_dataframe(
                code,
                session=session,
                limit=MA_TAIL_LIMIT,
                columns=('date', 'open', 'close'),
            )
            close = match_break_ma(df, ma1)
            if close is not None:
                rows.append({'code': code, 'name': name, 'close': close})
    _publish_rows(rows, result_file_path, 'break_ma')


def above_ma(instrument_filename, day_file_path, result_file_path, ma1):
    instruments = _load_instruments()
    if instruments is None:
        return

    rows = []
    with session_scope() as session:
        for code, name in zip(instruments['code'], instruments['name']):
            df = load_day_tail_dataframe(
                code,
                session=session,
                limit=MA_TAIL_LIMIT,
                columns=('date', 'open', 'close'),
            )
            close = match_above_ma(df, ma1)
            if close is not None:
                rows.append({'code': code, 'name': name, 'close': close})
    _publish_rows(rows, result_file_path, 'above_ma')


def price_change_computer(instrument_filename, day_file_path, result_file_path):
    today = date.today()
    days_list = [7, 30, 30 * 3, 30 * 6, 30 * 12]

    periods = []
    for days in days_list:
        period = PriceChangePeriod()
        period.begin_date = (date.today() + timedelta(days=-days)).strftime('%Y-%m-%d')
        period.end_date = today.strftime('%Y-%m-%d')
        period.title = 'rate' + str(days)
        periods.append(period)

    result = compute_all_instruments(instrument_filename, day_file_path, result_file_path, periods)
    logger.info('price change rows: %s', len(result) if result is not None else 0)
    return result


def price_amplitude_computer(days):
    today = date.today()
    period = PriceChangePeriod()
    period.begin_date = (date.today() + timedelta(days=-days)).strftime('%Y-%m-%d')
    period.end_date = today.strftime('%Y-%m-%d')
    period.title = 'amp_' + str(days)

    result = compute_all_instruments_amplitude(period)
    logger.info('price amplitude rows: %s', len(result) if result is not None else 0)
    return result


if __name__ == '__main__':
    run_all_technical_screens(
        instrument_filename=config.INSTRUMENT_FILENAME,
        day_file_path=config.DAY_FILE_PATH,
        result_file_path=config.RESULT_PATH,
    )
