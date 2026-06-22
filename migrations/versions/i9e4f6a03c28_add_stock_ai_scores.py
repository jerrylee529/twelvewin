"""add stock ai score cache table

Revision ID: i9e4f6a03c28
Revises: h8d3e5f92b17
Create Date: 2026-06-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

from migrations.util import (
    create_index_if_missing,
    create_table_if_missing,
    drop_index_if_exists,
    drop_table_if_exists,
)

revision = 'i9e4f6a03c28'
down_revision = 'h8d3e5f92b17'
branch_labels = None
depends_on = None


def upgrade():
    create_table_if_missing(
        'stock_ai_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=8), nullable=False),
        sa.Column('data_as_of', sa.String(length=10), nullable=False),
        sa.Column('score_version', sa.String(length=32), nullable=False),
        sa.Column('model', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('score_json', sa.Text(), nullable=True),
        sa.Column('markdown', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'code',
            'data_as_of',
            'score_version',
            name='uq_stock_ai_scores_code_date_version',
        ),
    )
    create_index_if_missing(
        'ix_stock_ai_scores_code_data_as_of',
        'stock_ai_scores',
        ['code', 'data_as_of'],
        unique=False,
    )


def downgrade():
    drop_index_if_exists('ix_stock_ai_scores_code_data_as_of', table_name='stock_ai_scores')
    drop_table_if_exists('stock_ai_scores')
