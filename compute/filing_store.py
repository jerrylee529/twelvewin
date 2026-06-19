# -*- coding: utf-8 -*-

"""Persist filing sync and PDF extraction results."""

from __future__ import annotations

import datetime
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

ANALYSIS_DIR = os.path.join(PROJECT_ROOT, 'analysis')
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)

from core.db import session_scope
from core.filing_names import parse_filing_filename
from core.stock_codes import normalize_stock_code

from api.db.models import FilingDocument, FilingTextChunk


def _analysis_import(module: str):
    __import__(module)
    return sys.modules[module]


def sync_filings_from_qiniu(code: str | None = None, *, limit: int = 0) -> dict:
    qiniu_client = _analysis_import('filing.qiniu_client')
    now = datetime.datetime.now()
    inserted = 0
    updated = 0
    skipped = 0

    with session_scope() as session:
        for obj in qiniu_client.iter_filing_objects(code=code, limit=limit):
            parsed = parse_filing_filename(obj.key)
            if parsed is None:
                skipped += 1
                continue

            normalized_code = normalize_stock_code(parsed.code)
            row = session.query(FilingDocument).filter_by(qiniu_key=obj.key).first()
            if row is None:
                session.add(
                    FilingDocument(
                        code=normalized_code,
                        year=parsed.year,
                        season=parsed.season,
                        report_kind=parsed.report_kind,
                        report_type_label=parsed.report_type_label,
                        qiniu_key=obj.key,
                        filename=parsed.filename,
                        file_size=obj.size,
                        file_hash=obj.hash_value,
                        publish_date=parsed.publish_date,
                        analysis_status=FilingDocument.STATUS_PENDING,
                        synced_at=now,
                    )
                )
                inserted += 1
                continue

            changed = False
            if obj.hash_value and row.file_hash != obj.hash_value:
                row.file_hash = obj.hash_value
                row.analysis_status = FilingDocument.STATUS_PENDING
                changed = True
            if obj.size and row.file_size != obj.size:
                row.file_size = obj.size
                changed = True
            row.synced_at = now
            if changed:
                updated += 1
            else:
                skipped += 1

    return {
        'status': 'ok',
        'inserted': inserted,
        'updated': updated,
        'skipped': skipped,
    }


def extract_pending_filings(*, batch_size: int = 20, code: str | None = None) -> dict:
    pdf_extract = _analysis_import('filing.pdf_extract')
    qiniu_client = _analysis_import('filing.qiniu_client')
    processed = 0
    failed = 0

    with session_scope() as session:
        query = session.query(FilingDocument).filter(
            FilingDocument.analysis_status.in_(
                [FilingDocument.STATUS_PENDING, FilingDocument.STATUS_FAILED]
            )
        )
        if code:
            query = query.filter(FilingDocument.code == normalize_stock_code(code))
        rows = query.order_by(FilingDocument.year.desc(), FilingDocument.season.desc()).limit(batch_size).all()

        for row in rows:
            row.analysis_status = FilingDocument.STATUS_PROCESSING
            session.flush()
            try:
                pdf_bytes = qiniu_client.download_filing_bytes(row.qiniu_key)
                extracted = pdf_extract.extract_pdf_text(pdf_bytes)
                session.query(FilingTextChunk).filter_by(filing_id=row.id).delete()

                for index, page in enumerate(extracted.pages):
                    session.add(
                        FilingTextChunk(
                            filing_id=row.id,
                            page_no=page.page_no,
                            section=pdf_extract.detect_section(page.content),
                            chunk_index=index,
                            content=page.content,
                            token_count=max(1, len(page.content) // 4),
                        )
                    )

                row.file_hash = extracted.file_hash
                row.page_count = extracted.page_count
                row.extracted_at = datetime.datetime.now()
                row.analysis_status = FilingDocument.STATUS_EXTRACTED
                processed += 1
            except Exception as exc:
                row.analysis_status = FilingDocument.STATUS_FAILED
                failed += 1
                print(f'extract failed {row.qiniu_key}: {exc!r}')

    return {
        'status': 'ok',
        'processed': processed,
        'failed': failed,
    }


def save_filing_analysis(
    filing_id: int,
    *,
    analysis_version: str,
    model: str | None,
    summary: str | None,
    highlights,
    risks,
    metrics_delta,
    full_markdown: str | None,
    disclaimer: str | None,
    status: str = FilingDocument.STATUS_DONE,
    error_message: str | None = None,
) -> None:
    import json

    from api.db.models import FilingAiAnalysis

    now = datetime.datetime.now()
    with session_scope() as session:
        row = session.query(FilingDocument).filter_by(id=filing_id).first()
        if row is None:
            raise ValueError(f'filing {filing_id} not found')

        analysis = (
            session.query(FilingAiAnalysis)
            .filter_by(filing_id=filing_id, analysis_version=analysis_version)
            .first()
        )
        payload = {
            'model': model,
            'status': status,
            'summary': summary,
            'highlights': json.dumps(highlights, ensure_ascii=False) if highlights is not None else None,
            'risks': json.dumps(risks, ensure_ascii=False) if risks is not None else None,
            'metrics_delta': json.dumps(metrics_delta, ensure_ascii=False) if metrics_delta is not None else None,
            'full_markdown': full_markdown,
            'disclaimer': disclaimer,
            'error_message': error_message,
            'created_at': now,
        }
        if analysis is None:
            session.add(FilingAiAnalysis(filing_id=filing_id, analysis_version=analysis_version, **payload))
        else:
            for key, value in payload.items():
                setattr(analysis, key, value)

        if status == FilingAiAnalysis.STATUS_DONE:
            row.analysis_status = FilingDocument.STATUS_DONE
