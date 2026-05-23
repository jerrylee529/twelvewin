# -*- coding: utf-8 -*-

"""Re-export ORM models and sessions — define new tables in app.models only."""

from analysis.db import get_engine, get_session, get_session_factory, session_scope
from app.models import (
    Instrument,
    Report,
    StockCluster,
    StockClusterItem,
    StockPrediction,
    StrategyResultInfo,
    XueQiuReportInfo,
)

# Legacy alias: Session() returns a new SQLAlchemy session bound to the shared engine.
Session = get_session_factory()
engine = get_engine()

__all__ = [
    'Instrument',
    'Report',
    'StockCluster',
    'StockClusterItem',
    'StockPrediction',
    'StrategyResultInfo',
    'XueQiuReportInfo',
    'Session',
    'engine',
    'get_engine',
    'get_session',
    'session_scope',
]
