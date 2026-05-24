# -*- coding: utf-8 -*-

"""Database session helpers built on core.db."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from core.db import get_session


def get_db_session() -> Generator[Session, None, None]:
    session = get_session()
    try:
        yield session
    finally:
        session.close()
