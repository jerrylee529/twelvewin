# -*- coding: utf-8 -*-

"""Market data provider chain for ranking / valuation jobs."""

import os
import time

from providers import akshare_market, tushare_market, yahoo_market
from providers.tushare_pro import get_tushare_token

PROVIDER_ALIASES = {
    'auto': ('akshare', 'yahoo', 'tushare'),
    'ak': ('akshare',),
    'akshare': ('akshare',),
    'yahoo': ('yahoo',),
    'yf': ('yahoo',),
    'tushare': ('tushare',),
    'ts': ('tushare',),
}

_FETCHERS = {
    'akshare': {
        'dividend': akshare_market.fetch_dividend_dataframe,
        'quotes': akshare_market.fetch_today_quotes_dataframe,
        'basics': akshare_market.fetch_stock_basics_dataframe,
        'financial_indicators': lambda **kwargs: None,
    },
    'yahoo': {
        'dividend': yahoo_market.fetch_dividend_dataframe,
        'quotes': yahoo_market.fetch_today_quotes_dataframe,
        'basics': yahoo_market.fetch_stock_basics_dataframe,
        'financial_indicators': lambda **kwargs: None,
    },
    'tushare': {
        'dividend': tushare_market.fetch_dividend_dataframe,
        'quotes': tushare_market.fetch_today_quotes_dataframe,
        'basics': tushare_market.fetch_stock_basics_dataframe,
        'financial_indicators': tushare_market.fetch_financial_indicators_dataframe,
    },
}

_QUOTES_CACHE = {
    'frame': None,
    'fetched_at': 0.0,
}


def _quotes_cache_ttl_sec():
    try:
        return float(os.environ.get('TW_QUOTES_CACHE_TTL_SEC', '900'))
    except (TypeError, ValueError):
        return 900.0


def clear_quotes_cache():
    _QUOTES_CACHE['frame'] = None
    _QUOTES_CACHE['fetched_at'] = 0.0


def _get_cached_quotes():
    frame = _QUOTES_CACHE.get('frame')
    fetched_at = _QUOTES_CACHE.get('fetched_at') or 0.0
    if frame is None or frame.empty:
        return None
    if (time.time() - fetched_at) > _quotes_cache_ttl_sec():
        return None
    return frame


def _store_quotes_cache(frame):
    _QUOTES_CACHE['frame'] = frame
    _QUOTES_CACHE['fetched_at'] = time.time()


def get_market_provider_chain(explicit=None):
    if explicit:
        key = explicit.strip().lower()
    else:
        key = os.environ.get('TW_MARKET_DATA_PROVIDER', 'auto').strip().lower()

    if key == 'auto' and get_tushare_token():
        return ('tushare', 'akshare', 'yahoo')
    return PROVIDER_ALIASES.get(key, (key,))


def _fetch(kind, provider=None, **kwargs):
    errors = []
    for name in get_market_provider_chain(provider):
        fetcher = _FETCHERS.get(name, {}).get(kind)
        if fetcher is None:
            continue
        try:
            frame = fetcher(**kwargs)
            if frame is not None and not frame.empty:
                frame.attrs['provider'] = frame.attrs.get('provider', name)
                return frame
        except Exception as exc:
            errors.append('{}: {}'.format(name, repr(exc)))
            print('market provider {} {} failed: {}'.format(name, kind, repr(exc)))

    if errors:
        print('all market providers failed for {}: {}'.format(kind, '; '.join(errors)))
    return None


def fetch_dividend_dataframe(provider=None, report_date=None):
    return _fetch('dividend', provider=provider, report_date=report_date)


def fetch_today_quotes_dataframe(provider=None, *, enrich=True, use_cache=True):
    if use_cache:
        cached = _get_cached_quotes()
        if cached is not None:
            return cached

    frame = _fetch('quotes', provider=provider, enrich=enrich)
    if frame is not None and not frame.empty:
        _store_quotes_cache(frame)
    return frame


def fetch_today_quotes_with_retry(
    *,
    max_attempts=3,
    backoff_sec=None,
    provider=None,
    enrich=True,
    use_cache=True,
):
    if backoff_sec is None:
        try:
            backoff_sec = float(os.environ.get('TW_QUOTES_RETRY_BACKOFF_SEC', '30'))
        except (TypeError, ValueError):
            backoff_sec = 30.0

    errors = []
    for attempt in range(1, max_attempts + 1):
        try:
            frame = fetch_today_quotes_dataframe(
                provider=provider,
                enrich=enrich,
                use_cache=use_cache and attempt == 1,
            )
            if frame is not None and not frame.empty:
                return frame
            errors.append('attempt {}: empty response'.format(attempt))
        except Exception as exc:
            errors.append('attempt {}: {}'.format(attempt, repr(exc)))

        if attempt < max_attempts:
            time.sleep(backoff_sec * attempt)

    print('spot quotes unavailable after {} attempts: {}'.format(max_attempts, '; '.join(errors)))
    return None


def fetch_stock_basics_dataframe(provider=None):
    return _fetch('basics', provider=provider)


def fetch_financial_indicators_dataframe(provider=None, codes=None):
    return _fetch('financial_indicators', provider=provider, codes=codes)
