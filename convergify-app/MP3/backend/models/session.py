"""
Session model for career analysis workflows
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import json

from database import Base

class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    
    # Session metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime)
    
    # Session state
    status = Column(String, default="active")  # active, completed, archived
    session_type = Column(String, default="comprehensive")  # comprehensive, single_job, market_analysis
    
    # Associated data IDs (JSON arrays)
    resume_ids = Column(Text, nullable=False, default="[]")  # JSON array of resume IDs
    job_ids = Column(Text, nullable=False, default="[]")  # JSON array of job IDs
    analysis_ids = Column(Text, nullable=False, default="[]")  # JSON array of analysis IDs
    
    # Session configuration and metadata
    configuration = Column(Text)  # JSON object with session settings
    tags = Column(Text)  # JSON array of user-defined tags
    
    # Summary statistics
    total_jobs = Column(Integer, default=0)
    total_resumes = Column(Integer, default=0)
    total_analyses = Column(Integer, default=0)
    overall_match_score = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    @property
    def resume_ids_list(self):
        """Get resume IDs as Python list"""
        if self.resume_ids:
            try:
                return json.loads(self.resume_ids)
            except json.JSONDecodeError:
                return []
        return []
    
    @resume_ids_list.setter
    def resume_ids_list(self, value):
        """Set resume IDs from Python list"""
        if value:
            self.resume_ids = json.dumps(value)
        else:
            self.resume_ids = "[]"
    
    @property
    def job_ids_list(self):
        """Get job IDs as Python list"""
        if self.job_ids:
            try:
                return json.loads(self.job_ids)
            except json.JSONDecodeError:
                return []
        return []
    
    @job_ids_list.setter
    def job_ids_list(self, value):
        """Set job IDs from Python list"""
        if value:
            self.job_ids = json.dumps(value)
        else:
            self.job_ids = "[]"
    
    @property
    def analysis_ids_list(self):
        """Get analysis IDs as Python list"""
        if self.analysis_ids:
            try:
                return json.loads(self.analysis_ids)
            except json.JSONDecodeError:
                return []
        return []
    
    @analysis_ids_list.setter
    def analysis_ids_list(self, value):
        """Set analysis IDs from Python list"""
        if value:
            self.analysis_ids = json.dumps(value)
        else:
            self.analysis_ids = "[]"
    
    @property
    def configuration_dict(self):
        """Get configuration as Python dict"""
        if self.configuration:
            try:
                return json.loads(self.configuration)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @configuration_dict.setter
    def configuration_dict(self, value):
        """Set configuration from Python dict"""
        if value:
            self.configuration = json.dumps(value)
        else:
            self.configuration = None
    
    @property
    def tags_list(self):
        """Get tags as Python list"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except json.JSONDecodeError:
                return []
        return []
    
    @tags_list.setter
    def tags_list(self, value):
        """Set tags from Python list"""
        if value:
            self.tags = json.dumps(value)
        else:
            self.tags = "[]"
    
    @property
    def duration(self):
        """Get session duration if completed"""
        if self.completed_at and self.created_at:
            return self.completed_at - self.created_at
        return None
    
    @property
    def is_completed(self):
        """Check if session is completed"""
        return self.status == "completed" and self.completed_at is not None
    
    def add_resume(self, resume_id: str):
        """Add a resume to this session"""
        resume_ids = self.resume_ids_list
        if resume_id not in resume_ids:
            resume_ids.append(resume_id)
            self.resume_ids_list = resume_ids
            self.total_resumes = len(resume_ids)
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_resume(self, resume_id: str):
        """Remove a resume from this session"""
        resume_ids = self.resume_ids_list
        if resume_id in resume_ids:
            resume_ids.remove(resume_id)
            self.resume_ids_list = resume_ids
            self.total_resumes = len(resume_ids)
            self.updated_at = datetime.now(timezone.utc)
    
    def add_job(self, job_id: str):
        """Add a job to this session"""
        job_ids = self.job_ids_list
        if job_id not in job_ids:
            job_ids.append(job_id)
            self.job_ids_list = job_ids
            self.total_jobs = len(job_ids)
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_job(self, job_id: str):
        """Remove a job from this session"""
        job_ids = self.job_ids_list
        if job_id in job_ids:
            job_ids.remove(job_id)
            self.job_ids_list = job_ids
            self.total_jobs = len(job_ids)
            self.updated_at = datetime.now(timezone.utc)
    
    def add_analysis(self, analysis_id: str):
        """Add an analysis to this session"""
        analysis_ids = self.analysis_ids_list
        if analysis_id not in analysis_ids:
            analysis_ids.append(analysis_id)
            self.analysis_ids_list = analysis_ids
            self.total_analyses = len(analysis_ids)
            self.updated_at = datetime.now(timezone.utc)
    
    def add_tag(self, tag: str):
        """Add a tag to this session"""
        tags = self.tags_list
        if tag not in tags:
            tags.append(tag)
            self.tags_list = tags
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_tag(self, tag: str):
        """Remove a tag from this session"""
        tags = self.tags_list
        if tag in tags:
            tags.remove(tag)
            self.tags_list = tags
            self.updated_at = datetime.now(timezone.utc)
    
    def mark_completed(self, overall_score: float = None):
        """Mark session as completed"""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        if overall_score is not None:
            self.overall_match_score = overall_score
    
    def archive(self):
        """Archive this session"""
        self.status = "archived"
        self.updated_at = datetime.now(timezone.utc)
    
    def restore(self):
        """Restore archived session to active"""
        self.status = "active"
        self.updated_at = datetime.now(timezone.utc)
    
    def update_configuration(self, config_updates: dict):
        """Update session configuration"""
        current_config = self.configuration_dict
        current_config.update(config_updates)
        self.configuration_dict = current_config
        self.updated_at = datetime.now(timezone.utc)
    
    def get_summary(self):
        """Get session summary for display"""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "session_type": self.session_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": str(self.duration) if self.duration else None,
            "total_resumes": self.total_resumes,
            "total_jobs": self.total_jobs,
            "total_analyses": self.total_analyses,
            "overall_match_score": self.overall_match_score,
            "tags": self.tags_list
        }
    
    def __repr__(self):
        return f"<AnalysisSession(id={self.id}, title={self.title}, status={self.status})>"