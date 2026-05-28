"""
Analysis-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

class AnalysisCreateRequest(BaseModel):
    """Schema for creating an analysis"""
    resume_id: str = Field(..., description="Resume ID to analyze")
    job_ids: Optional[List[str]] = None
    analysis_type: str = Field(default="comprehensive", description="Type of analysis")

class SkillGap(BaseModel):
    """Schema for skill gap analysis"""
    skill: str
    category: str
    importance: float = Field(..., ge=0, le=1)
    market_demand: float = Field(..., ge=0, le=1)
    learning_resources: Optional[List[Dict[str, Any]]] = None

class MarketInsights(BaseModel):
    """Schema for market insights"""
    top_skills: List[Dict[str, Any]]
    industry_trends: List[Dict[str, Any]]
    competition_level: str
    average_salary: Optional[Dict[str, Any]] = None

class AnalysisResults(BaseModel):
    """Schema for comprehensive analysis results"""
    skill_gaps: List[SkillGap]
    skill_overlaps: List[Dict[str, Any]]
    market_insights: MarketInsights
    recommendations: List[Dict[str, Any]]
    career_path_suggestions: List[Dict[str, Any]]
    salary_insights: Optional[Dict[str, Any]] = None
    match_score: Optional[float] = None

class AnalysisResponse(BaseModel):
    """Schema for analysis response"""
    id: str
    resume_id: str
    job_ids: List[str]
    analysis_type: str
    status: str
    start_date: datetime
    completion_date: Optional[datetime] = None
    results: Optional[AnalysisResults] = None
    optimized_resume_id: Optional[str] = None
    duration: Optional[timedelta] = None
    job_count: int
    
    @classmethod
    def from_orm(cls, analysis):
        """Create AnalysisResponse from Analysis ORM object"""
        return cls(
            id=analysis.id,
            resume_id=analysis.resume_id,
            job_ids=analysis.job_ids_list,  # Use the property that returns a list
            analysis_type=analysis.analysis_type,
            status=analysis.status,
            start_date=analysis.start_date,
            completion_date=analysis.completion_date,
            results=None,  # Will be populated separately if needed
            optimized_resume_id=analysis.optimized_resume_id,
            duration=analysis.duration,
            job_count=analysis.job_count
        )
    
    class Config:
        from_attributes = True

class AnalysisResultsResponse(BaseModel):
    """Schema for detailed analysis results"""
    analysis_id: str
    resume_id: str
    resume_filename: Optional[str] = None
    job_count: int
    job_titles: List[str]
    analysis_type: str
    status: str
    results: Dict[str, Any]
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class AnalysisListResponse(BaseModel):
    """Schema for analysis list response"""
    analyses: List[AnalysisResponse]
    total: int

class AnalysisStatus(BaseModel):
    """Schema for analysis status updates"""
    id: str
    status: str
    progress: int  # 0-100
    current_step: str
    estimated_completion: Optional[datetime] = None
    error: Optional[str] = None

class ExportFormat(BaseModel):
    """Schema for export format specification"""
    format: str = Field(..., description="Export format (pdf, json, csv)")
    include_raw_data: bool = Field(default=False)
    include_visualizations: bool = Field(default=True)

class ExportResult(BaseModel):
    """Schema for export result"""
    file_path: str
    file_size: int
    format: str
    generated_at: datetime
    download_url: str