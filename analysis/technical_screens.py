# -*- coding: utf-8 -*-

"""Pure technical screen predicates used by offline analysis jobs."""

import pandas as pd


def _rolling_mean_or_zero(series, window):
    value = series.rolling(window=window).mean().iloc[-1]
    if pd.isna(value):
        return 0.0
    return float(value)


def match_ma_long(df, ma1=5, ma2=10, ma3=20):
    if df.empty:
        return None

    closes = df['close']
    ma_short = _rolling_mean_or_zero(closes, ma1)
    ma_mid = _rolling_mean_or_zero(closes, ma2)
    ma_long = _rolling_mean_or_zero(closes, ma3)
    if ma_short > ma_mid > ma_long:
        return float(closes.iloc[-1])
    return None


def match_break_ma(df, ma1=20):
    if df.empty:
        return None

    ma_price = _rolling_mean_or_zero(df['close'], ma1)
    last_row = df.iloc[-1]
    if ma_price >= last_row['open'] and ma_price <= last_row['close']:
        return float(last_row['close'])
    return None


def match_above_ma(df, ma1=250):
    if df.empty:
        return None

    ma_price = _rolling_mean_or_zero(df['close'], ma1)
    last_close = float(df['close'].iloc[-1])
    if ma_price <= last_close:
        return last_close
    return None
