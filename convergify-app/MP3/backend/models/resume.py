"""
Resume and OptimizedResume models
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json

from database import Base

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_text = Column(Text, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    analysis_status = Column(String, default="pending")
    extracted_skills = Column(Text)  # JSON array
    optimized_version_id = Column(String, ForeignKey("optimized_resumes.id"))
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")
    optimized_version = relationship("OptimizedResume", foreign_keys=[optimized_version_id])
    
    @property
    def skills_list(self):
        """Get extracted skills as Python list"""
        if self.extracted_skills:
            try:
                return json.loads(self.extracted_skills)
            except json.JSONDecodeError:
                return []
        return []
    
    @skills_list.setter
    def skills_list(self, value):
        """Set extracted skills from Python list"""
        if value:
            self.extracted_skills = json.dumps(value)
        else:
            self.extracted_skills = None
    
    def __repr__(self):
        return f"<Resume(id={self.id}, filename={self.filename}, status={self.analysis_status})>"

class OptimizedResume(Base):
    __tablename__ = "optimized_resumes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    original_resume_id = Column(String, ForeignKey("resumes.id"), nullable=False)
    optimized_text = Column(Text, nullable=False)
    changes = Column(Text, nullable=False)  # JSON array
    improvement_score = Column(Float)
    target_job_ids = Column(Text, nullable=False)  # JSON array
    generated_date = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String)
    
    # Relationships
    original_resume = relationship("Resume", foreign_keys=[original_resume_id])
    analyses = relationship("Analysis", back_populates="optimized_resume")
    
    @property
    def changes_list(self):
        """Get changes as Python list"""
        if self.changes:
            try:
                return json.loads(self.changes)
            except json.JSONDecodeError:
                return []
        return []
    
    @changes_list.setter
    def changes_list(self, value):
        """Set changes from Python list"""
        if value:
            self.changes = json.dumps(value)
        else:
            self.changes = "[]"
    
    @property
    def target_jobs_list(self):
        """Get target job IDs as Python list"""
        if self.target_job_ids:
            try:
                return json.loads(self.target_job_ids)
            except json.JSONDecodeError:
                return []
        return []
    
    @target_jobs_list.setter
    def target_jobs_list(self, value):
        """Set target job IDs from Python list"""
        if value:
            self.target_job_ids = json.dumps(value)
        else:
            self.target_job_ids = "[]"
    
    def __repr__(self):
        return f"<OptimizedResume(id={self.id}, score={self.improvement_score})>"