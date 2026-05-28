"""
Common Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class StatusResponse(BaseModel):
    """Generic status response"""
    success: bool
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime
    updated_at: Optional[datetime] = None

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    size: int = 20
    
    class Config:
        validate_assignment = True

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: list
    total: int
    page: int
    size: int
    pages: int