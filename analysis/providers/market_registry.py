# -*- coding: utf-8 -*-

"""Market data provider chain for ranking / valuation jobs."""

import os

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


def fetch_today_quotes_dataframe(provider=None, *, enrich=True):
    return _fetch('quotes', provider=provider, enrich=enrich)


def fetch_stock_basics_dataframe(provider=None):
    return _fetch('basics', provider=provider)


def fetch_financial_indicators_dataframe(provider=None, codes=None):
    return _fetch('financial_indicators', provider=provider, codes=codes)
