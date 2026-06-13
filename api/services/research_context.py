# -*- coding: utf-8 -*-

"""Aggregate published research data for Dify agent tools."""

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from api.db.models import (
    AnalysisRun,
    FundamentalSnapshot,
    IndustryFundamentalBenchmark,
    Instrument,
    RankingResult,
    StockLabels,
    TechnicalScreenResult,
)
from api.services.data_status import get_data_status
from api.services.fundamentals import search_fundamentals
from api.services.industries import get_industry_stock_payload
from api.services.published_results import get_latest_analysis_run
from api.services.stocks import get_daily_bars, get_profile, get_quote
from core.artifacts import STOCK_RANKING_FILES, TECHNICAL_ANALYSIS_FILES
from core.stock_codes import normalize_stock_code

BARS_WINDOW_DAYS = 250
RANKING_KEYS = tuple(STOCK_RANKING_FILES.keys())
TECHNICAL_KEYS = tuple(TECHNICAL_ANALYSIS_FILES.keys())
PROFILE_SUMMARY_FIELDS = (
    'avg_roe',
    'basic_eps',
    'np_atsopc_nrgal_yoy',
    'gross_selling_rate',
)


def _match_code(column_value, code: str) -> bool:
    normalized = normalize_stock_code(code)
    return normalize_stock_code(column_value) == normalized


def _fundamentals_row(row: dict | None) -> dict | None:
    if not row:
        return None
    return {
        'pe_ttm': row.get('pe_ttm'),
        'pb_lf': row.get('pb_lf'),
        'roe': row.get('roe'),
        'roe_y1': row.get('roe_y1'),
        'roe_y2': row.get('roe_y2'),
        'roe_y3': row.get('roe_y3'),
        'dividend_yield': row.get('dividend_yield'),
        'market_cap': row.get('market_cap'),
        'float_market_cap': row.get('float_market_cap'),
        'revenue_growth': row.get('revenue_growth'),
        'profit_growth': row.get('profit_growth'),
        'pe_discount_to_industry': row.get('pe_discount_to_industry'),
        'pb_discount_to_industry': row.get('pb_discount_to_industry'),
        'close': row.get('close'),
        'is_st': row.get('is_st'),
        'updateTime': row.get('updateTime'),
    }


def _industry_benchmark(session: Session, trade_date, industry: str | None) -> dict | None:
    if not trade_date or not industry:
        return None

    benchmark = (
        session.query(IndustryFundamentalBenchmark)
        .filter_by(trade_date=trade_date, industry=industry)
        .first()
    )
    if benchmark is None:
        return None

    return {
        'industry': benchmark.industry,
        'stock_count': benchmark.stock_count,
        'median_pe_ttm': benchmark.median_pe_ttm,
        'median_pb_lf': benchmark.median_pb_lf,
        'median_roe': benchmark.median_roe,
        'median_dividend_yield': benchmark.median_dividend_yield,
        'median_market_cap': benchmark.median_market_cap,
        'median_float_market_cap': benchmark.median_float_market_cap,
        'trade_date': trade_date.strftime('%Y-%m-%d'),
    }


def _technical_signals(session: Session, code: str) -> list[str]:
    normalized = normalize_stock_code(code)
    signals = []

    for screen_key in TECHNICAL_KEYS:
        run = get_latest_analysis_run(
            session,
            AnalysisRun.CATEGORY_TECHNICAL,
            screen_key,
        )
        if run is None or run.row_count == 0:
            continue

        hit = (
            session.query(TechnicalScreenResult.id)
            .filter_by(run_id=run.id)
            .filter(
                or_(
                    TechnicalScreenResult.code == normalized,
                    TechnicalScreenResult.code == code,
                )
            )
            .first()
        )
        if hit is not None:
            signals.append(screen_key)

    return signals


def _ranking_positions(session: Session, code: str) -> dict[str, int]:
    normalized = normalize_stock_code(code)
    rankings = {}

    for ranking_key in RANKING_KEYS:
        run = get_latest_analysis_run(
            session,
            AnalysisRun.CATEGORY_RANKING,
            ranking_key,
        )
        if run is None or run.row_count == 0:
            continue

        item = (
            session.query(RankingResult.rank_order)
            .filter_by(run_id=run.id)
            .filter(
                or_(
                    RankingResult.code == normalized,
                    RankingResult.code == code,
                )
            )
            .first()
        )
        if item is not None:
            rankings[ranking_key] = item.rank_order

    return rankings


def _bars_summary(session: Session, code: str) -> dict | None:
    result = get_daily_bars(session, code, include_quote=False, days=BARS_WINDOW_DAYS)
    if result.error or not result.rows:
        return None

    closes = [row[2] for row in result.rows if len(row) >= 3]
    if not closes:
        return None

    first_close = closes[0]
    last_close = closes[-1]
    return_pct = (
        round((last_close - first_close) / first_close * 100, 2)
        if first_close
        else 0.0
    )

    return {
        'window_days': len(closes),
        'return_pct': return_pct,
        'high': round(max(closes), 2),
        'low': round(min(closes), 2),
        'last_close': round(last_close, 2),
        'updateTime': result.update_time,
    }


def _quote_summary(session: Session, code: str) -> dict | None:
    payload = get_quote(session, code)
    quot = payload.get('quot')
    if not quot:
        return None

    summary = {
        'source': payload.get('quot_source'),
        'update_time': quot.get('update_time'),
    }
    for field in ('trade', 'changepercent', 'per', 'pb', 'open', 'high', 'low'):
        if field in quot:
            summary[field] = quot[field]
    return summary


def _finance_profile_summary(profile: dict) -> dict:
    result = {}
    for field in PROFILE_SUMMARY_FIELDS:
        points = profile.get(field) or []
        if points:
            result[field] = points
    return result


def _cluster_peers(session: Session, industry: str | None, code: str) -> list[dict]:
    if not industry:
        return []

    payload = get_industry_stock_payload(session, industry, code)
    rows = payload.get('rows') or []
    normalized = normalize_stock_code(code)
    peers = []

    latest_snapshot_date = session.query(func.max(FundamentalSnapshot.trade_date)).scalar()
    snapshots_by_code: dict[str, FundamentalSnapshot] = {}
    if latest_snapshot_date is not None:
        snapshots = (
            session.query(FundamentalSnapshot)
            .filter_by(trade_date=latest_snapshot_date, industry=industry)
            .all()
        )
        for snapshot in snapshots:
            snapshots_by_code[normalize_stock_code(snapshot.code)] = snapshot

    for row in rows:
        if _match_code(row.get('code'), code):
            continue

        peer_code = normalize_stock_code(row.get('code'))
        snapshot = snapshots_by_code.get(peer_code)
        pe = (
            round(float(snapshot.pe_ttm), 2)
            if snapshot and snapshot.pe_ttm is not None
            else row.get('pe')
        )
        pb = (
            round(float(snapshot.pb_lf), 2)
            if snapshot and snapshot.pb_lf is not None
            else row.get('pb')
        )

        peers.append(
            {
                'code': peer_code,
                'name': row.get('name'),
                'pe': pe,
                'pb': pb,
                'label': row.get('label'),
            }
        )
        if len(peers) >= 8:
            break

    return peers


def _stock_labels(session: Session, code: str) -> str | None:
    normalized = normalize_stock_code(code)
    row = (
        session.query(StockLabels)
        .filter(or_(StockLabels.code == normalized, StockLabels.code == code))
        .first()
    )
    return row.labels if row else None


def _artifacts_freshness(session: Session) -> dict:
    status = get_data_status(session)
    artifacts = status.get('artifacts') or {}

    def _latest_update(group_name: str) -> str | None:
        group = artifacts.get(group_name) or {}
        dates = [
            item.get('update_time')
            for item in group.values()
            if isinstance(item, dict) and item.get('exists') and item.get('update_time')
        ]
        return max(dates) if dates else None

    return {
        'ranking': _latest_update('rankings'),
        'technical': _latest_update('technical'),
        'price_change': _latest_update('price_change'),
        'business': _latest_update('business'),
    }


def get_research_context(session: Session, code: str) -> dict:
    code = normalize_stock_code(code)
    if not code:
        return {'error': 'invalid stock code'}

    instrument = (
        session.query(Instrument)
        .filter(or_(Instrument.code == code, Instrument.code == code.lstrip('0')))
        .first()
    )

    fundamentals_result = search_fundamentals(
        session,
        search=code,
        page=1,
        page_size=1,
        exclude_st=False,
    )
    fundamentals_row = fundamentals_result.rows[0] if fundamentals_result.rows else None
    industry = (fundamentals_row or {}).get('industry') or (
        instrument.industry if instrument else None
    )
    name = (fundamentals_row or {}).get('name') or (
        instrument.name if instrument else code
    )
    data_as_of = fundamentals_result.update_time or (
        fundamentals_row.get('updateTime') if fundamentals_row else None
    )

    trade_date = None
    if fundamentals_result.update_time:
        from datetime import datetime

        try:
            trade_date = datetime.strptime(fundamentals_result.update_time, '%Y-%m-%d').date()
        except ValueError:
            trade_date = None

    profile = get_profile(session, code, include_quote=False)

    return {
        'code': code,
        'name': name,
        'industry': industry,
        'data_as_of': data_as_of,
        'labels': _stock_labels(session, code),
        'fundamentals': _fundamentals_row(fundamentals_row),
        'industry_benchmark': _industry_benchmark(session, trade_date, industry),
        'technical_signals': _technical_signals(session, code),
        'rankings': _ranking_positions(session, code),
        'quote': _quote_summary(session, code),
        'bars_summary': _bars_summary(session, code),
        'finance_profile': _finance_profile_summary(profile),
        'cluster_peers': _cluster_peers(session, industry, code),
        'artifacts_freshness': _artifacts_freshness(session),
        'errors': {
            'fundamentals': fundamentals_result.error,
        },
    }
