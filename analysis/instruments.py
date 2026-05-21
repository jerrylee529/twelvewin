# coding=utf8

"""股票基础信息入库和代码查询工具。

get_instrument_list() 按 TW_DATA_PROVIDER 链拉取列表（默认：AkShare → tushare → 本地 CSV/日线目录），
失败时使用数据库已有记录；结果写入 Instrument 表并导出 instruments.csv。
"""

__author__ = 'Administrator'

import os

import numpy as np
import pandas as pd
from sqlalchemy import and_, cast, Integer

from config import config
from models import Instrument, Session
from providers.base import (
    codes_from_day_csv_directory,
    dataframe_from_code_name_pairs,
    read_instruments_csv,
)
from providers.registry import fetch_instrument_dataframe as fetch_remote_instruments


def value_2_float(value):
    if value is None:
        return None
    if isinstance(value, float) and np.isnan(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def nan_2_none(value):
    if value is None:
        return None
    if isinstance(value, float) and np.isnan(value):
        return None
    if value != value:
        return None
    return value


def _day_file_path():
    path = config.get('DAY_FILE_PATH') or ''
    if path and not path.endswith(os.sep):
        path = path + os.sep
    return path


def _instruments_csv_path():
    return os.path.join(_day_file_path(), 'instruments.csv')


def _load_from_database_dataframe():
    session = Session()
    try:
        rows = session.query(Instrument.code, Instrument.name).all()
    finally:
        session.close()

    if not rows:
        return None

    frame = dataframe_from_code_name_pairs(rows)
    frame.attrs['provider'] = 'database'
    return frame


def _load_from_local_fallback():
    path = _instruments_csv_path()
    frame = read_instruments_csv(path)
    if frame is not None and not frame.empty:
        frame.attrs['provider'] = 'local_csv'
        return frame

    codes = codes_from_day_csv_directory(_day_file_path())
    if not codes:
        return None

    frame = dataframe_from_code_name_pairs([(code, code) for code in codes])
    frame.attrs['provider'] = 'day_csv'
    return frame


def _instrument_from_row(row):
    return Instrument(
        str(row['code']),
        row.get('name') or str(row['code']),
        nan_2_none(row.get('industry')),
        nan_2_none(row.get('area')),
        value_2_float(row.get('pe')),
        value_2_float(row.get('outstanding')),
        value_2_float(row.get('totals')),
        value_2_float(row.get('total_assets')),
        value_2_float(row.get('liquid_assets')),
        value_2_float(row.get('fixed_assets')),
        value_2_float(row.get('reserved')),
        value_2_float(row.get('reserved_per_share')),
        value_2_float(row.get('esp')),
        value_2_float(row.get('bvps')),
        value_2_float(row.get('pb')),
        nan_2_none(row.get('time_2_market')),
        value_2_float(row.get('undp')),
        value_2_float(row.get('perundp')),
        value_2_float(row.get('rev')),
        value_2_float(row.get('profit')),
        value_2_float(row.get('gpr')),
        value_2_float(row.get('npr')),
        value_2_float(row.get('holders')),
    )


def persist_instrument_dataframe(frame):
    session = Session()
    existing = {item[0] for item in session.query(Instrument.code).all()}
    added = 0

    try:
        for _, row in frame.iterrows():
            code = str(row.get('code', '')).strip()
            if not code or code in existing:
                continue
            session.add(_instrument_from_row(row))
            existing.add(code)
            added += 1
        session.commit()
    finally:
        session.close()

    return added


def export_instruments_csv(frame, csv_path=None):
    csv_path = csv_path or _instruments_csv_path()
    directory = os.path.dirname(os.path.abspath(csv_path))
    os.makedirs(directory, exist_ok=True)

    export_frame = frame[['code', 'name']].copy() if 'name' in frame.columns else frame[['code']].copy()
    if 'name' not in export_frame.columns:
        export_frame['name'] = export_frame['code']

    export_frame.to_csv(csv_path, index=False, encoding='utf-8-sig')
    return csv_path


def get_instrument_list(provider=None):
    """
    获取股票列表并保存到数据库；返回使用的 dataframe（含 attrs['provider']）。
    """
    frame = fetch_remote_instruments(provider=provider)

    if frame is None or frame.empty:
        frame = _load_from_local_fallback()

    if frame is None or frame.empty:
        frame = _load_from_database_dataframe()

    if frame is None or frame.empty:
        print('No instrument list available from providers, local files, or database')
        return None

    provider_name = frame.attrs.get('provider', 'unknown')
    added = persist_instrument_dataframe(frame)
    csv_path = export_instruments_csv(frame)

    print(
        'instrument list loaded via {}, rows={}, newly_inserted={}, csv={}'.format(
            provider_name,
            len(frame),
            added,
            csv_path,
        )
    )
    return frame


def get_all_instrument_codes():
    """优先数据库；为空时回退本地 instruments.csv 或 day_data 下的 CSV 文件名。"""
    session = Session()
    try:
        codes = [item[0] for item in session.query(Instrument.code).all()]
    finally:
        session.close()

    if codes:
        return codes

    frame = _load_from_local_fallback()
    if frame is not None and not frame.empty:
        return frame['code'].tolist()

    return []


def get_all_instrument_codes_before(timeToMarket):
    session = Session()
    try:
        codes = [
            item[0]
            for item in session.query(Instrument.code).filter(
                and_(
                    cast(Instrument.time_2_market, Integer) < timeToMarket,
                    Instrument.time_2_market != '0',
                    Instrument.time_2_market != None,
                )
            ).all()
        ]
    finally:
        session.close()

    return codes


if __name__ == '__main__':
    get_instrument_list()
