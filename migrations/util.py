# -*- coding: utf-8 -*-

"""Idempotent helpers for databases partially initialized outside Alembic."""

from alembic import op
import sqlalchemy as sa


def table_exists(name):
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return name in inspector.get_table_names()


def index_exists(table_name, index_name):
    if not table_exists(table_name):
        return False
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return index_name in {item['name'] for item in inspector.get_indexes(table_name)}


def create_table_if_missing(table_name, *columns, **kwargs):
    if not table_exists(table_name):
        op.create_table(table_name, *columns, **kwargs)


def create_index_if_missing(index_name, table_name, columns, **kwargs):
    if table_exists(table_name) and not index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns, **kwargs)


def drop_table_if_exists(table_name):
    if table_exists(table_name):
        op.drop_table(table_name)


def drop_index_if_exists(index_name, table_name):
    if table_exists(table_name) and index_exists(table_name, index_name):
        op.drop_index(index_name, table_name=table_name)
