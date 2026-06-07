# -*- coding: utf-8 -*-

from typing import Any, Optional

from pydantic import BaseModel, Field


class TableResponse(BaseModel):
    total: int
    rows: list[dict[str, Any]] = Field(default_factory=list)
    updateTime: Optional[str] = None
    error: Optional[str] = None


class IndustriesResponse(BaseModel):
    industries: list[dict[str, Any]] = Field(default_factory=list)


class InstrumentsResponse(BaseModel):
    instruments: list[dict[str, Any]] = Field(default_factory=list)


class InstrumentsListResponse(BaseModel):
    total: int
    instruments: list[dict[str, Any]] = Field(default_factory=list)


class BarsResponse(BaseModel):
    rows: list[list[Any]] = Field(default_factory=list)
    updateTime: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = 'ok'


class QuoteResponse(BaseModel):
    quot: Optional[dict[str, Any]] = None
    quot_source: Optional[str] = None


class ProfileResponse(BaseModel):
    quot: Optional[dict[str, Any]] = None
    quot_source: Optional[str] = None
    net_profit_after_nrgal_atsolc: list[dict[str, Any]] = Field(default_factory=list)
    avg_roe: list[dict[str, Any]] = Field(default_factory=list)
    np_atsopc_nrgal_yoy: list[dict[str, Any]] = Field(default_factory=list)
    basic_eps: list[dict[str, Any]] = Field(default_factory=list)
    gross_selling_rate: list[dict[str, Any]] = Field(default_factory=list)
    np_per_share: list[dict[str, Any]] = Field(default_factory=list)


class ResearchContextResponse(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    industry: Optional[str] = None
    data_as_of: Optional[str] = None
    labels: Optional[str] = None
    fundamentals: Optional[dict[str, Any]] = None
    industry_benchmark: Optional[dict[str, Any]] = None
    technical_signals: list[str] = Field(default_factory=list)
    rankings: dict[str, int] = Field(default_factory=dict)
    quote: Optional[dict[str, Any]] = None
    bars_summary: Optional[dict[str, Any]] = None
    finance_profile: dict[str, Any] = Field(default_factory=dict)
    cluster_peers: list[dict[str, Any]] = Field(default_factory=list)
    artifacts_freshness: dict[str, Any] = Field(default_factory=dict)
    errors: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class ClusterChartResponse(BaseModel):
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)
    heatmap: dict[str, Any] = Field(default_factory=dict)
    clusters: list[dict[str, Any]] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)
    updateTime: Optional[str] = None
    error: Optional[str] = None
