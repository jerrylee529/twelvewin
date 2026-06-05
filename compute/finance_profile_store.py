# -*- coding: utf-8 -*-

"""Persist Tushare finance profile payloads for the stock profile API."""

from __future__ import annotations

import os
import sys

from app.models import Instrument, XueQiuReportInfo
from core.db import session_scope

ANALYSIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'analysis'))
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)

from finance_profile import (  # noqa: E402
    FINANCE_PROFILE_REPORT_TYPE,
    fetch_finance_profile_report_data,
    finance_profile_years,
)
from providers.tushare_pro import TushareProError, get_pro_client  # noqa: E402


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value == '':
        return default
    return int(value)


def _parse_codes_filter(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(',') if part.strip()]


def resolve_finance_profile_codes(session) -> list[str]:
    explicit = _parse_codes_filter(os.environ.get('TW_FINANCE_PROFILE_CODES'))
    if explicit:
        return explicit

    rows = session.query(Instrument.code).order_by(Instrument.code).all()
    codes = [str(row[0]).strip() for row in rows if row and row[0]]
    max_codes = _env_int('TW_FINANCE_PROFILE_MAX_CODES', 0)
    if max_codes > 0:
        return codes[:max_codes]
    return codes


def _instrument_name_map(session, codes: list[str]) -> dict[str, str]:
    if not codes:
        return {}
    rows = session.query(Instrument.code, Instrument.name).filter(
        Instrument.code.in_(codes)
    ).all()
    return {
        str(code).strip(): (str(name).strip() if name else str(code).strip())
        for code, name in rows
    }


def _upsert_finance_profile(session, code: str, name: str, report_data: str) -> None:
    row = (
        session.query(XueQiuReportInfo)
        .filter_by(security_code=code, report_type=FINANCE_PROFILE_REPORT_TYPE)
        .first()
    )
    security_name = (name or code)[:8]
    if row is None:
        session.add(
            XueQiuReportInfo(
                security_code=code,
                security_name=security_name,
                report_type=FINANCE_PROFILE_REPORT_TYPE,
                report_data=report_data,
            )
        )
        return

    row.security_name = security_name
    row.report_data = report_data


def sync_finance_profiles(
    *,
    codes: list[str] | None = None,
    years: int | None = None,
) -> dict[str, int]:
    """Fetch Tushare annual indicators and upsert ``xueqiu_report_info`` rows."""
    profile_years = years or finance_profile_years()

    try:
        pro = get_pro_client()
    except TushareProError as exc:
        raise RuntimeError(str(exc)) from exc

    summary = {'requested': 0, 'synced': 0, 'skipped': 0, 'failed': 0}

    with session_scope() as session:
        target_codes = codes or resolve_finance_profile_codes(session)
        names = _instrument_name_map(session, target_codes)

    summary['requested'] = len(target_codes)
    if not target_codes:
        return summary

    pending: list[tuple[str, str, str]] = []

    for code in target_codes:
        normalized = str(code or '').strip()
        if not normalized:
            summary['skipped'] += 1
            continue

        try:
            report_data = fetch_finance_profile_report_data(
                normalized,
                years=profile_years,
                pro=pro,
            )
        except Exception as exc:
            summary['failed'] += 1
            print('finance profile sync failed for {}: {}'.format(normalized, repr(exc)))
            continue

        if not report_data:
            summary['skipped'] += 1
            continue

        pending.append((normalized, names.get(normalized, normalized), report_data))

    if pending:
        with session_scope() as session:
            for code, name, report_data in pending:
                _upsert_finance_profile(session, code, name, report_data)
                summary['synced'] += 1

    return summary
