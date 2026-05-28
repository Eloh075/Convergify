"""Initial migration - Create all tables

Revision ID: 0001
Revises: 
Create Date: 2026-02-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create optimized_resumes table (before resumes due to FK)
    op.create_table('optimized_resumes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('original_resume_id', sa.String(), nullable=False),
        sa.Column('optimized_text', sa.Text(), nullable=False),
        sa.Column('changes', sa.Text(), nullable=False),
        sa.Column('improvement_score', sa.Float(), nullable=True),
        sa.Column('target_job_ids', sa.Text(), nullable=False),
        sa.Column('generated_date', sa.DateTime(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create resumes table
    op.create_table('resumes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('upload_date', sa.DateTime(), nullable=True),
        sa.Column('analysis_status', sa.String(), nullable=True),
        sa.Column('extracted_skills', sa.Text(), nullable=True),
        sa.Column('optimized_version_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['optimized_version_id'], ['optimized_resumes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create job_groups table (before jobs due to FK)
    op.create_table('job_groups',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('job_ids', sa.Text(), nullable=False),
        sa.Column('created_date', sa.DateTime(), nullable=True),
        sa.Column('analysis_results', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create jobs table
    op.create_table('jobs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('scraped_date', sa.DateTime(), nullable=True),
        sa.Column('required_skills', sa.Text(), nullable=True),
        sa.Column('group_id', sa.String(), nullable=True),
        sa.Column('created_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['job_groups.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create analyses table
    op.create_table('analyses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('resume_id', sa.String(), nullable=False),
        sa.Column('job_ids', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('completion_date', sa.DateTime(), nullable=True),
        sa.Column('results', sa.Text(), nullable=True),
        sa.Column('optimized_resume_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['optimized_resume_id'], ['optimized_resumes.id'], ),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create celery_tasks table
    op.create_table('celery_tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('task_id', sa.String(), nullable=False),
        sa.Column('task_name', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('args', sa.Text(), nullable=True),
        sa.Column('kwargs', sa.Text(), nullable=True),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id')
    )
    
    # Add foreign key constraint for optimized_resumes.original_resume_id
    op.create_foreign_key(
        'fk_optimized_resumes_original_resume_id',
        'optimized_resumes', 'resumes',
        ['original_resume_id'], ['id']
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('celery_tasks')
    op.drop_table('analyses')
    op.drop_table('jobs')
    op.drop_table('job_groups')
    op.drop_table('resumes')
    op.drop_table('optimized_resumes')
    op.drop_table('users')