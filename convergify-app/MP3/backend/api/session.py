"""
Session management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from services.session_service import SessionService
from schemas.session import (
    SessionCreateRequest,
    SessionUpdateRequest,
    SessionResponse,
    SessionSummaryResponse,
    SessionDetailsResponse,
    SessionStatsResponse,
    SessionListResponse,
    AddToSessionRequest,
    SessionRestoreResponse
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])
session_service = SessionService()

# Default user ID for now
DEFAULT_USER_ID = "default-user"

@router.post("/", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreateRequest,
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Create a new analysis session"""
    try:
        session = session_service.create_session(
            user_id=user_id,
            title=session_data.title,
            session_type=session_data.session_type,
            description=session_data.description,
            configuration=session_data.configuration,
            db=db
        )
        
        # Add tags if provided
        if session_data.tags:
            session.tags_list = session_data.tags
            db.commit()
        
        return SessionResponse.from_session(session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    user_id: str = DEFAULT_USER_ID,
    status: Optional[str] = Query(None, description="Filter by status"),
    session_type: Optional[str] = Query(None, description="Filter by session type"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    sort_by: str = Query("updated_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db)
):
    """List sessions with filtering and sorting"""
    try:
        # Parse tags if provided
        tags_list = None
        if tags:
            tags_list = [tag.strip() for tag in tags.split(",")]
        
        sessions = session_service.list_sessions(
            user_id=user_id,
            status=status,
            session_type=session_type,
            tags=tags_list,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            db=db
        )
        
        # Convert to summary responses
        session_summaries = []
        for session in sessions:
            summary = session.get_summary()
            session_summaries.append(SessionSummaryResponse(**summary))
        
        # Get total count for pagination
        total_count = len(sessions)  # Simplified for now
        
        return SessionListResponse(
            sessions=session_summaries,
            total=total_count,
            page=skip // limit + 1,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{session_id}", response_model=SessionDetailsResponse)
async def get_session(
    session_id: str,
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Get detailed session information"""
    try:
        session_details = session_service.get_session_details(session_id, user_id, db)
        if not session_details:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionDetailsResponse(**session_details)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    session_data: SessionUpdateRequest,
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Update a session"""
    try:
        # Convert to dict, excluding None values
        updates = session_data.dict(exclude_unset=True)
        
        session = session_service.update_session(session_id, user_id, updates, db)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse.from_session(session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Delete a session"""
    try:
        success = session_service.delete_session(session_id, user_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{session_id}/items")
async def add_item_to_session(
    session_id: str,
    item_data: AddToSessionRequest,
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Add an item (resume, job, or analysis) to a session"""
    try:
        success = False
        
        if item_data.item_type == "resume":
            success = session_service.add_resume_to_session(
                session_id, item_data.item_id, user_id, db
            )
        elif item_data.item_type == "job":
            success = session_service.add_job_to_session(
                session_id, item_data.item_id, user_id, db
            )
        elif item_data.item_type == "analysis":
            success = session_service.add_analysis_to_session(
                session_id, item_data.item_id, user_id, db
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid item type")
        
        if not success:
            raise HTTPException(status_code=404, detail="Session or item not found")
        
        return {"message": f"{item_data.item_type.capitalize()} added to session successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{session_id}/items/{item_type}/{item_id}")
async def remove_item_from_session(
    session_id: str,
    item_type: str,
    item_id: str,
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Remove an item from a session"""
    try:
        success = False
        
        if item_type == "resume":
            success = session_service.remove_resume_from_session(
                session_id, item_id, user_id, db
            )
        elif item_type == "job":
            success = session_service.remove_job_from_session(
                session_id, item_id, user_id, db
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid item type")
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": f"{item_type.capitalize()} removed from session successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{session_id}/complete")
async def complete_session(
    session_id: str,
    overall_score: Optional[float] = Query(None, description="Overall match score"),
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Mark a session as completed"""
    try:
        success = session_service.complete_session(session_id, user_id, overall_score, db)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session marked as completed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{session_id}/archive")
async def archive_session(
    session_id: str,
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Archive a session"""
    try:
        success = session_service.archive_session(session_id, user_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session archived successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{session_id}/restore")
async def restore_session(
    session_id: str,
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Restore an archived session"""
    try:
        success = session_service.restore_session(session_id, user_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get session details for response
        session_details = session_service.get_session_details(session_id, user_id, db)
        
        restored_items = {
            "resumes": [r["id"] for r in session_details["resumes"]],
            "jobs": [j["id"] for j in session_details["jobs"]],
            "analyses": [a["id"] for a in session_details["analyses"]]
        }
        
        return SessionRestoreResponse(
            session_id=session_id,
            title=session_details["session"]["title"],
            restored_items=restored_items,
            message="Session restored successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats/user")
async def get_session_stats(
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Get session statistics for a user"""
    try:
        stats = session_service.get_session_statistics(user_id, db)
        return SessionStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auto-create/{analysis_id}")
async def auto_create_session(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Automatically create a session from an analysis"""
    try:
        session = session_service.auto_create_session_from_analysis(analysis_id, db)
        if not session:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "session_id": session.id,
            "title": session.title,
            "message": "Session created automatically from analysis"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))