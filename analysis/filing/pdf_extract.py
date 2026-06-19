# -*- coding: utf-8 -*-

"""Extract plain text from filing PDF bytes."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


SECTION_KEYWORDS: dict[str, tuple[str, ...]] = {
    'management_discussion': (
        '管理层讨论与分析',
        '经营情况讨论与分析',
        '董事会报告',
    ),
    'risk_disclosure': (
        '风险提示',
        '风险因素',
        '重大风险提示',
    ),
    'financial_statements': (
        '合并利润表',
        '合并资产负债表',
        '合并现金流量表',
        '财务报表',
    ),
}


@dataclass(frozen=True)
class PdfPageText:
    page_no: int
    content: str


@dataclass(frozen=True)
class PdfExtractResult:
    file_hash: str
    page_count: int
    pages: list[PdfPageText]


def _require_fitz():
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError(
            'pymupdf is required for filing extraction. Install requirements-analysis.txt.'
        ) from exc
    return fitz


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_pdf_text(data: bytes) -> PdfExtractResult:
    fitz = _require_fitz()
    digest = sha256_hex(data)
    document = fitz.open(stream=data, filetype='pdf')
    pages: list[PdfPageText] = []

    try:
        for index in range(document.page_count):
            page = document.load_page(index)
            text = (page.get_text('text') or '').strip()
            if text:
                pages.append(PdfPageText(page_no=index + 1, content=text))
    finally:
        document.close()

    return PdfExtractResult(
        file_hash=digest,
        page_count=len(pages),
        pages=pages,
    )


def detect_section(text: str) -> str | None:
    normalized = re.sub(r'\s+', '', text)
    for section, keywords in SECTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized:
                return section
    return None


def build_analysis_text(pages: list[PdfPageText], *, max_chars: int = 120_000) -> str:
    """Prefer management/risk/financial sections; fall back to truncated full text."""
    selected: list[str] = []
    current_section = 'other'

    for page in pages:
        section = detect_section(page.content) or current_section
        if detect_section(page.content):
            current_section = section
        if section in {'management_discussion', 'risk_disclosure', 'financial_statements'}:
            selected.append(f'[p.{page.page_no}] {page.content}')

    if not selected:
        selected = [f'[p.{page.page_no}] {page.content}' for page in pages]

    combined = '\n\n'.join(selected)
    if len(combined) <= max_chars:
        return combined
    return combined[:max_chars]
