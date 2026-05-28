"""add employment_type to jobs

Revision ID: 0003
Revises: 0002
Create Date: 2026-02-04 19:58:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    # Add employment_type column to jobs table
    op.add_column('jobs', sa.Column('employment_type', sa.String(), nullable=True))


def downgrade():
    # Remove employment_type column from jobs table
    op.drop_column('jobs', 'employment_type')