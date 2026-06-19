# -*- coding: utf-8 -*-

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.db.session import get_db_session
from api.schemas.responses import TableResponse
from api.services.filings import (
    get_filing,
    get_filing_analysis,
    get_filing_content,
    list_filings,
    upsert_filing_analysis,
)

router = APIRouter(prefix='/stocks', tags=['filings'])


class FilingContentResponse(BaseModel):
    code: str | None = None
    year: int | None = None
    season: int | None = None
    report_type_label: str | None = None
    display_label: str | None = None
    page_count: int | None = None
    analysis_status: str | None = None
    chunks: list[dict[str, Any]] = Field(default_factory=list)
    analysis_text: str | None = None
    error: str | None = None


class FilingAnalysisResponse(BaseModel):
    code: str | None = None
    year: int | None = None
    season: int | None = None
    display_label: str | None = None
    analysis_version: str | None = None
    model: str | None = None
    status: str | None = None
    summary: str | None = None
    highlights: Any = None
    risks: Any = None
    metrics_delta: Any = None
    full_markdown: str | None = None
    disclaimer: str | None = None
    created_at: str | None = None
    error_message: str | None = None
    error: str | None = None


class FilingAnalysisUpsertRequest(BaseModel):
    model: str | None = None
    status: str | None = None
    summary: str | None = None
    highlights: Any = None
    risks: Any = None
    metrics_delta: Any = None
    full_markdown: str | None = None
    disclaimer: str | None = None
    error_message: str | None = None
    analysis_version: str | None = None


class FilingDetailResponse(BaseModel):
    filing: dict[str, Any] | None = None
    error: str | None = None


@router.get('/{code}/filings', response_model=TableResponse)
def filings_list(code: str, session: Session = Depends(get_db_session)):
    result = list_filings(session, code)
    return TableResponse(
        total=result.total or len(result.rows),
        rows=result.rows,
        updateTime=result.update_time,
        error=result.error,
    )


@router.get('/{code}/filings/{year}/{season}', response_model=FilingDetailResponse)
def filing_detail(
    code: str,
    year: int,
    season: int,
    session: Session = Depends(get_db_session),
):
    filing = get_filing(session, code, year, season, include_pdf_url=True)
    if filing is None:
        return FilingDetailResponse(error='filing not found')
    return FilingDetailResponse(filing=filing)


@router.get('/{code}/filings/{year}/{season}/content', response_model=FilingContentResponse)
def filing_content(
    code: str,
    year: int,
    season: int,
    session: Session = Depends(get_db_session),
):
    payload = get_filing_content(session, code, year, season)
    if payload.get('error'):
        return FilingContentResponse(**payload)
    return FilingContentResponse(**payload)


@router.get('/{code}/filings/{year}/{season}/analysis', response_model=FilingAnalysisResponse)
def filing_analysis(
    code: str,
    year: int,
    season: int,
    session: Session = Depends(get_db_session),
):
    payload = get_filing_analysis(session, code, year, season)
    if payload is None:
        raise HTTPException(status_code=404, detail='analysis not found')
    return FilingAnalysisResponse(**payload)


@router.put('/{code}/filings/{year}/{season}/analysis', response_model=FilingAnalysisResponse)
def filing_analysis_upsert(
    code: str,
    year: int,
    season: int,
    body: FilingAnalysisUpsertRequest,
    session: Session = Depends(get_db_session),
):
    payload = upsert_filing_analysis(
        session,
        code,
        year,
        season,
        body.model_dump(exclude_none=True),
    )
    session.commit()
    if payload.get('error'):
        raise HTTPException(status_code=404, detail=payload['error'])
    return FilingAnalysisResponse(**payload)
