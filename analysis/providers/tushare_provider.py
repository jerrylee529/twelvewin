# -*- coding: utf-8 -*-

"""Fetch instrument list via Tushare Pro ``stock_basic``."""

from providers.base import normalize_stock_code
from providers.tushare_pro import TushareProError, get_pro_client, ts_code_to_code


def _is_nan(value):
    try:
        import math
        return isinstance(value, float) and math.isnan(value)
    except (TypeError, ValueError):
        return False


def fetch_instrument_dataframe():
    import pandas as pd

    try:
        pro = get_pro_client()
    except TushareProError as exc:
        print('tushare pro instruments skipped: {}'.format(exc))
        return None

    try:
        frame = pro.stock_basic(
            exchange='',
            list_status='L',
            fields='ts_code,name,area,industry,list_date',
        )
    except Exception as exc:
        print('tushare pro stock_basic failed: {}'.format(repr(exc)))
        return None

    if frame is None or frame.empty:
        return None

    records = []
    for _, row in frame.iterrows():
        code = ts_code_to_code(row.get('ts_code'))
        if not code:
            continue
        records.append({
            'code': code,
            'name': row.get('name'),
            'industry': _nan_to_none(row.get('industry')),
            'area': _nan_to_none(row.get('area')),
            'pe': None,
            'outstanding': None,
            'totals': None,
            'total_assets': None,
            'liquid_assets': None,
            'fixed_assets': None,
            'reserved': None,
            'reserved_per_share': None,
            'esp': None,
            'bvps': None,
            'pb': None,
            'time_2_market': _nan_to_none(row.get('list_date')),
            'undp': None,
            'perundp': None,
            'rev': None,
            'profit': None,
            'gpr': None,
            'npr': None,
            'holders': None,
        })

    result = pd.DataFrame(records)
    if result.empty:
        return None

    result.attrs['provider'] = 'tushare'
    return result


def _nan_to_none(value):
    if value is None:
        return None
    if _is_nan(value):
        return None
    if value != value:
        return None
    return value
