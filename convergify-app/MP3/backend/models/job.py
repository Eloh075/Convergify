"""
Job and JobGroup models
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json

from database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text)  # JSON array
    location = Column(String)
    employment_type = Column(String)  # full-time, part-time, contract, internship, etc.
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    source = Column(String, nullable=False)
    scraped_date = Column(DateTime)
    required_skills = Column(Text)  # JSON array
    skills_processed = Column(Boolean, default=False)  # Track if skills have been extracted
    classified_skills = Column(Text)  # JSON array of classified skills (cached)
    classification_date = Column(DateTime)  # When skills were last classified
    classification_version = Column(String, default='1.0')  # Version of classification algorithm
    group_id = Column(String, ForeignKey("job_groups.id"))
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    group = relationship("JobGroup", back_populates="jobs")
    
    @property
    def requirements_list(self):
        """Get requirements as Python list"""
        if self.requirements:
            try:
                return json.loads(self.requirements)
            except json.JSONDecodeError:
                return []
        return []
    
    @requirements_list.setter
    def requirements_list(self, value):
        """Set requirements from Python list"""
        if value:
            self.requirements = json.dumps(value)
        else:
            self.requirements = None
    
    @property
    def skills_list(self):
        """Get required skills as Python list"""
        if self.required_skills:
            try:
                return json.loads(self.required_skills)
            except json.JSONDecodeError:
                return []
        return []
    
    @skills_list.setter
    def skills_list(self, value):
        """Set required skills from Python list"""
        if value:
            self.required_skills = json.dumps(value)
        else:
            self.required_skills = None
    
    @property
    def classified_skills_list(self):
        """Get classified skills as Python list"""
        if self.classified_skills:
            try:
                return json.loads(self.classified_skills)
            except json.JSONDecodeError:
                return []
        return []
    
    @classified_skills_list.setter
    def classified_skills_list(self, value):
        """Set classified skills from Python list"""
        if value:
            self.classified_skills = json.dumps(value)
            self.classification_date = datetime.utcnow()
        else:
            self.classified_skills = None
            self.classification_date = None
    
    def has_cached_classification(self, version='1.0'):
        """Check if job has cached classification for given version"""
        return (
            self.classified_skills is not None and 
            self.classification_date is not None and
            self.classification_version == version
        )
    
    def should_reprocess_skills(self, max_age_days=30, version='1.0'):
        """Check if skills should be reprocessed"""
        if not self.has_cached_classification(version):
            return True
        
        # Check if cache is too old
        if self.classification_date:
            age = datetime.utcnow() - self.classification_date
            if age.days > max_age_days:
                return True
        
        return False
    
    @property
    def salary_range(self):
        """Get formatted salary range"""
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,}"
        elif self.salary_min:
            return f"${self.salary_min:,}+"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,}"
        return "Not specified"
    
    def __repr__(self):
        return f"<Job(id={self.id}, title={self.title}, company={self.company})>"

class JobGroup(Base):
    __tablename__ = "job_groups"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    group_type = Column(String, default="custom")  # "scraped" or "custom"
    job_ids = Column(Text, nullable=False)  # JSON array
    created_date = Column(DateTime, default=datetime.utcnow)
    analysis_results = Column(Text)  # JSON array
    
    # Relationships
    jobs = relationship("Job", back_populates="group")
    
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
    def analysis_results_list(self):
        """Get analysis results as Python list"""
        if self.analysis_results:
            try:
                return json.loads(self.analysis_results)
            except json.JSONDecodeError:
                return []
        return []
    
    @analysis_results_list.setter
    def analysis_results_list(self, value):
        """Set analysis results from Python list"""
        if value:
            self.analysis_results = json.dumps(value)
        else:
            self.analysis_results = None
    
    @property
    def job_count(self):
        """Get number of jobs in this group"""
        return len(self.job_ids_list)
    
    def __repr__(self):
        return f"<JobGroup(id={self.id}, name={self.name}, jobs={self.job_count})>"