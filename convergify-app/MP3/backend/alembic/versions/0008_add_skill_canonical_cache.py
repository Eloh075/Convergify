"""add skill canonical cache

Revision ID: 0008
Revises: 0007
Create Date: 2026-02-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade():
    # Create skill_canonical_cache table
    op.create_table(
        'skill_canonical_cache',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('skill_name', sa.String(), nullable=False),
        sa.Column('canonical_name', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('skill_name')
    )
    
    # Create indexes
    op.create_index('idx_skill_name', 'skill_canonical_cache', ['skill_name'])
    op.create_index('idx_canonical_name', 'skill_canonical_cache', ['canonical_name'])
    op.create_index('idx_skill_canonical_lookup', 'skill_canonical_cache', ['skill_name', 'canonical_name'])
    
    # Seed with common AI/ML mappings
    op.execute("""
        INSERT INTO skill_canonical_cache (skill_name, canonical_name, confidence) VALUES
        ('Generative AI', 'Artificial Intelligence (AI)', 1.0),
        ('AI Agents', 'Artificial Intelligence (AI)', 1.0),
        ('AI Architecture', 'Artificial Intelligence (AI)', 1.0),
        ('Machine Learning', 'Artificial Intelligence (AI)', 1.0),
        ('Deep Learning', 'Artificial Intelligence (AI)', 1.0),
        ('ML', 'Artificial Intelligence (AI)', 1.0),
        ('MLOps', 'Artificial Intelligence (AI)', 1.0),
        ('NLP', 'Artificial Intelligence (AI)', 1.0),
        ('Computer Vision', 'Artificial Intelligence (AI)', 1.0),
        ('LLM', 'Artificial Intelligence (AI)', 1.0),
        ('Large Language Models', 'Artificial Intelligence (AI)', 1.0),
        ('Neural Networks', 'Artificial Intelligence (AI)', 1.0),
        ('Transformer Models', 'Artificial Intelligence (AI)', 1.0),
        ('Reinforcement Learning', 'Artificial Intelligence (AI)', 1.0),
        ('Prompt Engineering', 'Artificial Intelligence (AI)', 1.0),
        ('RAG', 'Artificial Intelligence (AI)', 1.0),
        ('React.js', 'React', 1.0),
        ('ReactJS', 'React', 1.0),
        ('React Native', 'React', 1.0),
        ('Node.js', 'Node.js', 1.0),
        ('NodeJS', 'Node.js', 1.0),
        ('JavaScript', 'JavaScript', 1.0),
        ('JS', 'JavaScript', 1.0),
        ('TypeScript', 'TypeScript', 1.0),
        ('TS', 'TypeScript', 1.0),
        ('Python 3', 'Python', 1.0),
        ('Python Programming', 'Python', 1.0),
        ('PyTorch', 'PyTorch', 1.0),
        ('TensorFlow', 'TensorFlow', 1.0),
        ('Kubernetes', 'Kubernetes', 1.0),
        ('K8s', 'Kubernetes', 1.0),
        ('Docker', 'Docker', 1.0),
        ('AWS', 'AWS', 1.0),
        ('Amazon Web Services', 'AWS', 1.0),
        ('GCP', 'GCP', 1.0),
        ('Google Cloud Platform', 'GCP', 1.0),
        ('Azure', 'Azure', 1.0),
        ('Microsoft Azure', 'Azure', 1.0)
    """)


def downgrade():
    # Drop indexes
    op.drop_index('idx_skill_canonical_lookup', 'skill_canonical_cache')
    op.drop_index('idx_canonical_name', 'skill_canonical_cache')
    op.drop_index('idx_skill_name', 'skill_canonical_cache')
    
    # Drop table
    op.drop_table('skill_canonical_cache')
