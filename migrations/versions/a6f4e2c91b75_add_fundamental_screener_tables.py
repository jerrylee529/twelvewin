"""add fundamental screener tables

Revision ID: a6f4e2c91b75
Revises: f2b8c3d91e04
Create Date: 2026-05-23 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

from migrations.util import (
    create_index_if_missing,
    create_table_if_missing,
    drop_index_if_exists,
    drop_table_if_exists,
)

revision = 'a6f4e2c91b75'
down_revision = 'f2b8c3d91e04'
branch_labels = None
depends_on = None


def upgrade():
    create_table_if_missing(
        'fundamental_snapshots',
        sa.Column('trade_date', sa.Date(), nullable=False),
        sa.Column('code', sa.String(length=16), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=True),
        sa.Column('industry', sa.String(length=64), nullable=True),
        sa.Column('is_st', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('close', sa.Float(), nullable=True),
        sa.Column('pe_ttm', sa.Float(), nullable=True),
        sa.Column('pb_lf', sa.Float(), nullable=True),
        sa.Column('roe', sa.Float(), nullable=True),
        sa.Column('roe_y1', sa.Float(), nullable=True),
        sa.Column('roe_y2', sa.Float(), nullable=True),
        sa.Column('roe_y3', sa.Float(), nullable=True),
        sa.Column('dividend_yield', sa.Float(), nullable=True),
        sa.Column('market_cap', sa.Float(), nullable=True),
        sa.Column('float_market_cap', sa.Float(), nullable=True),
        sa.Column('revenue_growth', sa.Float(), nullable=True),
        sa.Column('profit_growth', sa.Float(), nullable=True),
        sa.Column('pe_discount_to_industry', sa.Float(), nullable=True),
        sa.Column('pb_discount_to_industry', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=32), nullable=True),
        sa.Column('create_time', sa.DateTime(), nullable=False),
        sa.Column('update_time', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('trade_date', 'code'),
    )
    create_index_if_missing(
        'ix_fundamental_snapshots_date_industry',
        'fundamental_snapshots',
        ['trade_date', 'industry'],
        unique=False,
    )
    create_index_if_missing(
        'ix_fundamental_snapshots_date_pe',
        'fundamental_snapshots',
        ['trade_date', 'pe_ttm'],
        unique=False,
    )
    create_index_if_missing(
        'ix_fundamental_snapshots_date_pb',
        'fundamental_snapshots',
        ['trade_date', 'pb_lf'],
        unique=False,
    )
    create_index_if_missing(
        'ix_fundamental_snapshots_date_roe',
        'fundamental_snapshots',
        ['trade_date', 'roe'],
        unique=False,
    )
    create_index_if_missing(
        'ix_fundamental_snapshots_date_dividend',
        'fundamental_snapshots',
        ['trade_date', 'dividend_yield'],
        unique=False,
    )
    create_index_if_missing(
        'ix_fundamental_snapshots_date_float_mv',
        'fundamental_snapshots',
        ['trade_date', 'float_market_cap'],
        unique=False,
    )

    create_table_if_missing(
        'industry_fundamental_benchmarks',
        sa.Column('trade_date', sa.Date(), nullable=False),
        sa.Column('industry', sa.String(length=64), nullable=False),
        sa.Column('stock_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('median_pe_ttm', sa.Float(), nullable=True),
        sa.Column('median_pb_lf', sa.Float(), nullable=True),
        sa.Column('median_roe', sa.Float(), nullable=True),
        sa.Column('median_dividend_yield', sa.Float(), nullable=True),
        sa.Column('median_market_cap', sa.Float(), nullable=True),
        sa.Column('median_float_market_cap', sa.Float(), nullable=True),
        sa.Column('create_time', sa.DateTime(), nullable=False),
        sa.Column('update_time', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('trade_date', 'industry'),
    )


def downgrade():
    drop_index_if_exists('ix_fundamental_snapshots_date_float_mv', 'fundamental_snapshots')
    drop_index_if_exists('ix_fundamental_snapshots_date_dividend', 'fundamental_snapshots')
    drop_index_if_exists('ix_fundamental_snapshots_date_roe', 'fundamental_snapshots')
    drop_index_if_exists('ix_fundamental_snapshots_date_pb', 'fundamental_snapshots')
    drop_index_if_exists('ix_fundamental_snapshots_date_pe', 'fundamental_snapshots')
    drop_index_if_exists('ix_fundamental_snapshots_date_industry', 'fundamental_snapshots')
    drop_table_if_exists('industry_fundamental_benchmarks')
    drop_table_if_exists('fundamental_snapshots')
