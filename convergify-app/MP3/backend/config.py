"""
Configuration settings for the Career Analysis Platform
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./career_analysis.db"
    
    # File storage
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".pdf", ".txt", ".doc", ".docx"]
    
    # Celery - Use database broker for development
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "sqla+sqlite:///celery_broker.db"
    celery_result_backend: str = "db+sqlite:///celery_results.db"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # External services
    gemini_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env

settings = Settings()