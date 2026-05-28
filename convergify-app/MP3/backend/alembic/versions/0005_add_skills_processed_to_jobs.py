"""add skills_processed to jobs

Revision ID: 0005
Revises: 0004
Create Date: 2026-02-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    # Add skills_processed column to jobs table
    # Default to True for existing jobs with required_skills, False otherwise
    op.add_column('jobs', sa.Column('skills_processed', sa.Boolean(), nullable=True, server_default='0'))
    
    # Update existing jobs: set skills_processed=True if required_skills is not null/empty
    op.execute("""
        UPDATE jobs 
        SET skills_processed = 1 
        WHERE required_skills IS NOT NULL 
        AND required_skills != '' 
        AND required_skills != '[]'
    """)


def downgrade():
    # Remove skills_processed column from jobs table
    op.drop_column('jobs', 'skills_processed')
