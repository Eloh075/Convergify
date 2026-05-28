"""Add sessions table

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create analysis_sessions table
    op.create_table('analysis_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('session_type', sa.String(), nullable=True),
        sa.Column('resume_ids', sa.Text(), nullable=False),
        sa.Column('job_ids', sa.Text(), nullable=False),
        sa.Column('analysis_ids', sa.Text(), nullable=False),
        sa.Column('configuration', sa.Text(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('total_jobs', sa.Integer(), nullable=True),
        sa.Column('total_resumes', sa.Integer(), nullable=True),
        sa.Column('total_analyses', sa.Integer(), nullable=True),
        sa.Column('overall_match_score', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('analysis_sessions')