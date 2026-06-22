# -*- coding: utf-8 -*-

"""Filing document catalog, PDF content, and AI analysis read/write."""

from __future__ import annotations

import datetime
import json
import os
import sys

from sqlalchemy.orm import Session

from api.db.models import FilingAiAnalysis, FilingDocument, FilingTextChunk
from api.services.redis_cache import (
    cache_get_json,
    cache_set_json,
    filing_analysis_cache_key,
)
from api.services.types import QueryResult
from core.filing_names import SEASON_LABELS
from core.stock_codes import normalize_stock_code

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
ANALYSIS_DIR = os.path.join(PROJECT_ROOT, 'analysis')
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)

DEFAULT_ANALYSIS_VERSION = os.environ.get('TW_FILING_ANALYSIS_VERSION', 'v1')
CONTENT_MAX_CHARS = int(os.environ.get('TW_FILING_CONTENT_MAX_CHARS', '120000') or '120000')


def _display_label(row: FilingDocument) -> str:
    if row.season == 0:
        return f'{row.year} 年报'
    if row.season == 2 and row.report_kind == 'semi_annual':
        return f'{row.year} 半年报'
    label = SEASON_LABELS.get(row.season, row.report_type_label)
    return f'{row.year} {label}'


def _serialize_filing_row(row: FilingDocument, *, include_pdf_url: bool = False) -> dict:
    payload = {
        'id': row.id,
        'code': row.code,
        'year': row.year,
        'season': row.season,
        'report_kind': row.report_kind,
        'report_type_label': row.report_type_label,
        'display_label': _display_label(row),
        'filename': row.filename,
        'publish_date': row.publish_date.isoformat() if row.publish_date else None,
        'page_count': row.page_count,
        'analysis_status': row.analysis_status,
        'synced_at': row.synced_at.isoformat() if row.synced_at else None,
        'extracted_at': row.extracted_at.isoformat() if row.extracted_at else None,
    }
    if include_pdf_url:
        try:
            from filing.qiniu_client import signed_filing_url

            payload['pdf_url'] = signed_filing_url(row.qiniu_key)
        except Exception:
            payload['pdf_url'] = None
    return payload


def _load_json_field(raw: str | None):
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def list_filings(session: Session, code: str) -> QueryResult:
    normalized = normalize_stock_code(code)
    rows = (
        session.query(FilingDocument)
        .filter_by(code=normalized)
        .order_by(FilingDocument.year.desc(), FilingDocument.season.desc())
        .all()
    )
    if not rows:
        return QueryResult(rows=[], update_time=None, error=None)

    latest = max(
        (row.extracted_at or row.synced_at for row in rows),
        default=None,
    )
    update_time = latest.isoformat() if isinstance(latest, datetime.datetime) else None
    return QueryResult(
        total_count=len(rows),
        rows=[_serialize_filing_row(row) for row in rows],
        update_time=update_time,
    )


def get_filing(
    session: Session,
    code: str,
    year: int,
    season: int,
    *,
    include_pdf_url: bool = True,
) -> dict | None:
    normalized = normalize_stock_code(code)
    row = (
        session.query(FilingDocument)
        .filter_by(code=normalized, year=year, season=season)
        .first()
    )
    if row is None:
        return None
    return _serialize_filing_row(row, include_pdf_url=include_pdf_url)


def get_filing_content(session: Session, code: str, year: int, season: int) -> dict:
    normalized = normalize_stock_code(code)
    row = (
        session.query(FilingDocument)
        .filter_by(code=normalized, year=year, season=season)
        .first()
    )
    if row is None:
        return {'error': 'filing not found'}

    chunks = (
        session.query(FilingTextChunk)
        .filter_by(filing_id=row.id)
        .order_by(FilingTextChunk.chunk_index.asc())
        .all()
    )
    if not chunks:
        return {
            'error': 'filing text not extracted yet',
            'code': normalized,
            'year': year,
            'season': season,
            'analysis_status': row.analysis_status,
        }

    from filing.pdf_extract import build_analysis_text

    pages = [
        type('Page', (), {'page_no': chunk.page_no or (index + 1), 'content': chunk.content})()
        for index, chunk in enumerate(chunks)
    ]
    analysis_text = build_analysis_text(pages, max_chars=CONTENT_MAX_CHARS)

    return {
        'code': normalized,
        'year': year,
        'season': season,
        'report_type_label': row.report_type_label,
        'display_label': _display_label(row),
        'page_count': row.page_count or len(chunks),
        'analysis_status': row.analysis_status,
        'chunks': [
            {
                'page_no': chunk.page_no,
                'section': chunk.section,
                'chunk_index': chunk.chunk_index,
                'content': chunk.content,
            }
            for chunk in chunks
        ],
        'analysis_text': analysis_text,
    }


def get_filing_analysis(
    session: Session,
    code: str,
    year: int,
    season: int,
    *,
    analysis_version: str | None = None,
) -> dict | None:
    normalized = normalize_stock_code(code)
    row = (
        session.query(FilingDocument)
        .filter_by(code=normalized, year=year, season=season)
        .first()
    )
    if row is None:
        return None

    version = analysis_version or DEFAULT_ANALYSIS_VERSION
    cache_key = filing_analysis_cache_key(normalized, year, season, analysis_version=version)
    cached = cache_get_json(cache_key)
    if cached is not None:
        return cached

    analysis = (
        session.query(FilingAiAnalysis)
        .filter_by(filing_id=row.id, analysis_version=version)
        .order_by(FilingAiAnalysis.created_at.desc())
        .first()
    )
    if analysis is None:
        return None

    payload = {
        'code': normalized,
        'year': year,
        'season': season,
        'display_label': _display_label(row),
        'analysis_version': analysis.analysis_version,
        'model': analysis.model,
        'status': analysis.status,
        'summary': analysis.summary,
        'highlights': _load_json_field(analysis.highlights),
        'risks': _load_json_field(analysis.risks),
        'metrics_delta': _load_json_field(analysis.metrics_delta),
        'full_markdown': analysis.full_markdown,
        'disclaimer': analysis.disclaimer,
        'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
        'error_message': analysis.error_message,
    }
    cache_set_json(cache_key, payload)
    return payload


def upsert_filing_analysis(
    session: Session,
    code: str,
    year: int,
    season: int,
    payload: dict,
    *,
    analysis_version: str | None = None,
) -> dict:
    normalized = normalize_stock_code(code)
    row = (
        session.query(FilingDocument)
        .filter_by(code=normalized, year=year, season=season)
        .first()
    )
    if row is None:
        return {'error': 'filing not found'}

    version = analysis_version or payload.get('analysis_version') or DEFAULT_ANALYSIS_VERSION
    now = datetime.datetime.now()
    analysis = (
        session.query(FilingAiAnalysis)
        .filter_by(filing_id=row.id, analysis_version=version)
        .first()
    )

    highlights = payload.get('highlights')
    risks = payload.get('risks')
    metrics_delta = payload.get('metrics_delta')

    fields = {
        'model': payload.get('model'),
        'status': payload.get('status') or FilingAiAnalysis.STATUS_DONE,
        'summary': payload.get('summary'),
        'highlights': json.dumps(highlights, ensure_ascii=False) if highlights is not None else None,
        'risks': json.dumps(risks, ensure_ascii=False) if risks is not None else None,
        'metrics_delta': json.dumps(metrics_delta, ensure_ascii=False) if metrics_delta is not None else None,
        'full_markdown': payload.get('full_markdown'),
        'disclaimer': payload.get('disclaimer'),
        'error_message': payload.get('error_message'),
        'created_at': now,
    }

    if analysis is None:
        analysis = FilingAiAnalysis(
            filing_id=row.id,
            analysis_version=version,
            **fields,
        )
        session.add(analysis)
    else:
        for key, value in fields.items():
            setattr(analysis, key, value)

    if fields['status'] == FilingAiAnalysis.STATUS_DONE:
        row.analysis_status = FilingDocument.STATUS_DONE

    session.flush()
    return get_filing_analysis(session, normalized, year, season, analysis_version=version) or {'error': 'save failed'}
