"""
Pydantic schemas for API request/response validation
"""
from .resume import ResumeCreate, ResumeResponse, ResumeComparison, OptimizedResumeResponse
from .job import JobCreateRequest, JobResponse, JobGroupCreateRequest, JobGroupResponse
from .analysis import AnalysisCreateRequest, AnalysisResponse, AnalysisResults
from .common import StatusResponse, ErrorResponse

__all__ = [
    "ResumeCreate",
    "ResumeResponse", 
    "ResumeComparison",
    "OptimizedResumeResponse",
    "JobCreateRequest",
    "JobResponse",
    "JobGroupCreateRequest", 
    "JobGroupResponse",
    "AnalysisCreateRequest",
    "AnalysisResponse",
    "AnalysisResults",
    "StatusResponse",
    "ErrorResponse"
]