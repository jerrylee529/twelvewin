#!/usr/bin/env python
# encoding: utf-8
"""
@author: Jerry Lee
@license: (C) Copyright 2013-2019, Node Supply Chain Manager Corporation Limited.
@file: roe_selection.py
@time: 2020/2/9 13:51
@desc: 
"""

import json
import random
import time

import pandas as pd
import requests
from models import Session, XueQiuReportInfo, engine


def get_reports():
    session = Session()

    try:
        query_result = session.query(XueQiuReportInfo.security_code, XueQiuReportInfo.security_name,
                                     XueQiuReportInfo.report_data).filter_by(report_type=3).all()
    finally:
        session.close()

    return query_result


def roe_to_db():
    stocks = []

    session = Session()

    count = session.query(XueQiuReportInfo).filter_by(report_type=3).count()

    num_of_page = 10
    for i in range(0, int((count-1)/num_of_page)+1):
        reports = session.query(XueQiuReportInfo.security_code, XueQiuReportInfo.security_name,
                                XueQiuReportInfo.report_data).filter_by(report_type=3).limit(num_of_page) \
            .offset(i * num_of_page).all()

        for report in reports:
            json_data = json.loads(report.report_data)

            stock = {'code': report.security_code, 'name': report.security_name}

            for item in json_data['data']['list']:
                year = time.strftime("%Y", time.localtime(item['report_date'] / 1000))
                stock[year] = item['avg_roe'][0]

            stocks.append(stock)

    session.close()

    df = pd.DataFrame(stocks)

    print(df)

    df.to_sql(name='roe_per_year', con=engine, if_exists='append', index=False)

    print(stocks)


my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]

def roe_selection():
    stocks = []

    sql = ''' SELECT code, name, (`2016`+`2017`+`2018`)/3 as avg_roe, (`2018`-`2016`)*100/`2016`/2 as growth_rate
      FROM roe_per_year 
      where `2016`>20 and `2017`>20 and `2018`>20 and `2018`>`2017` and `2017`>`2016` ORDER BY avg_roe DESC
     '''

    # read_sql_query的两个参数: sql语句， 数据库连接
    df = pd.read_sql_query(sql, engine)

    df['pb'] = None
    df['pe'] = None
    df['eps'] = None
    df['market_capital'] = None

    session = requests.session()

    headers = {'User-Agent':  random.choice(my_headers)}

    session.get('https://xueqiu.com/', headers=headers)

    url = 'https://stock.xueqiu.com/v5/stock/quote.json?symbol={}{}&extend=detail'

    for code in df['code']:
        if code[0] == '6':
            market = 'SH'
        else:
            market = 'SZ'

        rsp = session.get(url.format(market, code), headers=headers)

        if rsp.status_code == 200:
            json_data = rsp.json()
            df.loc[df['code'] == code, 'pe'] = json_data['data']['quote']['pe_ttm']
            df.loc[df['code'] == code, 'pb'] = json_data['data']['quote']['pb']
            df.loc[df['code'] == code, 'eps'] = json_data['data']['quote']['eps']
            df.loc[df['code'] == code, 'market_capital'] = json_data['data']['quote']['market_capital']
        else:
            print(rsp.content)

    print(df)

    df.to_csv('avg_roe.csv', index=False)


if __name__ == '__main__':
    #roe_to_db()
    roe_selection()
