"""add stock_cluster_chart table

Revision ID: g7c2d4e81a06
Revises: a6f4e2c91b75
Create Date: 2026-05-25 21:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

from migrations.util import create_table_if_missing, drop_table_if_exists

revision = 'g7c2d4e81a06'
down_revision = 'a6f4e2c91b75'
branch_labels = None
depends_on = None


def upgrade():
    create_table_if_missing(
        'stock_cluster_chart',
        sa.Column('section', sa.String(length=64), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('update_time', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('section'),
    )


def downgrade():
    drop_table_if_exists('stock_cluster_chart')
