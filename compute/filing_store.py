# -*- coding: utf-8 -*-

"""Persist filing sync and PDF extraction results."""

from __future__ import annotations

import datetime
import json
import logging
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

ANALYSIS_DIR = os.path.join(PROJECT_ROOT, 'analysis')
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)

from core.config import LOCAL_DATA_DIR
from core.db import session_scope
from core.filing_names import parse_filing_filename
from core.stock_codes import normalize_stock_code

from api.db.models import FilingDocument, FilingTextChunk

logger = logging.getLogger(__name__)

CHECKPOINT_VERSION = 1
DEFAULT_CHECKPOINT_FILENAME = 'filing_sync_checkpoint.json'


def _analysis_import(module: str):
    __import__(module)
    return sys.modules[module]


def default_sync_checkpoint_path() -> str:
    os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    return os.path.join(LOCAL_DATA_DIR, DEFAULT_CHECKPOINT_FILENAME)


def load_sync_checkpoint(
    path: str | None = None,
    *,
    code: str | None = None,
) -> str | None:
    checkpoint_path = path or default_sync_checkpoint_path()
    if not os.path.exists(checkpoint_path):
        return None

    with open(checkpoint_path, 'r', encoding='utf-8') as handle:
        payload = json.load(handle)

    if payload.get('version') != CHECKPOINT_VERSION:
        return None

    checkpoint_code = payload.get('code')
    normalized_code = normalize_stock_code(code) if code else None
    if checkpoint_code != normalized_code:
        return None

    marker = payload.get('marker')
    return marker or None


def save_sync_checkpoint(
    marker: str | None,
    *,
    code: str | None = None,
    path: str | None = None,
) -> None:
    checkpoint_path = path or default_sync_checkpoint_path()
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)

    if marker is None:
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)
        return

    payload = {
        'version': CHECKPOINT_VERSION,
        'code': normalize_stock_code(code) if code else None,
        'marker': marker,
        'updated_at': datetime.datetime.now().isoformat(sep=' '),
    }
    with open(checkpoint_path, 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def count_extractable_filings(*, code: str | None = None) -> dict[str, int]:
    statuses = [
        FilingDocument.STATUS_PENDING,
        FilingDocument.STATUS_FAILED,
        FilingDocument.STATUS_PROCESSING,
    ]
    with session_scope() as session:
        counts: dict[str, int] = {}
        for status in statuses:
            query = session.query(FilingDocument).filter(FilingDocument.analysis_status == status)
            if code:
                query = query.filter(FilingDocument.code == normalize_stock_code(code))
            counts[status] = query.count()
        counts['total'] = sum(counts.values())
        return counts


def reset_stuck_filing_extractions(*, code: str | None = None) -> int:
    with session_scope() as session:
        query = session.query(FilingDocument).filter(
            FilingDocument.analysis_status == FilingDocument.STATUS_PROCESSING
        )
        if code:
            query = query.filter(FilingDocument.code == normalize_stock_code(code))
        rows = query.all()
        for row in rows:
            row.analysis_status = FilingDocument.STATUS_PENDING
        return len(rows)


def _upsert_filing_object(session, obj, now: datetime.datetime) -> str:
    parsed = parse_filing_filename(obj.key)
    if parsed is None:
        return 'skipped'

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
        return 'inserted'

    changed = False
    if obj.hash_value and row.file_hash != obj.hash_value:
        row.file_hash = obj.hash_value
        row.analysis_status = FilingDocument.STATUS_PENDING
        changed = True
    if obj.size and row.file_size != obj.size:
        row.file_size = obj.size
        changed = True
    row.synced_at = now
    return 'updated' if changed else 'skipped'


def sync_filings_from_qiniu(
    code: str | None = None,
    *,
    limit: int = 0,
    resume: bool = False,
    log_interval: int = 0,
    checkpoint_path: str | None = None,
) -> dict:
    qiniu_client = _analysis_import('filing.qiniu_client')
    now = datetime.datetime.now()
    inserted = 0
    updated = 0
    skipped = 0
    scanned = 0
    pages = 0
    marker = load_sync_checkpoint(checkpoint_path, code=code) if resume else None

    logger.info('filing sync started (code=%s, resume=%s)', code or 'all', resume)

    page_marker = marker
    while True:
        objects, next_marker, eof = qiniu_client.list_filing_objects_page(code, marker=page_marker)
        pages += 1

        with session_scope() as session:
            for obj in objects:
                outcome = _upsert_filing_object(session, obj, now)
                if outcome == 'inserted':
                    inserted += 1
                elif outcome == 'updated':
                    updated += 1
                else:
                    skipped += 1

                scanned += 1
                if log_interval > 0 and scanned % log_interval == 0:
                    logger.info(
                        'filing sync progress: scanned=%d inserted=%d updated=%d skipped=%d',
                        scanned,
                        inserted,
                        updated,
                        skipped,
                    )

                if limit > 0 and scanned >= limit:
                    save_sync_checkpoint(next_marker, code=code, path=checkpoint_path)
                    logger.info(
                        'filing sync stopped at limit=%d (inserted=%d updated=%d skipped=%d)',
                        limit,
                        inserted,
                        updated,
                        skipped,
                    )
                    return {
                        'status': 'ok',
                        'inserted': inserted,
                        'updated': updated,
                        'skipped': skipped,
                        'scanned': scanned,
                        'pages': pages,
                        'resumed': bool(marker),
                        'stopped_early': True,
                    }

        if resume:
            save_sync_checkpoint(None if eof else next_marker, code=code, path=checkpoint_path)

        if eof:
            break
        page_marker = next_marker

    logger.info(
        'filing sync finished: scanned=%d inserted=%d updated=%d skipped=%d',
        scanned,
        inserted,
        updated,
        skipped,
    )
    return {
        'status': 'ok',
        'inserted': inserted,
        'updated': updated,
        'skipped': skipped,
        'scanned': scanned,
        'pages': pages,
        'resumed': bool(marker),
        'stopped_early': False,
    }


def _count_company_actionable(session, stock_code: str) -> int:
    return (
        session.query(FilingDocument)
        .filter(
            FilingDocument.code == stock_code,
            FilingDocument.analysis_status.in_(
                [FilingDocument.STATUS_PENDING, FilingDocument.STATUS_FAILED]
            ),
        )
        .count()
    )


def _get_company_done_stats(session, stock_code: str) -> tuple[int, int]:
    processed = (
        session.query(FilingDocument)
        .filter(
            FilingDocument.code == stock_code,
            FilingDocument.analysis_status.in_(
                [FilingDocument.STATUS_EXTRACTED, FilingDocument.STATUS_DONE]
            ),
        )
        .count()
    )
    failed = (
        session.query(FilingDocument)
        .filter(
            FilingDocument.code == stock_code,
            FilingDocument.analysis_status == FilingDocument.STATUS_FAILED,
        )
        .count()
    )
    return processed, failed


def _log_company_done(session, stock_code: str) -> None:
    processed, failed = _get_company_done_stats(session, stock_code)
    if failed:
        logger.warning(
            'filing extract: %s done processed=%d failed=%d',
            stock_code,
            processed,
            failed,
        )
    else:
        logger.info('filing extract: %s done processed=%d', stock_code, processed)


def extract_pending_filings(*, batch_size: int = 20, code: str | None = None) -> dict:
    pdf_extract = _analysis_import('filing.pdf_extract')
    qiniu_client = _analysis_import('filing.qiniu_client')
    processed = 0
    failed = 0
    completed_codes: set[str] = set()

    with session_scope() as session:
        base_query = session.query(FilingDocument).filter(
            FilingDocument.analysis_status.in_(
                [FilingDocument.STATUS_PENDING, FilingDocument.STATUS_FAILED]
            )
        )
        if code:
            base_query = base_query.filter(FilingDocument.code == normalize_stock_code(code))

        total_queued = base_query.count()
        rows = (
            base_query.order_by(FilingDocument.year.desc(), FilingDocument.season.desc())
            .limit(batch_size)
            .all()
        )

        if not rows:
            return {
                'status': 'ok',
                'processed': 0,
                'failed': 0,
                'queued': total_queued,
                'batch_size': batch_size,
            }

        for row in rows:
            row.analysis_status = FilingDocument.STATUS_PROCESSING
            session.flush()
            try:
                with session.begin_nested():
                    pdf_bytes = qiniu_client.download_filing_bytes(row.qiniu_key)
                    extracted = pdf_extract.extract_pdf_text(pdf_bytes)
                    session.query(FilingTextChunk).filter_by(filing_id=row.id).delete()

                    for chunk_index, page in enumerate(extracted.pages):
                        session.add(
                            FilingTextChunk(
                                filing_id=row.id,
                                page_no=page.page_no,
                                section=pdf_extract.detect_section(page.content),
                                chunk_index=chunk_index,
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
                logger.warning('filing extract failed %s: %s', row.qiniu_key, exc)

            if row.code not in completed_codes and _count_company_actionable(session, row.code) == 0:
                completed_codes.add(row.code)
                _log_company_done(session, row.code)

    return {
        'status': 'ok',
        'processed': processed,
        'failed': failed,
        'queued': total_queued,
        'batch_size': batch_size,
    }


def extract_pending_filings_until_done(
    *,
    batch_size: int = 20,
    code: str | None = None,
    max_rounds: int = 0,
    reset_stuck: bool = False,
) -> dict:
    if reset_stuck:
        reset_stuck_filing_extractions(code=code)

    total_processed = 0
    total_failed = 0
    rounds = 0

    while True:
        counts = count_extractable_filings(code=code)
        actionable = (
            counts.get(FilingDocument.STATUS_PENDING, 0)
            + counts.get(FilingDocument.STATUS_FAILED, 0)
        )
        if actionable == 0:
            break

        rounds += 1
        result = extract_pending_filings(batch_size=batch_size, code=code)
        total_processed += result['processed']
        total_failed += result['failed']

        if result['processed'] + result['failed'] == 0:
            logger.warning('filing extract: no progress in round %d, stopping', rounds)
            break

        if max_rounds > 0 and rounds >= max_rounds:
            break

    if total_processed or total_failed:
        logger.info(
            'filing extract finished: processed=%d failed=%d rounds=%d',
            total_processed,
            total_failed,
            rounds,
        )

    return {
        'status': 'ok',
        'processed': total_processed,
        'failed': total_failed,
        'rounds': rounds,
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
