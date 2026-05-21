# coding=utf8

"""行情数据获取封装（Tushare Pro）。

get_history_data() 使用 ``pro_bar`` / ``index_daily`` / ``daily`` 替代旧版 ``get_k_data``。
"""

__author__ = 'Administrator'

import pandas as pd
import text

from providers.tushare_pro import (
    TushareProError,
    code_to_ts_code,
    get_pro_client,
    pro_bar_to_legacy_kline,
)


def _normalize_dates(start, end):
    start_s = (start or '').replace('-', '')[:8]
    end_s = (end or '').replace('-', '')[:8]
    return start_s, end_s


def _freq_from_ktype(ktype):
    mapping = {
        'D': 'D',
        'W': 'W',
        'M': 'M',
        '5': '5min',
        '15': '15min',
        '30': '30min',
        '60': '60min',
    }
    return mapping.get(ktype, 'D')


def _adj_from_autype(autype):
    if autype in (None, '', 'None', 'none'):
        return None
    if autype in ('qfq', 'hfq'):
        return autype
    return 'qfq'


def get_history_data(code, start, end, ktype='D', autype='qfq', index=False):
    """Download OHLCV history compatible with legacy ``get_k_data`` output."""
    df = pd.DataFrame()

    try:
        import tushare as ts

        pro = get_pro_client()
        start_s, end_s = _normalize_dates(start, end)
        ts_code = code_to_ts_code(code)

        if index:
            ts_code = code if '.' in str(code) else code_to_ts_code(code)
            raw = pro.index_daily(
                ts_code=ts_code,
                start_date=start_s,
                end_date=end_s,
                fields='ts_code,trade_date,open,high,low,close,vol',
            )
            df = pro_bar_to_legacy_kline(raw)
            if not df.empty and 'code' not in df.columns:
                df['code'] = code
            return df

        if not ts_code:
            return df

        freq = _freq_from_ktype(ktype)
        adj = _adj_from_autype(autype)

        if freq == 'D' and adj in (None, 'qfq', 'hfq'):
            raw = ts.pro_bar(
                ts_code=ts_code,
                start_date=start_s,
                end_date=end_s,
                freq='D',
                adj=adj or 'qfq',
                asset='E',
            )
            df = pro_bar_to_legacy_kline(raw)
        else:
            raw = ts.pro_bar(
                ts_code=ts_code,
                start_date=start_s,
                end_date=end_s,
                freq=freq,
                adj=adj,
                asset='E',
            )
            df = pro_bar_to_legacy_kline(raw)

        if not df.empty and 'code' not in df.columns:
            df['code'] = code

    except TushareProError as exc:
        print('Tushare Pro unavailable for {}: {}'.format(code, exc))
        text.send_text("获取历史数据失败(Tushare token), %s" % code)
    except Exception as exc:
        print('Exception:', repr(exc))
        text.send_text("获取历史数据失败, %s" % code)

    return df


def get_realtime_data():
    pass
