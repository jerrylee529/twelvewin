"""phase6 analysis results tables

Revision ID: c7e2a9f41b30
Revises: b8f4a2c91d0e
Create Date: 2026-05-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c7e2a9f41b30'
down_revision = 'b8f4a2c91d0e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'analysis_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=32), nullable=False, comment='结果类别'),
        sa.Column('result_key', sa.String(length=64), nullable=False, comment='结果键'),
        sa.Column('as_of_date', sa.Date(), nullable=False, comment='数据截至日期'),
        sa.Column('row_count', sa.Integer(), nullable=False, comment='行数'),
        sa.Column('source_file', sa.String(length=512), nullable=True, comment='来源 CSV'),
        sa.Column('job_run_id', sa.Integer(), nullable=True),
        sa.Column('create_time', sa.DateTime(), nullable=False, comment='入库时间'),
        sa.ForeignKeyConstraint(['job_run_id'], ['analysis_job_run.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_analysis_runs_as_of_date'), 'analysis_runs', ['as_of_date'], unique=False)
    op.create_index(op.f('ix_analysis_runs_category'), 'analysis_runs', ['category'], unique=False)
    op.create_index(op.f('ix_analysis_runs_result_key'), 'analysis_runs', ['result_key'], unique=False)
    op.create_index(
        'ix_analysis_runs_category_key_date',
        'analysis_runs',
        ['category', 'result_key', 'as_of_date'],
        unique=False,
    )

    op.create_table(
        'ranking_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.Column('rank_order', sa.Integer(), nullable=False, comment='排名序号'),
        sa.Column('code', sa.String(length=16), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=True),
        sa.Column('data', sa.Text(), nullable=True, comment='完整行 JSON'),
        sa.ForeignKeyConstraint(['run_id'], ['analysis_runs.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_ranking_results_code'), 'ranking_results', ['code'], unique=False)
    op.create_index(op.f('ix_ranking_results_run_id'), 'ranking_results', ['run_id'], unique=False)
    op.create_index('ix_ranking_results_run_order', 'ranking_results', ['run_id', 'rank_order'], unique=False)

    op.create_table(
        'technical_screen_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.Column('rank_order', sa.Integer(), nullable=False, comment='排序序号'),
        sa.Column('code', sa.String(length=16), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=True),
        sa.Column('data', sa.Text(), nullable=True, comment='完整行 JSON'),
        sa.ForeignKeyConstraint(['run_id'], ['analysis_runs.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_technical_screen_results_code'), 'technical_screen_results', ['code'], unique=False)
    op.create_index(op.f('ix_technical_screen_results_run_id'), 'technical_screen_results', ['run_id'], unique=False)
    op.create_index(
        'ix_technical_screen_results_run_order',
        'technical_screen_results',
        ['run_id', 'rank_order'],
        unique=False,
    )


def downgrade():
    op.drop_index('ix_technical_screen_results_run_order', table_name='technical_screen_results')
    op.drop_index(op.f('ix_technical_screen_results_run_id'), table_name='technical_screen_results')
    op.drop_index(op.f('ix_technical_screen_results_code'), table_name='technical_screen_results')
    op.drop_table('technical_screen_results')

    op.drop_index('ix_ranking_results_run_order', table_name='ranking_results')
    op.drop_index(op.f('ix_ranking_results_run_id'), table_name='ranking_results')
    op.drop_index(op.f('ix_ranking_results_code'), table_name='ranking_results')
    op.drop_table('ranking_results')

    op.drop_index('ix_analysis_runs_category_key_date', table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_result_key'), table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_category'), table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_as_of_date'), table_name='analysis_runs')
    op.drop_table('analysis_runs')
