# -*- coding: utf-8 -*-

"""SQLAlchemy ORM models for the API layer (no Flask dependency)."""

import datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AnalysisRun(Base):
    __tablename__ = 'analysis_runs'

    CATEGORY_RANKING = 'ranking'
    CATEGORY_TECHNICAL = 'technical'
    CATEGORY_PRICE_CHANGE = 'price_change'
    CATEGORY_ANNUAL_STOCK = 'annual_stock'
    CATEGORY_ANNUAL_INDUSTRY = 'annual_industry'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    result_key: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    as_of_date: Mapped[datetime.date] = mapped_column(Date, index=True, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_file: Mapped[str | None] = mapped_column(String(512), nullable=True)
    job_run_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('analysis_job_run.id'), nullable=True)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)


class RankingResult(Base):
    __tablename__ = 'ranking_results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey('analysis_runs.id'), index=True, nullable=False)
    rank_order: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    data: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index('ix_ranking_results_run_order', 'run_id', 'rank_order'),
    )


class TechnicalScreenResult(Base):
    __tablename__ = 'technical_screen_results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey('analysis_runs.id'), index=True, nullable=False)
    rank_order: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    data: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index('ix_technical_screen_results_run_order', 'run_id', 'rank_order'),
    )


class DailyBar(Base):
    __tablename__ = 'daily_bars'

    code: Mapped[str] = mapped_column(String(16), primary_key=True)
    trade_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    open: Mapped[float | None] = mapped_column(Float, nullable=True)
    high: Mapped[float | None] = mapped_column(Float, nullable=True)
    low: Mapped[float | None] = mapped_column(Float, nullable=True)
    close: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume: Mapped[float | None] = mapped_column(Float, nullable=True)
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)


class FundamentalSnapshot(Base):
    __tablename__ = 'fundamental_snapshots'

    trade_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    code: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    is_st: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    close: Mapped[float | None] = mapped_column(Float, nullable=True)
    pe_ttm: Mapped[float | None] = mapped_column(Float, nullable=True)
    pb_lf: Mapped[float | None] = mapped_column(Float, nullable=True)
    roe: Mapped[float | None] = mapped_column(Float, nullable=True)
    roe_y1: Mapped[float | None] = mapped_column(Float, nullable=True)
    roe_y2: Mapped[float | None] = mapped_column(Float, nullable=True)
    roe_y3: Mapped[float | None] = mapped_column(Float, nullable=True)
    dividend_yield: Mapped[float | None] = mapped_column(Float, nullable=True)
    market_cap: Mapped[float | None] = mapped_column(Float, nullable=True)
    float_market_cap: Mapped[float | None] = mapped_column(Float, nullable=True)
    revenue_growth: Mapped[float | None] = mapped_column(Float, nullable=True)
    profit_growth: Mapped[float | None] = mapped_column(Float, nullable=True)
    pe_discount_to_industry: Mapped[float | None] = mapped_column(Float, nullable=True)
    pb_discount_to_industry: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        Index('ix_fundamental_snapshots_date_industry', 'trade_date', 'industry'),
        Index('ix_fundamental_snapshots_date_pe', 'trade_date', 'pe_ttm'),
        Index('ix_fundamental_snapshots_date_pb', 'trade_date', 'pb_lf'),
        Index('ix_fundamental_snapshots_date_roe', 'trade_date', 'roe'),
        Index('ix_fundamental_snapshots_date_dividend', 'trade_date', 'dividend_yield'),
        Index('ix_fundamental_snapshots_date_float_mv', 'trade_date', 'float_market_cap'),
    )


class IndustryFundamentalBenchmark(Base):
    __tablename__ = 'industry_fundamental_benchmarks'

    trade_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    industry: Mapped[str] = mapped_column(String(64), primary_key=True)
    stock_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    median_pe_ttm: Mapped[float | None] = mapped_column(Float, nullable=True)
    median_pb_lf: Mapped[float | None] = mapped_column(Float, nullable=True)
    median_roe: Mapped[float | None] = mapped_column(Float, nullable=True)
    median_dividend_yield: Mapped[float | None] = mapped_column(Float, nullable=True)
    median_market_cap: Mapped[float | None] = mapped_column(Float, nullable=True)
    median_float_market_cap: Mapped[float | None] = mapped_column(Float, nullable=True)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)


class Instrument(Base):
    __tablename__ = 'instrument'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(32), nullable=True)
    area: Mapped[str | None] = mapped_column(String(32), nullable=True)
    pe: Mapped[float | None] = mapped_column(Float, nullable=True)
    outstanding: Mapped[float | None] = mapped_column(Float, nullable=True)
    totals: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_assets: Mapped[float | None] = mapped_column(Float, nullable=True)
    liquid_assets: Mapped[float | None] = mapped_column(Float, nullable=True)
    fixed_assets: Mapped[float | None] = mapped_column(Float, nullable=True)
    esp: Mapped[float | None] = mapped_column(Float, nullable=True)
    bvps: Mapped[float | None] = mapped_column(Float, nullable=True)
    pb: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_2_market: Mapped[str | None] = mapped_column(String(16), nullable=True)
    gpr: Mapped[float | None] = mapped_column(Float, nullable=True)
    npr: Mapped[float | None] = mapped_column(Float, nullable=True)
    holders: Mapped[int | None] = mapped_column(Integer, nullable=True)


class StockCluster(Base):
    __tablename__ = 'stock_cluster'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section: Mapped[str] = mapped_column(String(16), nullable=False)
    code: Mapped[str] = mapped_column(String(8), nullable=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False)


class StockClusterItem(Base):
    __tablename__ = 'stock_cluster_item'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section: Mapped[str] = mapped_column(String(16), nullable=False)
    parent_code: Mapped[str] = mapped_column(String(8), nullable=False)
    code: Mapped[str] = mapped_column(String(8), nullable=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    corr: Mapped[float] = mapped_column(Float, nullable=False)


class StockLabels(Base):
    __tablename__ = 'stock_labels'

    code: Mapped[str] = mapped_column(String(8), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(32), nullable=True)
    labels: Mapped[str | None] = mapped_column(String(128), nullable=True)


class XueQiuReportInfo(Base):
    __tablename__ = 'xueqiu_report_info'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    security_code: Mapped[str] = mapped_column(String(8), index=True, nullable=False)
    security_name: Mapped[str] = mapped_column(String(8), index=True, nullable=False)
    report_type: Mapped[int] = mapped_column(Integer, nullable=False)
    report_data: Mapped[str] = mapped_column(Text, nullable=False)


class AnalysisJobRun(Base):
    __tablename__ = 'analysis_job_run'

    STATUS_RUNNING = 'running'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    parameters: Mapped[str | None] = mapped_column(Text, nullable=True)
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
