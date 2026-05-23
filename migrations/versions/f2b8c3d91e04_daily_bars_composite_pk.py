"""daily_bars composite primary key (code, trade_date)

Revision ID: f2b8c3d91e04
Revises: e9c4f1a72b05
Create Date: 2026-05-23 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

from migrations.util import drop_index_if_exists, index_exists, table_exists

revision = 'f2b8c3d91e04'
down_revision = 'e9c4f1a72b05'
branch_labels = None
depends_on = None


def _has_id_column():
    if not table_exists('daily_bars'):
        return False
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return 'id' in {col['name'] for col in inspector.get_columns('daily_bars')}


def upgrade():
    if not table_exists('daily_bars') or not _has_id_column():
        return

    drop_index_if_exists('ix_daily_bars_code_date', 'daily_bars')

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    constraints = {item['name'] for item in inspector.get_unique_constraints('daily_bars')}
    if 'uq_daily_bars_code_trade_date' in constraints:
        op.drop_constraint('uq_daily_bars_code_trade_date', 'daily_bars', type_='unique')

    op.drop_constraint('daily_bars_pkey', 'daily_bars', type_='primary')
    op.drop_column('daily_bars', 'id')
    op.create_primary_key('daily_bars_pkey', 'daily_bars', ['code', 'trade_date'])


def downgrade():
    if not table_exists('daily_bars') or _has_id_column():
        return

    op.drop_constraint('daily_bars_pkey', 'daily_bars', type_='primary')
    op.add_column('daily_bars', sa.Column('id', sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE daily_bars AS db
            SET id = numbered.rn
            FROM (
                SELECT code, trade_date,
                       ROW_NUMBER() OVER (ORDER BY code, trade_date) AS rn
                FROM daily_bars
            ) AS numbered
            WHERE db.code = numbered.code
              AND db.trade_date = numbered.trade_date
            """
        )
    )
    op.alter_column('daily_bars', 'id', nullable=False)
    op.create_primary_key('daily_bars_pkey', 'daily_bars', ['id'])
    op.create_unique_constraint(
        'uq_daily_bars_code_trade_date',
        'daily_bars',
        ['code', 'trade_date'],
    )
    if not index_exists('daily_bars', 'ix_daily_bars_code_date'):
        op.create_index('ix_daily_bars_code_date', 'daily_bars', ['code', 'trade_date'], unique=False)
