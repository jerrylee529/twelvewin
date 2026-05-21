# -*- coding: utf-8 -*-

"""Python 3 helpers shared by legacy analysis scripts."""


def set_display_precision(digits=2):
    """Compatible with pandas 2.x (``precision`` alone is ambiguous)."""
    import pandas as pd

    pd.set_option('display.precision', digits)


def swap_value(x, y):
    return x if x != 0.00 else y


def apply_close_price(df, trade_col="trade", settlement_col="settlement", close_col="close"):
    """Use last trade when non-zero, otherwise fall back to settlement."""
    import pandas as pd

    trade = pd.to_numeric(df[trade_col], errors="coerce")
    settlement = pd.to_numeric(df[settlement_col], errors="coerce")
    df[close_col] = trade.where(trade != 0, settlement)
    return df
