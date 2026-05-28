"""
Job-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class JobCreateRequest(BaseModel):
    """Schema for creating a job"""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    description: str = Field(..., description="Job description")
    requirements: Optional[List[str]] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    skills: Optional[List[str]] = None

class JobResponse(BaseModel):
    """Schema for job response"""
    id: str
    title: str
    company: str
    description: str
    requirements: Optional[List[str]] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    source: str
    scraped_date: Optional[datetime] = None
    required_skills: Optional[List[str]] = None
    skills_processed: Optional[bool] = False
    group_id: Optional[str] = None
    created_date: datetime
    salary_range: str  # Computed property
    
    @classmethod
    def from_job_model(cls, job):
        """Create JobResponse from Job model using property getters"""
        return cls(
            id=job.id,
            title=job.title,
            company=job.company,
            description=job.description,
            requirements=job.requirements_list,  # Use property getter
            location=job.location,
            employment_type=job.employment_type,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            source=job.source,
            scraped_date=job.scraped_date,
            required_skills=job.skills_list,  # Use property getter
            skills_processed=job.skills_processed,
            group_id=job.group_id,
            created_date=job.created_date,
            salary_range=job.salary_range
        )
    
    class Config:
        from_attributes = True

class JobGroupCreateRequest(BaseModel):
    """Schema for creating a job group"""
    name: str = Field(..., description="Group name")
    description: Optional[str] = None
    job_ids: Optional[List[str]] = None

class JobGroupResponse(BaseModel):
    """Schema for job group response"""
    id: str
    name: str
    description: Optional[str] = None
    group_type: str = "custom"
    job_ids: List[str]
    
    @classmethod
    def from_job_group_model(cls, group):
        """Create JobGroupResponse from JobGroup model using property getters"""
        return cls(
            id=group.id,
            name=group.name,
            description=group.description,
            group_type=getattr(group, 'group_type', 'custom'),
            job_ids=group.job_ids_list  # Use property getter
        )
    
    class Config:
        from_attributes = True

class ScrapingRequest(BaseModel):
    """Schema for job scraping request"""
    search_terms: List[str] = Field(..., description="Search terms for job scraping")
    employment_type: Optional[str] = Field(default="full-time", description="Employment type filter")
    max_jobs: Optional[int] = Field(default=10, description="Maximum number of jobs to scrape")

class JobListResponse(BaseModel):
    """Schema for job list response"""
    jobs: List[JobResponse]
    total: int

class JobGroupListResponse(BaseModel):
    """Schema for job group list response"""
    groups: List[JobGroupResponse]
    total: int

class JobFilters(BaseModel):
    """Schema for job filtering"""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    source: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    skills: Optional[List[str]] = None
    group_id: Optional[str] = None

class ScrapingConfig(BaseModel):
    """Schema for job scraping configuration"""
    search_terms: List[str] = Field(..., description="Job search terms")
    location: Optional[str] = None
    max_jobs: int = Field(default=50, description="Maximum number of jobs to scrape")
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    
class ScrapingJob(BaseModel):
    """Schema for scraping job status"""
    id: str
    status: str
    progress: int  # 0-100
    total_jobs: int
    scraped_jobs: int
    errors: List[str]
    started_at: datetime
    estimated_completion: Optional[datetime] = None