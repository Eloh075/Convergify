"""
Initialize database with correct schema
"""
from database import Base, engine
from models.user import User
from models.resume import Resume, OptimizedResume
from models.job import Job, JobGroup
from models.analysis import Analysis
from models.session import AnalysisSession
from models.celery_task import CeleryTask

print("🗄️  Creating database tables...")

# Drop all tables first (if they exist)
Base.metadata.drop_all(bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ Database initialized successfully!")
print("   Tables created:")
print("   - users")
print("   - resumes")
print("   - optimized_resumes")
print("   - jobs")
print("   - job_groups")
print("   - analyses")
print("   - sessions")
print("   - celery_tasks")
