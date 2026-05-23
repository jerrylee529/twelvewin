# -*- coding:utf-8 -*-

"""Generate annual stock and industry performance reports (published to Postgres)."""

from __future__ import print_function

import os
import sys
from datetime import date

import pandas as pd

from config import config

_ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_ANALYSIS_DIR, '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from compat import set_display_precision
from day_data import day_data_available, load_day_dataframe, load_instruments_dataframe
from result_export import export_annual_industry_report, export_annual_stock_report

set_display_precision(2)


def format_float(value):
    return round(value, 2)


class StockInfo(object):
    def __init__(self, industry, code):
        self.industry = industry
        self.code = code
        self.change_rate = -9999
        self.amplitude = -9999
        self.close_prev_year = -9999
        self.open = -9999
        self.close = -9999
        self.high = -9999
        self.low = -9999
        self.pe = -9999
        self.pb = -9999


class TechniqueReport(object):
    def __init__(self):
        self.result_list = {}

    def compute(self, industry, code, close_prev_year, data):
        if len(data) <= 0 or not close_prev_year:
            return

        stock_info = StockInfo(industry, code)
        low = data['close'].min()
        high = data['close'].max()
        close_last = data.iloc[len(data) - 1]['close']

        stock_info.change_rate = format_float(
            (close_last - close_prev_year) * 100 / close_prev_year
        )
        stock_info.close_prev_year = format_float(close_prev_year)
        stock_info.low = format_float(low)
        stock_info.high = format_float(high)
        stock_info.open = format_float(data.iloc[0]['open'])
        stock_info.close = format_float(close_last)
        stock_info.amplitude = format_float((high - low) * 100 / low)
        self.result_list[code] = stock_info


class IndustryInfo(object):
    def __init__(self, industry):
        self.industry = industry
        self.avg_change_rate = -9999
        self.avg_amplitude = -9999
        self.avg_price = -9999
        self.avg_pe = -9999
        self.avg_pb = -9999
        self.stock_number = 0


class IndustryReport(object):
    def __init__(self):
        self.result_list = {}
        self._total_amplitude = {}
        self._total_change_rate = {}
        self._total_price = {}
        self._stock_number = {}

    def compute(self, data):
        for item in data.values():
            if item.industry not in self.result_list:
                industry_info = IndustryInfo(item.industry)
                self.result_list[item.industry] = industry_info
                self._total_amplitude[item.industry] = 0
                self._total_change_rate[item.industry] = 0
                self._total_price[item.industry] = 0
                self._stock_number[item.industry] = 0
            else:
                industry_info = self.result_list[item.industry]

            self._total_amplitude[item.industry] += item.amplitude
            self._total_change_rate[item.industry] += item.change_rate
            self._total_price[item.industry] += item.close
            self._stock_number[item.industry] += 1

            count = self._stock_number[item.industry]
            industry_info.avg_change_rate = format_float(
                self._total_change_rate[item.industry] / count
            )
            industry_info.avg_amplitude = format_float(
                self._total_amplitude[item.industry] / count
            )
            industry_info.avg_price = format_float(
                self._total_price[item.industry] / count
            )
            industry_info.stock_number = count


def _results_to_dataframe(result_list):
    rows = [item.__dict__ for item in result_list]
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def compute(year=None, *, instrument_filename=None, day_file_path=None, result_file_path=None):
    """Build annual stock/industry reports for ``year`` and publish to the database."""
    del instrument_filename, day_file_path, result_file_path  # legacy args, unused

    if year is None:
        year = int(os.environ.get('TW_ANNUAL_REPORT_YEAR', date.today().year))

    instruments = load_instruments_dataframe(include_industry=True)
    if instruments is None or instruments.empty:
        print('Could not find any instruments, exit')
        return {'status': 'skipped', 'reason': 'no instruments'}

    technique_report = TechniqueReport()

    for _, row in instruments.iterrows():
        code = str(row['code'])
        industry = row.get('industry') or ''

        print('calculate {}'.format(code))

        if not day_data_available(code):
            continue

        try:
            df = load_day_dataframe(code)
            if df.empty:
                continue

            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date']).set_index('date')

            target_year = int(year)
            df_year = df[df.index.year == target_year]
            if df_year.empty:
                continue

            df_prev_year = df[df.index.year == target_year - 1]
            try:
                last_close = float(df_prev_year.iloc[-1]['close']) if not df_prev_year.empty else None
            except (IndexError, TypeError, ValueError):
                last_close = None
            if last_close is None:
                try:
                    last_close = float(df_year.iloc[0]['open'])
                except (IndexError, TypeError, ValueError):
                    continue

            if not last_close:
                continue

            technique_report.compute(industry, code, last_close, df_year)
        except Exception as exc:
            print(repr(exc))
            continue

    stock_frame = _results_to_dataframe(technique_report.result_list.values())
    stock_summary = {'status': 'skipped', 'reason': 'no stock rows'}
    if not stock_frame.empty:
        stock_summary = export_annual_stock_report(stock_frame, year, config=config)
        print('annual stock report:', stock_summary)

    industry_report = IndustryReport()
    industry_report.compute(technique_report.result_list)
    industry_frame = _results_to_dataframe(industry_report.result_list.values())
    industry_summary = {'status': 'skipped', 'reason': 'no industry rows'}
    if not industry_frame.empty:
        industry_summary = export_annual_industry_report(industry_frame, year, config=config)
        print('annual industry report:', industry_summary)

    return {
        'status': 'ok',
        'year': year,
        'stock': stock_summary,
        'industry': industry_summary,
    }


if __name__ == '__main__':
    compute(year=int(os.environ.get('TW_ANNUAL_REPORT_YEAR', '2018')))
