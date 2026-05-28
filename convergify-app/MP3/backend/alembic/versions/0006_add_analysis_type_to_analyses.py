"""add_analysis_type_to_analyses

Revision ID: 0006
Revises: 0005
Create Date: 2026-02-05 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None

def upgrade():
    # Add analysis_type column to analyses table
    op.add_column('analyses', sa.Column('analysis_type', sa.String(), nullable=True))
    
    # Set default value for existing records
    op.execute("UPDATE analyses SET analysis_type = 'comprehensive' WHERE analysis_type IS NULL")
    
    # Make the column non-nullable after setting defaults
    op.alter_column('analyses', 'analysis_type', nullable=False)

def downgrade():
    # Remove analysis_type column
    op.drop_column('analyses', 'analysis_type')