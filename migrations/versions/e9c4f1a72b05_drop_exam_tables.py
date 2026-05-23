"""drop exam_question and exam_result tables

Revision ID: e9c4f1a72b05
Revises: d4a1e8b52f03
Create Date: 2026-05-22 12:00:00.000000

"""
from alembic import op

from migrations.util import drop_index_if_exists, drop_table_if_exists

revision = 'e9c4f1a72b05'
down_revision = 'd4a1e8b52f03'
branch_labels = None
depends_on = None


def upgrade():
    drop_index_if_exists(op.f('ix_exam_question_title'), 'exam_question')
    drop_table_if_exists('exam_result')
    drop_table_if_exists('exam_question')


def downgrade():
    import sqlalchemy as sa

    op.create_table(
        'exam_question',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False, comment='试题描述'),
        sa.Column('type', sa.Integer(), nullable=False, comment='试题类型, 0: 单选题, 1: 多选题, 2: 是非题'),
        sa.Column('score', sa.Integer(), nullable=False, comment='试题分数'),
        sa.Column('right_answer', sa.String(length=16), nullable=False, comment='正确答案'),
        sa.Column('option_a', sa.String(length=32), nullable=False, comment='选项A'),
        sa.Column('option_b', sa.String(length=32), nullable=False, comment='选项B'),
        sa.Column('option_c', sa.String(length=32), nullable=True, comment='选项C'),
        sa.Column('option_d', sa.String(length=32), nullable=True, comment='选项D'),
        sa.Column('option_e', sa.String(length=32), nullable=True, comment='选项E'),
        sa.Column('option_f', sa.String(length=32), nullable=True, comment='选项F'),
        sa.Column('create_time', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('update_time', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_exam_question_title'),
        'exam_question',
        ['title'],
        unique=False,
    )
    op.create_table(
        'exam_result',
        sa.Column('user_nickname', sa.String(length=128), nullable=False, comment='试题描述'),
        sa.Column('score', sa.Integer(), nullable=False, comment='考试得分'),
        sa.Column('create_time', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('update_time', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('user_nickname'),
    )
