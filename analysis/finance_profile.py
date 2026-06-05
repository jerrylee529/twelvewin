# -*- coding: utf-8 -*-

"""Build stock finance profile payloads from Tushare Pro ``fina_indicator``."""

from __future__ import annotations

import datetime
import json
import math
import os
import time
from typing import Any

from providers.tushare_pro import (
    TushareProError,
    _financial_indicator_periods,
    code_to_ts_code,
    get_pro_client,
)

FINANCE_PROFILE_REPORT_TYPE = 3

FINANCE_PROFILE_FIELDS = (
    'ts_code',
    'end_date',
    'roe',
    'eps',
    'dt_eps',
    'grossprofit_margin',
    'dt_netprofit_yoy',
    'profit_dedt',
)

TUSHARE_TO_PROFILE_FIELDS = {
    'avg_roe': 'roe',
    'basic_eps': 'eps',
    'gross_selling_rate': 'grossprofit_margin',
    'np_atsopc_nrgal_yoy': 'dt_netprofit_yoy',
    'net_profit_after_nrgal_atsolc': 'profit_dedt',
    'np_per_share': 'dt_eps',
}


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value == '':
        return default
    return int(value)


def _env_float(name: str, default: float) -> float:
    value = os.environ.get(name)
    if value is None or value == '':
        return default
    return float(value)


def finance_profile_years() -> int:
    return max(1, _env_int('TW_FINANCE_PROFILE_YEARS', 5))


def finance_profile_sleep_seconds() -> float:
    # Tushare fina_indicator: 200 calls/min -> ~0.30s minimum between requests.
    return max(0.0, _env_float('TW_FINANCE_PROFILE_SLEEP_SEC', 0.35))


def _clean_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number):
        return None
    return number


def period_to_report_date_ms(end_date: str) -> int:
    normalized = str(end_date).strip()
    year = int(normalized[:4])
    month = int(normalized[4:6])
    day = int(normalized[6:8])
    dt = datetime.datetime(year, month, day, 12, 0, 0)
    return int(dt.timestamp() * 1000)


def build_finance_profile_list_item(row: dict[str, Any]) -> dict[str, Any]:
    end_date = str(row.get('end_date') or '').strip()
    if len(end_date) != 8:
        return {}

    item: dict[str, Any] = {'report_date': period_to_report_date_ms(end_date)}
    for target, source in TUSHARE_TO_PROFILE_FIELDS.items():
        value = _clean_number(row.get(source))
        if value is not None:
            item[target] = [value]
    return item


def build_finance_profile_report_data(list_items: list[dict[str, Any]]) -> str:
    return json.dumps({'data': {'list': list_items}}, ensure_ascii=False)


def fetch_finance_profile_list_items(
    code: str,
    *,
    years: int | None = None,
    pro=None,
) -> list[dict[str, Any]]:
    ts_code = code_to_ts_code(code)
    if not ts_code:
        return []

    client = pro or get_pro_client()
    periods = _financial_indicator_periods(years or finance_profile_years())
    pause = finance_profile_sleep_seconds()
    items: list[dict[str, Any]] = []

    for _offset, period in periods:
        if not str(period).endswith('1231'):
            continue
        frame = None
        for attempt in range(2):
            try:
                frame = client.fina_indicator(
                    ts_code=ts_code,
                    period=period,
                    fields=','.join(FINANCE_PROFILE_FIELDS),
                )
                # 增加一条日志
                print('tushare fina_indicator {} {} success'.format(ts_code, period))
                break
            except Exception as exc:
                if attempt == 0 and '频率超限' in str(exc):
                    time.sleep(61)
                    continue
                print('tushare fina_indicator {} {} failed: {}'.format(ts_code, period, repr(exc)))
                frame = None
                break

        if pause > 0:
            time.sleep(pause)

        if frame is None or frame.empty:
            continue

        item = build_finance_profile_list_item(frame.iloc[0].to_dict())
        if item:
            items.append(item)

    items.sort(key=lambda row: row['report_date'])
    return items


def fetch_finance_profile_report_data(
    code: str,
    *,
    years: int | None = None,
    pro=None,
) -> str | None:
    try:
        items = fetch_finance_profile_list_items(code, years=years, pro=pro)
    except TushareProError as exc:
        raise
    except Exception as exc:
        print('finance profile fetch failed for {}: {}'.format(code, repr(exc)))
        return None

    if not items:
        return None
    return build_finance_profile_report_data(items)
