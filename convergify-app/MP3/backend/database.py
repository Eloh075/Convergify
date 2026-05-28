"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import os

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    # Import all models to ensure they're registered
    from models import User, Resume, OptimizedResume, Job, JobGroup, Analysis, CeleryTask, SkillCanonical
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully")

def check_db_exists():
    """Check if database file exists (for SQLite)"""
    if "sqlite" in settings.database_url:
        db_path = settings.database_url.replace("sqlite:///", "")
        return os.path.exists(db_path)
    return True

def get_db_info():
    """Get database information"""
    return {
        "url": settings.database_url,
        "exists": check_db_exists(),
        "engine": str(engine.url)
    }