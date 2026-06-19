"""add filing document tables

Revision ID: h8d3e5f92b17
Revises: g7c2d4e81a06
Create Date: 2026-06-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

from migrations.util import (
    create_index_if_missing,
    create_table_if_missing,
    drop_index_if_exists,
    drop_table_if_exists,
)

revision = 'h8d3e5f92b17'
down_revision = 'g7c2d4e81a06'
branch_labels = None
depends_on = None


def upgrade():
    create_table_if_missing(
        'filing_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=8), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=False),
        sa.Column('report_kind', sa.String(length=16), nullable=False),
        sa.Column('report_type_label', sa.String(length=32), nullable=False),
        sa.Column('qiniu_key', sa.String(length=512), nullable=False),
        sa.Column('filename', sa.String(length=256), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('file_hash', sa.String(length=64), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('publish_date', sa.Date(), nullable=True),
        sa.Column('analysis_status', sa.String(length=16), nullable=False, server_default='pending'),
        sa.Column('synced_at', sa.DateTime(), nullable=False),
        sa.Column('extracted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('qiniu_key'),
    )
    create_index_if_missing(
        'ix_filing_documents_code_year_season',
        'filing_documents',
        ['code', 'year', 'season'],
        unique=False,
    )

    create_table_if_missing(
        'filing_text_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filing_id', sa.Integer(), nullable=False),
        sa.Column('page_no', sa.Integer(), nullable=True),
        sa.Column('section', sa.String(length=64), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['filing_id'], ['filing_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    create_index_if_missing(
        'ix_filing_text_chunks_filing_id',
        'filing_text_chunks',
        ['filing_id'],
        unique=False,
    )

    create_table_if_missing(
        'filing_ai_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filing_id', sa.Integer(), nullable=False),
        sa.Column('analysis_version', sa.String(length=32), nullable=False),
        sa.Column('model', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('highlights', sa.Text(), nullable=True),
        sa.Column('risks', sa.Text(), nullable=True),
        sa.Column('metrics_delta', sa.Text(), nullable=True),
        sa.Column('full_markdown', sa.Text(), nullable=True),
        sa.Column('disclaimer', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['filing_id'], ['filing_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('filing_id', 'analysis_version', name='uq_filing_ai_analyses_filing_version'),
    )
    create_index_if_missing(
        'ix_filing_ai_analyses_filing_id',
        'filing_ai_analyses',
        ['filing_id'],
        unique=False,
    )


def downgrade():
    drop_index_if_exists('ix_filing_ai_analyses_filing_id', 'filing_ai_analyses')
    drop_table_if_exists('filing_ai_analyses')
    drop_index_if_exists('ix_filing_text_chunks_filing_id', 'filing_text_chunks')
    drop_table_if_exists('filing_text_chunks')
    drop_index_if_exists('ix_filing_documents_code_year_season', 'filing_documents')
    drop_table_if_exists('filing_documents')
