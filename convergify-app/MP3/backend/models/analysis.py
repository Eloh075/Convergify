"""
Analysis model for career analysis sessions
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json

from database import Base

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=False)
    job_ids = Column(Text, nullable=False)  # JSON array
    analysis_type = Column(String, default="comprehensive")
    status = Column(String, default="pending")
    task_id = Column(String)  # Celery task ID for tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, default=datetime.utcnow)  # Keep for backward compatibility
    started_at = Column(DateTime)  # When analysis actually started processing
    completion_date = Column(DateTime)
    results = Column(Text)  # JSON object
    error_message = Column(Text)  # Error details if failed
    optimized_resume_id = Column(String, ForeignKey("optimized_resumes.id"))
    
    # Relationships
    resume = relationship("Resume", back_populates="analyses")
    optimized_resume = relationship("OptimizedResume", back_populates="analyses")
    
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
    def results_dict(self):
        """Get analysis results as Python dict"""
        if self.results:
            try:
                return json.loads(self.results)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @results_dict.setter
    def results_dict(self, value):
        """Set analysis results from Python dict"""
        if value:
            self.results = json.dumps(value)
        else:
            self.results = None
    
    @property
    def duration(self):
        """Get analysis duration if completed"""
        if self.completion_date and self.start_date:
            return self.completion_date - self.start_date
        return None
    
    @property
    def completed_at(self):
        """Alias for completion_date for consistency"""
        return self.completion_date
    
    @property
    def is_completed(self):
        """Check if analysis is completed"""
        return self.status == "completed" and self.completion_date is not None
    
    @property
    def job_count(self):
        """Get number of jobs analyzed"""
        return len(self.job_ids_list)
    
    def mark_completed(self):
        """Mark analysis as completed"""
        self.status = "completed"
        self.completion_date = datetime.utcnow()
    
    def mark_failed(self, error_message=None):
        """Mark analysis as failed"""
        self.status = "failed"
        self.completion_date = datetime.utcnow()
        if error_message:
            results = self.results_dict
            results["error"] = error_message
            self.results_dict = results
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, status={self.status}, jobs={self.job_count})>"