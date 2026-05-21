# -*- coding: utf-8 -*-

"""Fetch A-share instrument list via AkShare (POC)."""

from providers.base import dataframe_from_code_name_pairs, normalize_stock_code


def fetch_instrument_dataframe():
    import akshare as ak

    frame = ak.stock_info_a_code_name()
    if frame is None or frame.empty:
        return None

    code_col = 'code' if 'code' in frame.columns else frame.columns[0]
    name_col = 'name' if 'name' in frame.columns else frame.columns[1]

    pairs = []
    for _, row in frame.iterrows():
        code = normalize_stock_code(row[code_col])
        if not code:
            continue
        pairs.append((code, row[name_col]))

    result = dataframe_from_code_name_pairs(pairs)
    if result.empty:
        return None

    result.attrs['provider'] = 'akshare'
    return result
