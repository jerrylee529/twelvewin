# -*- coding: utf-8 -*-

"""Resolve the market end date used for incremental history downloads."""

import logging
from datetime import date

logger = logging.getLogger(__name__)


def resolve_download_end_date(session):
    """Return ``(YYYY-MM-DD, source)`` for the latest market trading day."""
    try:
        from providers.tushare_pro import latest_open_trade_date_iso

        end_date = latest_open_trade_date_iso()
        if end_date:
            return end_date, 'tushare_trade_cal'
    except Exception as exc:
        logger.info('tushare trade_cal unavailable, falling back: %s', exc)

    from core.day_bars import get_global_max_trade_date

    max_date = get_global_max_trade_date(session)
    if max_date is not None:
        return max_date.strftime('%Y-%m-%d'), 'daily_bars_max'

    return date.today().strftime('%Y-%m-%d'), 'calendar_today'
