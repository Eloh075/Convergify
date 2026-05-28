"""add skill classification cache

Revision ID: 0007
Revises: 0006
Create Date: 2026-02-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns for caching classified skills
    op.add_column('jobs', sa.Column('classified_skills', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('classification_date', sa.DateTime(), nullable=True))
    op.add_column('jobs', sa.Column('classification_version', sa.String(), nullable=True, server_default='1.0'))
    

def downgrade():
    # Remove caching columns
    op.drop_column('jobs', 'classified_skills')
    op.drop_column('jobs', 'classification_date')
    op.drop_column('jobs', 'classification_version')
