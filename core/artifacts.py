# -*- coding: utf-8 -*-

"""Canonical artifact filenames and DB keys (shared compute/web contract)."""

STOCK_RANKING_FILES = {
    'pe': 'stock_pe.csv',
    'pb': 'stock_pb.csv',
    'roe': 'stock_roe.csv',
    'divi': 'stock_dividence.csv',
    'value': 'stock_value.csv',
}

TECHNICAL_ANALYSIS_FILES = {
    'highest': 'highest_in_history.csv',
    'lowest': 'lowest_in_history.csv',
    'ma_long': 'ma_long.csv',
    'break_ma': 'break_ma.csv',
    'above_ma': 'above_ma.csv',
}

PRICE_CHANGE_FILE = 'price_change.csv'
BUSINESS_RANKING_FILE = 'stock_business.csv'

ANNUAL_STOCK_REPORT_FILE = 'annual_technique_report_{year}.csv'
ANNUAL_INDUSTRY_REPORT_FILE = 'annual_industry_report_{year}.csv'


def annual_stock_report_filename(year):
    return ANNUAL_STOCK_REPORT_FILE.format(year=year)


def annual_industry_report_filename(year):
    return ANNUAL_INDUSTRY_REPORT_FILE.format(year=year)
