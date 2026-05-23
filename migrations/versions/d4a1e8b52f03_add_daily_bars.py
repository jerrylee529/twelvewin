"""add daily_bars table

Revision ID: d4a1e8b52f03
Revises: c7e2a9f41b30
Create Date: 2026-05-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

from migrations.util import (
    create_index_if_missing,
    create_table_if_missing,
    drop_index_if_exists,
    drop_table_if_exists,
)

revision = 'd4a1e8b52f03'
down_revision = 'c7e2a9f41b30'
branch_labels = None
depends_on = None


def upgrade():
    create_table_if_missing(
        'daily_bars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=16), nullable=False),
        sa.Column('trade_date', sa.Date(), nullable=False),
        sa.Column('open', sa.Float(), nullable=True),
        sa.Column('high', sa.Float(), nullable=True),
        sa.Column('low', sa.Float(), nullable=True),
        sa.Column('close', sa.Float(), nullable=True),
        sa.Column('volume', sa.Float(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code', 'trade_date', name='uq_daily_bars_code_trade_date'),
    )
    create_index_if_missing(
        op.f('ix_daily_bars_code'),
        'daily_bars',
        ['code'],
        unique=False,
    )
    create_index_if_missing(
        op.f('ix_daily_bars_trade_date'),
        'daily_bars',
        ['trade_date'],
        unique=False,
    )
    create_index_if_missing(
        'ix_daily_bars_code_date',
        'daily_bars',
        ['code', 'trade_date'],
        unique=False,
    )


def downgrade():
    drop_index_if_exists('ix_daily_bars_code_date', 'daily_bars')
    drop_index_if_exists(op.f('ix_daily_bars_trade_date'), 'daily_bars')
    drop_index_if_exists(op.f('ix_daily_bars_code'), 'daily_bars')
    drop_table_if_exists('daily_bars')
