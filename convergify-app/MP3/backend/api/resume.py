"""
Resume management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

from database import get_db
from services.resume_service import ResumeService
from services.celery_service import CeleryService
from services.export_service import ExportService
from schemas.resume import ResumeResponse, ResumeListResponse, ResumeUploadResponse, ResumeComparisonResponse
from schemas.analysis import AnalysisResponse
from models.resume import Resume, OptimizedResume
from models.analysis import Analysis

router = APIRouter(prefix="/api/resumes", tags=["resumes"])
resume_service = ResumeService()
celery_service = CeleryService()
export_service = ExportService()

# For now, we'll use a default user ID
# In a real app, this would come from authentication
DEFAULT_USER_ID = "default-user"

@router.post("/upload", response_model=dict)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Form(DEFAULT_USER_ID),
    db: Session = Depends(get_db)
):
    """Upload and process a resume file"""
    try:
        result = await resume_service.upload_resume(file, user_id, db)
        return {
            "success": True,
            "message": "Resume uploaded successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    user_id: Optional[str] = Query(DEFAULT_USER_ID, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by analysis status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    sort_by: str = Query("upload_date", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db)
):
    """List resumes with filtering, sorting, and pagination"""
    try:
        resumes = resume_service.list_resumes(
            user_id=user_id,
            status=status,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            db=db
        )
        return resumes
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: str, db: Session = Depends(get_db)):
    """Get a specific resume by ID with full details"""
    try:
        resume = resume_service.get_resume(resume_id, DEFAULT_USER_ID, db)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{resume_id}/metadata")
async def get_resume_metadata(resume_id: str, db: Session = Depends(get_db)):
    """Get resume metadata and processing status"""
    try:
        metadata = resume_service.get_resume_metadata(resume_id, db)
        if not metadata:
            raise HTTPException(status_code=404, detail="Resume not found")
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{resume_id}/history")
async def get_resume_history(
    resume_id: str,
    include_analyses: bool = Query(True, description="Include analysis history"),
    include_optimizations: bool = Query(True, description="Include optimization history"),
    db: Session = Depends(get_db)
):
    """Get complete history of resume analyses and optimizations"""
    try:
        history = resume_service.get_resume_history(
            resume_id, include_analyses, include_optimizations, db
        )
        if not history:
            raise HTTPException(status_code=404, detail="Resume not found")
        return history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{resume_id}/analyze")
async def analyze_resume(
    resume_id: str,
    job_ids: Optional[List[str]] = None,
    analysis_type: str = "comprehensive",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Start resume analysis against jobs or market"""
    try:
        # Validate resume exists
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Create analysis record
        analysis = Analysis(
            resume_id=resume_id,
            job_ids_list=job_ids or [],
            analysis_type=analysis_type,
            status="pending"
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Submit background task
        if job_ids:
            task_result = celery_service.submit_task(
                "comprehensive_analysis",
                args=[resume_id, job_ids, analysis_type],
                db=db
            )
        else:
            # Market analysis - extract skills first
            task_result = celery_service.submit_task(
                "extract_skills_from_resume",
                args=[resume_id, resume.original_text],
                db=db
            )
        
        # Update analysis with task ID
        analysis.task_id = task_result["task_id"]
        db.commit()
        
        return {
            "analysis_id": analysis.id,
            "task_id": task_result["task_id"],
            "status": "started",
            "message": "Analysis started in background"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{resume_id}/analyses")
async def get_resume_analyses(
    resume_id: str,
    status: Optional[str] = Query(None, description="Filter by analysis status"),
    analysis_type: Optional[str] = Query(None, description="Filter by analysis type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all analyses for a resume"""
    try:
        analyses = resume_service.get_resume_analyses(
            resume_id, status, analysis_type, skip, limit, db
        )
        return analyses
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{resume_id}/optimize")
async def optimize_resume(
    resume_id: str,
    analysis_id: Optional[str] = None,
    target_job_ids: Optional[List[str]] = None,
    optimization_type: str = "comprehensive",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Start resume optimization based on analysis results"""
    try:
        # Validate resume exists
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Get analysis results if analysis_id provided
        analysis_results = {}
        if analysis_id:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis and analysis.results_dict:
                analysis_results = analysis.results_dict
        
        # Submit optimization task
        task_result = celery_service.submit_task(
            "generate_optimized_resume",
            args=[resume_id, analysis_results],
            db=db
        )
        
        return {
            "task_id": task_result["task_id"],
            "status": "started",
            "message": "Resume optimization started in background"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{resume_id}/optimized")
async def get_optimized_resumes(
    resume_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get all optimized versions of a resume"""
    try:
        optimized_resumes = resume_service.get_optimized_resumes(resume_id, skip, limit, db)
        return optimized_resumes
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{resume_id}/compare/{optimized_id}")
async def compare_resumes(
    resume_id: str,
    optimized_id: str,
    db: Session = Depends(get_db)
):
    """Compare original resume with optimized version"""
    try:
        comparison = resume_service.compare_resumes(resume_id, optimized_id, db)
        if not comparison:
            raise HTTPException(status_code=404, detail="Resume or optimized version not found")
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{resume_id}")
async def delete_resume(resume_id: str, db: Session = Depends(get_db)):
    """Delete a resume and all associated data"""
    try:
        success = resume_service.delete_resume(resume_id, DEFAULT_USER_ID, db)
        if not success:
            raise HTTPException(status_code=404, detail="Resume not found")
        return {"message": "Resume deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{resume_id}/optimized/{optimized_id}")
async def delete_optimized_resume(
    resume_id: str,
    optimized_id: str,
    db: Session = Depends(get_db)
):
    """Delete a specific optimized resume version"""
    try:
        success = resume_service.delete_optimized_resume(resume_id, optimized_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Optimized resume not found")
        return {"message": "Optimized resume deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{resume_id}/download")
async def download_resume(resume_id: str, db: Session = Depends(get_db)):
    """Download original resume file"""
    try:
        file_path = resume_service.get_resume_file_path(resume_id, db)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        return FileResponse(
            path=file_path,
            filename=Path(file_path).name,
            media_type='application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{resume_id}/optimized/{optimized_id}/download")
async def download_optimized_resume(
    resume_id: str,
    optimized_id: str,
    format: str = Query("pdf", regex="^(pdf|txt|markdown)$"),
    db: Session = Depends(get_db)
):
    """Download optimized resume in specified format"""
    try:
        file_path = resume_service.export_optimized_resume(
            resume_id, optimized_id, format, db
        )
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Optimized resume file not found")
        
        return FileResponse(
            path=file_path,
            filename=Path(file_path).name,
            media_type='application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{resume_id}/duplicate")
async def duplicate_resume(
    resume_id: str,
    new_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a duplicate of an existing resume"""
    try:
        duplicate = resume_service.duplicate_resume(resume_id, new_name, db)
        if not duplicate:
            raise HTTPException(status_code=404, detail="Resume not found")
        return duplicate
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{resume_id}/export")
async def export_resume_data(
    resume_id: str,
    format: str = Query("json", regex="^(json|csv)$"),
    include_analyses: bool = Query(True),
    include_optimizations: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Export complete resume data including analyses and optimizations"""
    try:
        export_data = export_service.export_resume_data(
            resume_id, format, include_analyses, include_optimizations, db
        )
        if not export_data:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return export_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{resume_id}/export/download")
async def download_resume_export(
    resume_id: str,
    format: str = Query("json", regex="^(json|csv)$"),
    include_analyses: bool = Query(True),
    include_optimizations: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Download exported resume data as file"""
    try:
        export_data = export_service.export_resume_data(
            resume_id, format, include_analyses, include_optimizations, db
        )
        if not export_data:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        file_path = export_data["file_path"]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Export file not found")
        
        return FileResponse(
            path=file_path,
            filename=export_data["filename"],
            media_type='application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Legacy endpoints for backward compatibility
@router.get("/{resume_id}/comparison")
def get_resume_comparison(
    resume_id: str,
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Get comparison between original and optimized resume (legacy endpoint)"""
    comparison = resume_service.get_resume_comparison(resume_id, user_id, db)
    if not comparison:
        raise HTTPException(status_code=404, detail="Resume not found")
    return comparison

@router.get("/{resume_id}/text")
def get_resume_text(
    resume_id: str,
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Get the original text content of a resume (legacy endpoint)"""
    text = resume_service.get_resume_text(resume_id, user_id, db)
    if text is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {"text": text}

@router.get("/search/", response_model=List[ResumeResponse])
def search_resumes(
    q: str = Query(..., min_length=1),
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Search resumes by filename or content"""
    resumes = resume_service.search_resumes(user_id, q, db)
    return resumes

@router.get("/stats/", response_model=dict)
def get_resume_stats(
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Get resume statistics for a user"""
    stats = resume_service.get_resume_stats(user_id, db)
    return {
        "success": True,
        "data": stats
    }

@router.put("/{resume_id}/status")
def update_resume_status(
    resume_id: str,
    status: str,
    user_id: str = DEFAULT_USER_ID,
    db: Session = Depends(get_db)
):
    """Update resume analysis status"""
    success = resume_service.update_resume_status(resume_id, status, db)
    if not success:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {
        "success": True,
        "message": f"Resume status updated to {status}"
    }