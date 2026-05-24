# coding=utf8

"""Compute interval price change and amplitude reports."""

import datetime
import logging
import os
import sys

import pandas as pd

from config import config
from instruments import get_all_instrument_codes_before

_ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, _ANALYSIS_DIR)

from compat import set_display_precision
from core.db import session_scope
from csv_output import atomic_export_pair, get_result_path
from day_data import load_day_since_dataframe, load_instruments_dataframe
from result_export import export_price_change_report

set_display_precision(2)
logger = logging.getLogger(__name__)

PRICE_CHANGE_COLUMNS = ('date', 'high', 'low', 'close')


class PriceChangePeriod(object):
    """One interval used for price change statistics."""

    def __init__(self):
        self.begin_date = ""
        self.end_date = ""
        self.title = ""


def price_change(df, begin_date, end_date):
    window = df[(df['date'] >= begin_date) & (df['date'] <= end_date)]

    rate = -9999
    update_date = None
    close = -9999
    if not window.empty:
        first_row = window.iloc[0]
        last_row = window.iloc[-1]
        rate = (last_row['close'] - first_row['close']) * 100 / first_row['close']
        close = first_row['close']
        update_date = last_row['date']

    return rate, close, update_date


def price_amplitude(df, begin_date, end_date):
    result = df[(df['date'] >= begin_date) & (df['date'] <= end_date)].copy()
    result['amplitude'] = (result['high'] - result['low']) * 100 / result['low']
    return result


def compute_all_instruments(instrument_filename, day_file_path, result_file_path, periods):
    instruments = load_instruments_dataframe()

    if instruments is None or instruments.empty:
        logger.warning('Could not find any instruments, exit')
        return

    instruments = instruments.copy()
    instruments['code'] = instruments['code'].astype(str)
    instruments['close'] = None
    instruments['update_time'] = None

    for period in periods:
        instruments[period.title] = -9999

    min_begin_date = min(period.begin_date for period in periods)
    code_to_index = {code: index for index, code in enumerate(instruments['code'])}

    with session_scope() as session:
        total = len(instruments)
        for index, code in enumerate(instruments['code'], start=1):
            if index % 500 == 0 or index == total:
                logger.info('price change: %d / %d', index, total)

            try:
                df = load_day_since_dataframe(
                    code,
                    session=session,
                    since_date=min_begin_date,
                    columns=PRICE_CHANGE_COLUMNS,
                )
                if df.empty:
                    continue

                row_index = code_to_index[code]
                for period in periods:
                    rate, close, update_time = price_change(
                        df,
                        period.begin_date,
                        period.end_date,
                    )
                    instruments.at[row_index, period.title] = rate
                    instruments.at[row_index, 'close'] = close
                    instruments.at[row_index, 'update_time'] = update_time
            except Exception as exc:
                logger.warning('price change failed for %s: %s', code, exc)
                continue

    export_price_change_report(instruments)
    return instruments


def compute_all_instruments_amplitude(period):
    instruments = get_all_instrument_codes_before(20190101)

    if instruments is None:
        logger.warning('Could not find any instruments, exit')
        return

    result = pd.DataFrame()
    result['close'] = None
    result['update_time'] = None
    result[period.title] = -9999
    result['amp_std'] = None
    result['code'] = instruments

    code_to_index = {code: index for index, code in enumerate(instruments)}

    with session_scope() as session:
        total = len(instruments)
        for index, code in enumerate(instruments, start=1):
            if index % 500 == 0 or index == total:
                logger.info('price amplitude: %d / %d', index, total)

            try:
                df = load_day_since_dataframe(
                    code,
                    session=session,
                    since_date=period.begin_date,
                    columns=PRICE_CHANGE_COLUMNS,
                )
                if df.empty:
                    continue

                df_amp = price_amplitude(df, period.begin_date, period.end_date)
                row_index = code_to_index[code]
                result.at[row_index, 'close'] = df.iloc[-1]['close']
                result.at[row_index, 'update_time'] = df.iloc[-1]['date']
                result.at[row_index, period.title] = df_amp['amplitude'].mean()
                result.at[row_index, 'amp_std'] = df_amp['amplitude'].std()
            except Exception as exc:
                logger.warning('price amplitude failed for %s: %s', code, exc)
                continue

    atomic_export_pair(
        result,
        get_result_path(config),
        "price_amplitude",
        date_suffix=datetime.date.today().strftime('%Y-%m-%d'),
        index=False,
        float_format='%.2f',
    )

    return result


if __name__ == '__main__':
    today = datetime.date.today()
    days_list = [7, 30, 30 * 3, 30 * 6, 30 * 12]

    periods = []
    for days in days_list:
        period = PriceChangePeriod()
        period.begin_date = (datetime.date.today() + datetime.timedelta(days=-days)).strftime('%Y-%m-%d')
        period.end_date = today.strftime('%Y-%m-%d')
        period.title = 'rate' + str(days)
        periods.append(period)

    result = compute_all_instruments(
        config.INSTRUMENT_FILENAME,
        config.DAY_FILE_PATH,
        config.RESULT_PATH,
        periods,
    )
    print(result)
