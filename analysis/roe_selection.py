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
from config import my_headers


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


def get_financial_report(session, headers, market, code):
    """
    获取2019第三季度和2018年报的营业收入以及扣非净利润数据
    """

    url = 'https://stock.xueqiu.com/v5/stock/finance/cn/indicator.json?symbol={}{}&type=all&is_detail=true&count=5&timestamp='

    rsp = session.get(url.format(market, code), headers=headers)

    item_2019_rev = None
    item_2019_np = None
    item_2019_ratio = None
    item_2018_rev = None
    item_2018_np = None

    if rsp.status_code == 200:
        json_date = rsp.json()
        for item in json_date['data']['list']:
            if item['report_date'] == 1569772800000:
                item_2019_rev = item['total_revenue'][0]
                item_2019_np = item['net_profit_after_nrgal_atsolc'][0]
                item_2019_ratio = item['asset_liab_ratio'][0]
            elif item['report_date'] == 1546185600000:
                item_2018_rev = item['total_revenue'][0]
                item_2018_np = item['net_profit_after_nrgal_atsolc'][0]
                break
            else:
                continue

    return item_2019_rev, item_2019_np, item_2019_ratio, item_2018_rev, item_2018_np


def get_listed_date(session, headers, market, code):
    url = 'https://stock.xueqiu.com/v5/stock/f10/cn/company.json?symbol={}{}'

    rsp = session.get(url.format(market, code), headers=headers)

    if rsp.status_code == 200:
        json_data = rsp.json()
        return json_data['data']['company']['listed_date']
    else:
        return None


def roe_selection():
    stocks = []

    sql = ''' SELECT code, name, (`2016`+`2017`+`2018`)/3 as avg_roe, (`2018`-`2016`)*100/`2016`/2 as growth_rate,
      `2019` FROM roe_per_year 
      where `2016` > 15 and `2017` > 15 and `2018` > 15 ORDER BY avg_roe DESC
     '''

    # read_sql_query的两个参数: sql语句， 数据库连接
    df = pd.read_sql_query(sql, engine)

    df['pb'] = None
    df['pe'] = None
    df['eps'] = None
    df['market_capital'] = None
    df['2019_rev'] = None
    df['2019_np'] = None
    df['2018_rev'] = None
    df['2018_np'] = None

    df['pe_season3'] = None
    df['peg_season3'] = None

    session = requests.session()

    headers = {'User-Agent':  random.choice(my_headers)}

    session.get('https://xueqiu.com/', headers=headers)

    url = 'https://stock.xueqiu.com/v5/stock/quote.json?symbol={}{}&extend=detail'

    for code in df['code']:
        if code[0] == '6':
            market = 'SH'
        else:
            market = 'SZ'

        listed_date = get_listed_date(session, headers, market, code)

        if listed_date is None or listed_date > 1483200000000:
            continue
        else:
            #print(listed_date)
            pass

        rsp = session.get(url.format(market, code), headers=headers)

        if rsp.status_code == 200:
            json_data = rsp.json()
            df.loc[df['code'] == code, 'pe'] = json_data['data']['quote']['pe_forecast']
            df.loc[df['code'] == code, 'pb'] = json_data['data']['quote']['pb']
            df.loc[df['code'] == code, 'eps'] = json_data['data']['quote']['eps']
            df.loc[df['code'] == code, 'market_capital'] = json_data['data']['quote']['market_capital'] /100000000 if json_data['data']['quote']['market_capital'] else 0
        else:
            print(rsp.content)

        item_2019_rev, item_2019_np, item_2019_ratio, item_2018_rev, item_2018_np = get_financial_report(session, headers, market, code)

        df.loc[df['code'] == code, '2019_rev'] = item_2019_rev/100000000 if item_2019_rev else item_2019_rev
        df.loc[df['code'] == code, '2019_np'] = item_2019_np/100000000 if item_2019_np else item_2019_np
        df.loc[df['code'] == code, '2019_ratio'] = item_2019_ratio
        df.loc[df['code'] == code, '2018_rev'] = item_2018_rev/100000000 if item_2018_rev else item_2018_rev
        df.loc[df['code'] == code, '2018_np'] = item_2018_np/100000000 if item_2018_np else item_2018_np

    df['increase_rate'] = (df['2019_np']-df['2018_np'])*100/df['2018_np']
    df['pe_season3'] = df['market_capital']/df['2019_np']
    df['peg_season3'] = df['pe_season3']/df['increase_rate']

    print(df)

    df = df.dropna(subset=["pe", "pb"])  # 删除指定列空值的行

    df.drop(df[df.pe < 0].index, inplace=True)

    df.drop(df[df.increase_rate < 0].index, inplace=True)

    df.to_csv('avg_roe.csv', index=False)


if __name__ == '__main__':
    #roe_to_db()
    roe_selection()
