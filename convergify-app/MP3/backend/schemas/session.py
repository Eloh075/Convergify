"""
Session-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class SessionCreateRequest(BaseModel):
    """Schema for creating a session"""
    title: str = Field(..., description="Session title")
    session_type: str = Field(default="comprehensive", description="Type of session")
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class SessionUpdateRequest(BaseModel):
    """Schema for updating a session"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    session_type: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class SessionResponse(BaseModel):
    """Schema for session response"""
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    session_type: str
    resume_ids: List[str]
    job_ids: List[str]
    analysis_ids: List[str]
    configuration: Optional[Dict[str, Any]] = None
    tags: List[str]
    total_jobs: int
    total_resumes: int
    total_analyses: int
    overall_match_score: Optional[float] = None
    
    @classmethod
    def from_session(cls, session):
        """Create SessionResponse from AnalysisSession model"""
        return cls(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            description=session.description,
            created_at=session.created_at,
            updated_at=session.updated_at,
            completed_at=session.completed_at,
            status=session.status,
            session_type=session.session_type,
            resume_ids=session.resume_ids_list,
            job_ids=session.job_ids_list,
            analysis_ids=session.analysis_ids_list,
            configuration=session.configuration_dict,
            tags=session.tags_list,
            total_jobs=session.total_jobs,
            total_resumes=session.total_resumes,
            total_analyses=session.total_analyses,
            overall_match_score=session.overall_match_score
        )

class SessionSummaryResponse(BaseModel):
    """Schema for session summary response"""
    id: str
    title: str
    status: str
    session_type: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[str] = None
    total_resumes: int
    total_jobs: int
    total_analyses: int
    overall_match_score: Optional[float] = None
    tags: List[str]

class SessionDetailsResponse(BaseModel):
    """Schema for detailed session response"""
    session: SessionSummaryResponse
    resumes: List[Dict[str, Any]]
    jobs: List[Dict[str, Any]]
    analyses: List[Dict[str, Any]]

class SessionStatsResponse(BaseModel):
    """Schema for session statistics response"""
    total_sessions: int
    active_sessions: int
    completed_sessions: int
    archived_sessions: int
    session_types: Dict[str, int]

class SessionListResponse(BaseModel):
    """Schema for session list response"""
    sessions: List[SessionSummaryResponse]
    total: int
    page: int
    limit: int

class AddToSessionRequest(BaseModel):
    """Schema for adding items to a session"""
    item_id: str = Field(..., description="ID of the item to add")
    item_type: str = Field(..., description="Type of item (resume, job, analysis)")

class SessionRestoreResponse(BaseModel):
    """Schema for session restoration response"""
    session_id: str
    title: str
    restored_items: Dict[str, List[str]]
    message: str