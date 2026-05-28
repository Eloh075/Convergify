"""
Resume-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ResumeCreate(BaseModel):
    """Schema for creating a resume"""
    filename: str = Field(..., description="Original filename")
    user_id: Optional[str] = None  # Will be set from session

class ResumeResponse(BaseModel):
    """Schema for resume response"""
    id: str
    user_id: str
    filename: str
    file_size: int
    upload_date: datetime
    analysis_status: str
    extracted_skills: Optional[List[str]] = None
    optimized_version_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class ResumeComparison(BaseModel):
    """Schema for resume comparison"""
    original: ResumeResponse
    optimized: Optional["OptimizedResumeResponse"] = None
    changes: List[dict] = []
    improvement_score: Optional[float] = None

class OptimizedResumeResponse(BaseModel):
    """Schema for optimized resume response"""
    id: str
    original_resume_id: str
    optimized_text: str
    changes: List[dict]
    improvement_score: Optional[float] = None
    target_job_ids: List[str]
    generated_date: datetime
    file_path: Optional[str] = None
    
    class Config:
        from_attributes = True

class ResumeUploadResponse(BaseModel):
    """Schema for resume upload response"""
    resume: ResumeResponse
    extracted_text: str
    processing_status: str

class ResumeListResponse(BaseModel):
    """Schema for resume list response"""
    resumes: List[ResumeResponse]
    total: int

class ResumeComparisonResponse(BaseModel):
    """Schema for resume comparison response"""
    original: dict
    optimized: dict
    comparison: dict

# Forward reference resolution
ResumeComparison.model_rebuild()