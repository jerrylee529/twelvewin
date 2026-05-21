# -*- coding: utf-8 -*-

"""Yahoo Finance market data via yfinance (A-share symbols: .SS / .SZ / .BJ)."""

import os
import time

from providers.base import (
    code_to_yahoo_symbol,
    codes_from_day_csv_directory,
    normalize_stock_code,
    read_instruments_csv,
    yahoo_symbol_to_code,
)


def _env_int(name, default):
    raw = os.environ.get(name, '').strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name, default):
    raw = os.environ.get(name, '').strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _day_file_path():
    path = os.environ.get('DAY_FILE_PATH', '').strip()
    if path:
        return path if path.endswith(os.sep) else path + os.sep
    try:
        from config import config as analysis_config

        path = analysis_config.get('DAY_FILE_PATH') or ''
    except ImportError:
        path = ''
    if path and not path.endswith(os.sep):
        path = path + os.sep
    return path


def resolve_quote_codes():
    """Codes to request from Yahoo (explicit list, instruments.csv, or day_data/)."""
    explicit = os.environ.get('TW_YAHOO_QUOTE_CODES', '').strip()
    if explicit:
        codes = [normalize_stock_code(part) for part in explicit.split(',')]
        return sorted({code for code in codes if code})

    codes = []
    day_dir = _day_file_path()
    instruments = read_instruments_csv(os.path.join(day_dir, 'instruments.csv'))
    if instruments is not None and not instruments.empty:
        codes.extend(instruments['code'].tolist())

    codes.extend(codes_from_day_csv_directory(day_dir))

    codes = sorted({normalize_stock_code(code) for code in codes if normalize_stock_code(code)})

    max_codes = _env_int('TW_YAHOO_MAX_CODES', 0)
    if max_codes > 0:
        codes = codes[:max_codes]

    return codes


def _parse_download_history(data, symbol_to_code):
    """Build quote rows from yfinance ``download()`` OHLC panel."""
    import pandas as pd

    if data is None or data.empty:
        return []

    records = []

    if isinstance(data.columns, pd.MultiIndex):
        tickers = data.columns.get_level_values(0).unique()
        for symbol in tickers:
            code = symbol_to_code.get(symbol)
            if not code:
                continue
            try:
                ticker_df = data[symbol].dropna(how='all')
            except (KeyError, TypeError):
                continue
            if ticker_df is None or ticker_df.empty or 'Close' not in ticker_df.columns:
                continue
            closes = pd.to_numeric(ticker_df['Close'], errors='coerce').dropna()
            if closes.empty:
                continue
            trade = float(closes.iloc[-1])
            settlement = float(closes.iloc[-2]) if len(closes) > 1 else trade
            records.append({
                'code': code,
                'trade': trade,
                'settlement': settlement,
            })
    else:
        if 'Close' not in data.columns:
            return records
        symbol = next(iter(symbol_to_code.keys()), None)
        code = symbol_to_code.get(symbol)
        if not code:
            return records
        closes = pd.to_numeric(data['Close'], errors='coerce').dropna()
        if closes.empty:
            return records
        trade = float(closes.iloc[-1])
        settlement = float(closes.iloc[-2]) if len(closes) > 1 else trade
        records.append({'code': code, 'trade': trade, 'settlement': settlement})

    return records


def _fetch_quotes_via_download(codes):
    import pandas as pd
    import yfinance as yf

    batch_size = max(1, _env_int('TW_YAHOO_BATCH_SIZE', 80))
    sleep_seconds = max(0.0, _env_float('TW_YAHOO_BATCH_SLEEP', 0.3))

    symbol_to_code = {}
    symbols = []
    for code in codes:
        symbol = code_to_yahoo_symbol(code)
        if not symbol:
            continue
        symbol_to_code[symbol] = code
        symbols.append(symbol)

    if not symbols:
        return None

    all_records = []
    for offset in range(0, len(symbols), batch_size):
        batch = symbols[offset:offset + batch_size]
        try:
            panel = yf.download(
                batch,
                period='5d',
                interval='1d',
                group_by='ticker',
                auto_adjust=False,
                threads=True,
                progress=False,
            )
        except Exception as exc:
            print('yahoo download batch failed: {}'.format(repr(exc)))
            continue

        all_records.extend(_parse_download_history(panel, symbol_to_code))
        if sleep_seconds and offset + batch_size < len(symbols):
            time.sleep(sleep_seconds)

    if not all_records:
        return None

    return pd.DataFrame(all_records)


def _enrich_fundamentals_from_fast_info(frame):
    """Add per / pb / mktcap from ``Ticker.fast_info`` (batched)."""
    import yfinance as yf

    batch_size = max(1, _env_int('TW_YAHOO_FUNDAMENTALS_BATCH', 40))
    sleep_seconds = max(0.0, _env_float('TW_YAHOO_BATCH_SLEEP', 0.3))

    per_values = []
    pb_values = []
    mktcap_values = []

    codes = frame['code'].tolist()
    for offset in range(0, len(codes), batch_size):
        batch_codes = codes[offset:offset + batch_size]
        symbols = [code_to_yahoo_symbol(code) for code in batch_codes]
        symbols = [symbol for symbol in symbols if symbol]

        try:
            tickers = yf.Tickers(' '.join(symbols))
        except Exception as exc:
            print('yahoo Tickers batch failed: {}'.format(repr(exc)))
            per_values.extend([None] * len(batch_codes))
            pb_values.extend([None] * len(batch_codes))
            mktcap_values.extend([None] * len(batch_codes))
            continue

        for code in batch_codes:
            symbol = code_to_yahoo_symbol(code)
            per = pb = mktcap = None
            try:
                ticker = tickers.tickers.get(symbol)
                if ticker is None:
                    raise KeyError(symbol)
                info = getattr(ticker, 'fast_info', None)
                if info is None:
                    info = ticker.info
                else:
                    info = dict(info)

                last_price = info.get('last_price') or info.get('regularMarketPrice')
                trailing_pe = info.get('trailing_pe') or info.get('trailingPE')
                price_to_book = info.get('price_to_book') or info.get('priceToBook')
                market_cap = info.get('market_cap') or info.get('marketCap')

                if trailing_pe is not None:
                    per = float(trailing_pe)
                if price_to_book is not None:
                    pb = float(price_to_book)
                if market_cap is not None:
                    mktcap = float(market_cap) / 10000.0
            except Exception:
                pass

            per_values.append(per)
            pb_values.append(pb)
            mktcap_values.append(mktcap)

        if sleep_seconds and offset + batch_size < len(codes):
            time.sleep(sleep_seconds)

    frame = frame.copy()
    frame['per'] = per_values
    frame['pb'] = pb_values
    frame['mktcap'] = mktcap_values
    frame['nmc'] = mktcap_values
    return frame


def _try_akshare_fhps_enrich(frame):
    try:
        from providers import akshare_market

        fhps, _date = akshare_market._load_fhps()
        if fhps is not None:
            return akshare_market._enrich_spot_from_fhps(frame, fhps)
    except Exception as exc:
        print('yahoo fhps enrich skipped: {}'.format(repr(exc)))
    return frame


def fetch_today_quotes_dataframe(*, enrich=True):
    """Spot quotes compatible with legacy ``get_today_all`` column names."""
    codes = resolve_quote_codes()
    if not codes:
        print('yahoo: no stock codes resolved (set TW_YAHOO_QUOTE_CODES or populate day_data/)')
        return None

    frame = _fetch_quotes_via_download(codes)
    if frame is None or frame.empty:
        return None

    if os.environ.get('TW_YAHOO_FETCH_FUNDAMENTALS', '1').strip().lower() not in ('0', 'false', 'no'):
        frame = _enrich_fundamentals_from_fast_info(frame)

    if enrich:
        frame = _try_akshare_fhps_enrich(frame)

    frame.attrs['provider'] = 'yahoo'
    return frame.reset_index(drop=True)


def fetch_dividend_dataframe(report_date=None):
    """Build dividend rows from Yahoo ``fast_info`` / ``info`` (subset of market)."""
    import pandas as pd

    codes = resolve_quote_codes()
    if not codes:
        return None

    import yfinance as yf

    records = []
    batch_size = max(1, _env_int('TW_YAHOO_FUNDAMENTALS_BATCH', 40))
    for offset in range(0, len(codes), batch_size):
        batch_codes = codes[offset:offset + batch_size]
        symbols = [code_to_yahoo_symbol(code) for code in batch_codes]
        symbols = [symbol for symbol in symbols if symbol]
        try:
            tickers = yf.Tickers(' '.join(symbols))
        except Exception as exc:
            print('yahoo dividend batch failed: {}'.format(repr(exc)))
            continue

        for code in batch_codes:
            symbol = code_to_yahoo_symbol(code)
            try:
                ticker = tickers.tickers.get(symbol)
                if ticker is None:
                    continue
                info = dict(getattr(ticker, 'fast_info', None) or ticker.info)
                name = info.get('shortName') or info.get('longName') or code
                price = info.get('last_price') or info.get('regularMarketPrice')
                div_rate = info.get('dividend_rate') or info.get('dividendRate')
                trailing_div = info.get('trailing_annual_dividend_rate') or info.get(
                    'trailingAnnualDividendRate'
                )

                divi = None
                if trailing_div is not None and float(trailing_div) > 0:
                    divi = float(trailing_div) * 10.0
                elif div_rate is not None and price and float(price) > 0:
                    divi = float(div_rate) * 10.0 / float(price)

                if divi is None or divi <= 0:
                    continue

                records.append({
                    'code': code,
                    'name': name,
                    'divi': divi,
                    'report_date': pd.Timestamp.today().normalize(),
                    'year': pd.Timestamp.today().year,
                })
            except Exception:
                continue

    if not records:
        return None

    frame = pd.DataFrame(records)
    frame.attrs['provider'] = 'yahoo'
    return frame.reset_index(drop=True)


def fetch_stock_basics_dataframe():
    """Fundamental snapshot from Yahoo ``fast_info`` / ``info``."""
    import pandas as pd
    import yfinance as yf

    codes = resolve_quote_codes()
    if not codes:
        return None

    records = []
    batch_size = max(1, _env_int('TW_YAHOO_FUNDAMENTALS_BATCH', 40))
    for offset in range(0, len(codes), batch_size):
        batch_codes = codes[offset:offset + batch_size]
        symbols = [code_to_yahoo_symbol(c) for c in batch_codes]
        symbols = [s for s in symbols if s]
        try:
            tickers = yf.Tickers(' '.join(symbols))
        except Exception as exc:
            print('yahoo basics batch failed: {}'.format(repr(exc)))
            continue

        for code in batch_codes:
            symbol = code_to_yahoo_symbol(code)
            try:
                ticker = tickers.tickers.get(symbol)
                if ticker is None:
                    continue
                info = dict(getattr(ticker, 'fast_info', None) or ticker.info)
                records.append({
                    'code': code,
                    'name': info.get('shortName') or info.get('longName') or code,
                    'esp': info.get('trailing_eps') or info.get('trailingEps'),
                    'bvps': info.get('book_value') or info.get('bookValue'),
                    'pe': info.get('trailing_pe') or info.get('trailingPE'),
                    'pb': info.get('price_to_book') or info.get('priceToBook'),
                    'totals': None,
                    'industry': info.get('industry'),
                })
            except Exception:
                continue

    if not records:
        return None

    frame = pd.DataFrame(records)
    for col in ('esp', 'bvps', 'pe', 'pb'):
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors='coerce')

    frame.attrs['provider'] = 'yahoo'
    return frame.reset_index(drop=True)
