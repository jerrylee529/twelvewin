"""add analysis_job_run

Revision ID: b8f4a2c91d0e
Revises: 33e7716425a6
Create Date: 2026-05-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b8f4a2c91d0e'
down_revision = '33e7716425a6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'analysis_job_run',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_name', sa.String(length=128), nullable=False, comment='任务名称'),
        sa.Column('status', sa.String(length=32), nullable=False, comment='任务状态'),
        sa.Column('parameters', sa.Text(), nullable=True, comment='任务参数，JSON 字符串'),
        sa.Column('output', sa.Text(), nullable=True, comment='任务输出，JSON 字符串或文件路径'),
        sa.Column('error', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('started_at', sa.DateTime(), nullable=False, comment='开始时间'),
        sa.Column('finished_at', sa.DateTime(), nullable=True, comment='结束时间'),
        sa.Column('duration_seconds', sa.Float(), nullable=True, comment='运行耗时，秒'),
        sa.Column('create_time', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('update_time', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_analysis_job_run_job_name'), 'analysis_job_run', ['job_name'], unique=False)
    op.create_index(op.f('ix_analysis_job_run_status'), 'analysis_job_run', ['status'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_analysis_job_run_status'), table_name='analysis_job_run')
    op.drop_index(op.f('ix_analysis_job_run_job_name'), table_name='analysis_job_run')
    op.drop_table('analysis_job_run')
