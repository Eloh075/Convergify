"""add group_type to job_groups

Revision ID: 0004
Revises: 0003
Create Date: 2026-02-04 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    # Add group_type column to job_groups table
    op.add_column('job_groups', sa.Column('group_type', sa.String(), nullable=True, server_default='custom'))


def downgrade():
    # Remove group_type column from job_groups table
    op.drop_column('job_groups', 'group_type')