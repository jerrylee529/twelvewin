# -*- coding: utf-8 -*-

"""SQLAlchemy engine and session factory independent of Flask request context."""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import load_core_settings

_engine = None
_session_factory = None


def get_database_uri():
    settings = load_core_settings()
    uri = settings.get('SQLALCHEMY_DATABASE_URI')
    if not uri:
        raise RuntimeError(
            'DATABASE_URL is not set. Source .env or set TW_ANALYSIS_CONFIG_FILE.'
        )
    return uri


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(get_database_uri(), echo=False)
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine())
    return _session_factory


def get_session():
    return get_session_factory()()


@contextmanager
def session_scope():
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_engine():
    """Reset cached engine (for tests)."""
    global _engine, _session_factory
    _engine = None
    _session_factory = None
