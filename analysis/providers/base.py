# -*- coding: utf-8 -*-

"""Shared helpers for instrument list providers."""

import os
import re


def normalize_stock_code(value):
    """Normalize A-share code to 6-digit string without exchange suffix."""
    if value is None:
        return None
    text = str(value).strip().upper()
    if not text:
        return None
    text = text.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
    if text.isdigit():
        return text.zfill(6)
    match = re.search(r'(\d{6})', text)
    return match.group(1) if match else None


def dataframe_from_code_name_pairs(rows):
    """Build a normalized instrument dataframe from (code, name) pairs."""
    import pandas as pd

    records = []
    for code, name in rows:
        normalized = normalize_stock_code(code)
        if not normalized:
            continue
        records.append({'code': normalized, 'name': (name or normalized)})

    if not records:
        return pd.DataFrame(columns=['code', 'name'])

    frame = pd.DataFrame(records)
    return frame.drop_duplicates(subset=['code']).sort_values('code').reset_index(drop=True)


def read_instruments_csv(csv_path):
    if not csv_path or not os.path.isfile(csv_path):
        return None

    import csv

    pairs = []
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return None
        code_col = 'code' if 'code' in reader.fieldnames else reader.fieldnames[0]
        name_col = 'name' if 'name' in reader.fieldnames else (
            reader.fieldnames[1] if len(reader.fieldnames) > 1 else None
        )
        for row in reader:
            name = row.get(name_col) or row.get(code_col) if name_col else row.get(code_col)
            pairs.append((row.get(code_col), name))

    return dataframe_from_code_name_pairs(pairs)


def code_to_yahoo_symbol(code):
    """Map A-share code to Yahoo Finance ticker (e.g. 600000 -> 600000.SS)."""
    normalized = normalize_stock_code(code)
    if not normalized:
        return None
    # 北交所及新三板（Yahoo 后缀 .BJ）。92xxxx 为北交所新号段，不可映射为 .SS。
    if normalized.startswith('92'):
        return normalized + '.BJ'
    if normalized.startswith(('83', '87', '88', '43')):
        return normalized + '.BJ'
    if normalized.startswith(('4', '8')):
        return normalized + '.BJ'
    if normalized.startswith(('6', '5')):
        return normalized + '.SS'
    if normalized.startswith(('0', '3')):
        return normalized + '.SZ'
    return normalized + '.SS'


def yahoo_symbol_to_code(symbol):
    """Extract 6-digit A-share code from a Yahoo ticker."""
    if not symbol:
        return None
    return normalize_stock_code(str(symbol).split('.')[0])


def codes_from_day_csv_directory(day_dir):
    if not day_dir or not os.path.isdir(day_dir):
        return []

    codes = []
    for filename in os.listdir(day_dir):
        if filename.endswith('.csv'):
            codes.append(filename[:-4])
    return sorted(set(codes))
