# -*- coding: utf-8 -*-

"""Select and invoke instrument list providers."""

import os

from providers import akshare_provider, local_provider, tushare_provider
from providers.tushare_pro import get_tushare_token

PROVIDER_ALIASES = {
    'auto': ('akshare', 'tushare', 'local'),
    'ak': ('akshare',),
    'akshare': ('akshare',),
    'tushare': ('tushare',),
    'ts': ('tushare',),
    'local': ('local',),
    'csv': ('local',),
}

_PROVIDER_FETCHERS = {
    'akshare': akshare_provider.fetch_instrument_dataframe,
    'tushare': tushare_provider.fetch_instrument_dataframe,
    'local': local_provider.fetch_instrument_dataframe,
}


def get_provider_chain(explicit=None):
    if explicit:
        key = explicit.strip().lower()
    else:
        key = os.environ.get('TW_DATA_PROVIDER', 'auto').strip().lower()

    if key == 'auto' and get_tushare_token():
        return ('tushare', 'akshare', 'local')
    return PROVIDER_ALIASES.get(key, (key,))


def fetch_instrument_dataframe(provider=None):
    """Try providers in order; return the first non-empty dataframe."""
    errors = []

    for name in get_provider_chain(provider):
        fetcher = _PROVIDER_FETCHERS.get(name)
        if fetcher is None:
            continue
        try:
            frame = fetcher()
            if frame is not None and not frame.empty:
                frame.attrs['provider'] = frame.attrs.get('provider', name)
                return frame
        except Exception as exc:
            errors.append('{}: {}'.format(name, repr(exc)))
            print('instrument provider {} failed: {}'.format(name, repr(exc)))

    if errors:
        print('all instrument providers failed: {}'.format('; '.join(errors)))

    return None
