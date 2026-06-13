# -*- coding: utf-8 -*-

"""Stock search, candlestick bars, and finance profile."""

import json
import time

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from api.db.models import DailyBar, FundamentalSnapshot, Instrument, XueQiuReportInfo
from api.services.quotes import get_quotation
from api.services.types import QueryResult

PROFILE_FIELDS = [
    'net_profit_after_nrgal_atsolc',
    'avg_roe',
    'np_atsopc_nrgal_yoy',
    'basic_eps',
    'gross_selling_rate',
    'np_per_share',
]

PROFILE_AMOUNT_FIELDS = {
    'net_profit_after_nrgal_atsolc': True,
    'avg_roe': False,
    'np_atsopc_nrgal_yoy': False,
    'basic_eps': False,
    'gross_selling_rate': False,
    'np_per_share': False,
}


def _convert_float(value, *, is_amount=False):
    if value is None:
        return 0.0
    return round(value / 10000 if is_amount else value, 2)


def list_instruments(
    session: Session,
    *,
    offset: int = 0,
    limit: int | None = None,
) -> tuple[list[dict], int]:
    """Return all instruments for sitemap and bulk SEO pages."""
    total = session.query(func.count(Instrument.id)).scalar() or 0
    db_query = session.query(Instrument).order_by(Instrument.code)
    if offset > 0:
        db_query = db_query.offset(offset)
    if limit is not None and limit > 0:
        db_query = db_query.limit(limit)

    items = []
    for index, instrument in enumerate(db_query.all(), start=offset + 1):
        items.append(
            {
                'id': index,
                'code': instrument.code,
                'name': instrument.name,
                'industry': instrument.industry,
            }
        )
    return items, total


def search_instruments(session: Session, query: str = '', *, limit=50) -> list[dict]:
    q = (query or '').strip()
    db_query = session.query(Instrument).order_by(Instrument.code)
    if q:
        pattern = '%{}%'.format(q)
        db_query = db_query.filter(
            or_(Instrument.code.like(pattern), Instrument.name.like(pattern))
        )

    items = []
    for index, instrument in enumerate(db_query.limit(limit).all(), start=1):
        items.append(
            {
                'id': index,
                'code': instrument.code,
                'name': instrument.name,
                'industry': instrument.industry,
            }
        )
    return items


def get_daily_bars(
    session: Session,
    code: str,
    *,
    include_quote=True,
    days: int | None = None,
) -> QueryResult:
    code = str(code).strip()
    db_query = session.query(DailyBar).filter_by(code=code)
    if days is not None and days > 0:
        bars = (
            db_query.order_by(DailyBar.trade_date.desc())
            .limit(days)
            .all()
        )
        bars.reverse()
    else:
        bars = db_query.order_by(DailyBar.trade_date.asc()).all()

    rows = []
    update_time = None
    for bar in bars:
        if bar.open is None or bar.close is None or bar.low is None or bar.high is None:
            continue
        trade_date = bar.trade_date.strftime('%Y-%m-%d')
        update_time = trade_date
        row = [
            trade_date,
            float(bar.open),
            float(bar.close),
            float(bar.low),
            float(bar.high),
        ]
        if bar.volume is not None:
            row.append(float(bar.volume))
        rows.append(row)

    if include_quote:
        quot = get_quotation(code)
        if quot:
            quote_date = quot['update_time'].split()[0]
            quote_row = [
                quote_date,
                float(quot['open']),
                float(quot['trade']),
                float(quot['low']),
                float(quot['high']),
            ]
            if quot.get('volume'):
                quote_row.append(float(quot['volume']))
            if rows and rows[-1][0] != quote_date:
                rows.append(quote_row)
            elif not rows:
                rows.append(quote_row)
                update_time = quote_date

    if not rows:
        return QueryResult(error='no daily bars in database')

    return QueryResult(rows=rows, update_time=update_time)


def _load_finance_reports(session: Session, code: str) -> dict:
    query_result = (
        session.query(XueQiuReportInfo)
        .filter_by(security_code=code, report_type=3)
        .order_by(XueQiuReportInfo.id.desc())
        .first()
    )
    reports = {}
    if query_result is None:
        return reports

    json_data = json.loads(query_result.report_data)
    for item in json_data['data']['list']:
        year = time.strftime('%Y', time.localtime(item['report_date'] / 1000))
        report = reports.get(year)
        if report is None:
            report = {}
            reports[year] = report

        for key in item.keys():
            if isinstance(item[key], list):
                report[key] = item[key][0]
            else:
                report[key] = item[key]

    return reports


def _build_quotation_fallback(session: Session, code: str) -> dict | None:
    """Synthesize quote fields from DB when Redis realtime quote is unavailable."""
    latest_bars = (
        session.query(DailyBar)
        .filter_by(code=code)
        .order_by(DailyBar.trade_date.desc())
        .limit(2)
        .all()
    )
    if not latest_bars:
        return None

    latest = latest_bars[0]
    previous = latest_bars[1] if len(latest_bars) > 1 else None
    if latest.close is None or latest.open is None or latest.high is None or latest.low is None:
        return None

    settlement = previous.close if previous and previous.close else latest.open
    trade = float(latest.close)
    settlement_value = float(settlement) if settlement else trade
    change_percent = (
        round((trade - settlement_value) / settlement_value * 100, 2)
        if settlement_value
        else 0.0
    )

    instrument = session.query(Instrument).filter_by(code=code).first()
    latest_snapshot_date = session.query(func.max(FundamentalSnapshot.trade_date)).scalar()
    snapshot = None
    if latest_snapshot_date is not None:
        snapshot = (
            session.query(FundamentalSnapshot)
            .filter_by(code=code, trade_date=latest_snapshot_date)
            .first()
        )

    name = (snapshot.name if snapshot and snapshot.name else None) or (
        instrument.name if instrument else code
    )
    pe = (snapshot.pe_ttm if snapshot and snapshot.pe_ttm else None) or (
        instrument.pe if instrument else None
    )
    pb = (snapshot.pb_lf if snapshot and snapshot.pb_lf else None) or (
        instrument.pb if instrument else None
    )

    quot = {
        'code': code,
        'name': name,
        'trade': str(trade),
        'open': str(float(latest.open)),
        'high': str(float(latest.high)),
        'low': str(float(latest.low)),
        'settlement': str(settlement_value),
        'changepercent': str(change_percent),
        'update_time': latest.trade_date.strftime('%Y-%m-%d'),
        'source': 'daily_bar',
    }

    if latest.volume is not None:
        quot['volume'] = str(int(latest.volume))
    if pe is not None:
        quot['per'] = str(round(float(pe), 2))
    if pb is not None:
        quot['pb'] = str(round(float(pb), 2))
    if snapshot and snapshot.market_cap is not None:
        quot['mktcap'] = str(snapshot.market_cap)
    if snapshot and snapshot.float_market_cap is not None:
        quot['nmc'] = str(snapshot.float_market_cap)

    return quot


def get_quote(session: Session, code: str) -> dict:
    code = str(code).strip()
    quot = get_quotation(code)
    if quot:
        return {'quot': quot, 'quot_source': 'redis'}

    fallback = _build_quotation_fallback(session, code)
    return {
        'quot': fallback,
        'quot_source': 'daily_bar' if fallback else None,
    }


def get_profile(session: Session, code: str, *, include_quote=True) -> dict:
    result = {field: [] for field in PROFILE_FIELDS}
    code = str(code).strip()

    if include_quote:
        quote_payload = get_quote(session, code)
        result['quot_source'] = quote_payload['quot_source']
        result['quot'] = quote_payload['quot']
    else:
        result['quot_source'] = None
        result['quot'] = None

    reports = _load_finance_reports(session, code)
    for year in sorted(reports.keys(), reverse=False):
        row = reports[year]
        for field in PROFILE_FIELDS:
            result[field].append(
                {
                    'date': year,
                    'value': _convert_float(
                        row.get(field),
                        is_amount=PROFILE_AMOUNT_FIELDS[field],
                    ),
                }
            )

    return result
