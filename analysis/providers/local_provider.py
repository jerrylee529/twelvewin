# -*- coding: utf-8 -*-

"""Load instrument codes from local instruments.csv or day-data CSV filenames."""

import os

from config import config
from providers.base import (
    codes_from_day_csv_directory,
    dataframe_from_code_name_pairs,
    read_instruments_csv,
)


def _day_file_path():
    path = config.get('DAY_FILE_PATH') or ''
    if path and not path.endswith(os.sep):
        path = path + os.sep
    return path


def _instruments_csv_path():
    day_dir = _day_file_path()
    explicit = os.path.join(day_dir, 'instruments.csv')
    if os.path.isfile(explicit):
        return explicit
    return explicit


def fetch_from_instruments_csv():
    path = _instruments_csv_path()
    frame = read_instruments_csv(path)
    if frame is not None and not frame.empty:
        frame.attrs['provider'] = 'local_csv'
    return frame


def fetch_from_day_csv_directory():
    day_dir = _day_file_path()
    codes = codes_from_day_csv_directory(day_dir)
    if not codes:
        return None

    frame = dataframe_from_code_name_pairs([(code, code) for code in codes])
    frame.attrs['provider'] = 'day_csv'
    return frame


def fetch_instrument_dataframe():
    frame = fetch_from_instruments_csv()
    if frame is not None and not frame.empty:
        return frame
    return fetch_from_day_csv_directory()
