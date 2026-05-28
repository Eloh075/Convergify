"""
Analysis management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import subprocess
import json as json_lib
import threading

from database import get_db
from services.analysis_service import AnalysisService
from services.celery_service import CeleryService
from services.export_service import ExportService
from schemas.analysis import AnalysisResponse, AnalysisCreateRequest, AnalysisResultsResponse
from models.analysis import Analysis
from models.resume import Resume
from models.job import Job

router = APIRouter(prefix="/api/analyses", tags=["analyses"])
analysis_service = AnalysisService()
celery_service = CeleryService()
export_service = ExportService()

# Store progress updates in memory (for real-time tracking)
progress_store: Dict[str, Dict[str, Any]] = {}

@router.post("/", response_model=AnalysisResponse)
async def create_analysis(
    analysis_data: AnalysisCreateRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Create and start a new analysis"""
    try:
        # Create analysis record
        analysis = analysis_service.create_analysis(analysis_data, db)
        
        # Get resume and jobs data
        resume = db.query(Resume).filter(Resume.id == analysis_data.resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        jobs = db.query(Job).filter(Job.id.in_(analysis_data.job_ids)).all()
        if not jobs:
            raise HTTPException(status_code=404, detail="No jobs found")
        
        # Prepare jobs data for subprocess
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                'job_id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'description': job.description,
                'required_skills': job.skills_list or [],
                'skills_processed': job.skills_processed or False
            })
        
        # Determine analysis mode
        analysis_mode = 'single_job' if len(jobs) == 1 else 'market_intelligence'
        
        # Initialize progress tracking
        progress_store[analysis.id] = {
            'stage': 'initialization',
            'status': 'Starting analysis...',
            'progress': 0,
            'jobs_processed': 0,
            'total_jobs': len(jobs)
        }
        
        # Run analysis as subprocess
        def run_analysis_subprocess():
            """Run analysis subprocess with progress tracking"""
            from database import SessionLocal
            db_session = SessionLocal()
            
            try:
                # Update analysis status to running
                db_analysis = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
                if db_analysis:
                    db_analysis.status = "running"
                    from datetime import datetime
                    db_analysis.started_at = datetime.utcnow()
                    db_session.commit()
                
                # Run subprocess - just pass IDs, let script query database
                # Use strategic analysis script for better results
                script_path = os.path.join(os.path.dirname(__file__), '..', 'run_analysis_strategic.py')
                
                import sys as sys_module
                python_executable = sys_module.executable
                
                # Just pass IDs as arguments
                job_ids_json = json_lib.dumps(analysis_data.job_ids)
                
                process = subprocess.Popen(
                    [
                        python_executable,
                        script_path,
                        analysis_data.resume_id,
                        job_ids_json,
                        analysis_mode
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                
                # Wait for completion (increased timeout to 20 minutes)
                stdout, stderr = process.communicate(timeout=1200)
                
                print(f"Analysis subprocess completed with return code: {process.returncode}")
                print(f"Stdout length: {len(stdout)}")
                print(f"Stderr length: {len(stderr)}")
                print(f"Stdout content (first 500 chars): {stdout[:500]}")
                if stderr:
                    print(f"Stderr content: {stderr[:500]}")
                
                # Parse result from stdout
                if process.returncode == 0:
                    try:
                        analysis_result = json_lib.loads(stdout)
                        
                        if analysis_result.get('success'):
                            # Update analysis with results
                            db_analysis = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
                            if db_analysis:
                                db_analysis.results_dict = analysis_result
                                db_analysis.mark_completed()
                                db_session.commit()
                                
                                # Update progress store
                                progress_store[analysis.id] = {
                                    'stage': 'completed',
                                    'status': 'Analysis complete!',
                                    'progress': 100,
                                    'jobs_processed': len(jobs),
                                    'total_jobs': len(jobs)
                                }
                        else:
                            # Mark as failed
                            error_msg = analysis_result.get('error', 'Unknown error')
                            db_analysis = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
                            if db_analysis:
                                db_analysis.mark_failed(error_msg)
                                db_session.commit()
                                
                            progress_store[analysis.id] = {
                                'stage': 'error',
                                'status': f'Analysis failed: {error_msg}',
                                'progress': 0
                            }
                    except json_lib.JSONDecodeError as e:
                        error_msg = f"Failed to parse analysis results: {str(e)}"
                        db_analysis = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
                        if db_analysis:
                            db_analysis.mark_failed(error_msg)
                            db_session.commit()
                        
                        progress_store[analysis.id] = {
                            'stage': 'error',
                            'status': error_msg,
                            'progress': 0
                        }
                else:
                    # Subprocess failed
                    error_msg = stderr or "Analysis subprocess failed"
                    db_analysis = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
                    if db_analysis:
                        db_analysis.mark_failed(error_msg)
                        db_session.commit()
                    
                    progress_store[analysis.id] = {
                        'stage': 'error',
                        'status': f'Analysis failed: {error_msg}',
                        'progress': 0
                    }
                        
            except subprocess.TimeoutExpired:
                error_msg = "Analysis timed out after 20 minutes"
                db_analysis = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
                if db_analysis:
                    db_analysis.mark_failed(error_msg)
                    db_session.commit()
                
                progress_store[analysis.id] = {
                    'stage': 'error',
                    'status': error_msg,
                    'progress': 0
                }
            except Exception as e:
                error_msg = str(e)
                db_analysis = db_session.query(Analysis).filter(Analysis.id == analysis.id).first()
                if db_analysis:
                    db_analysis.mark_failed(error_msg)
                    db_session.commit()
                
                progress_store[analysis.id] = {
                    'stage': 'error',
                    'status': f'Analysis failed: {error_msg}',
                    'progress': 0
                }
            finally:
                db_session.close()
        
        # Run in background using threading (not BackgroundTasks which might be killed)
        import threading
        thread = threading.Thread(target=run_analysis_subprocess, daemon=False)  # Not daemon so it completes
        thread.start()
        
        return {
            **analysis.dict(),
            "message": "Analysis started in background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[AnalysisResponse])
async def list_analyses(
    resume_id: Optional[str] = Query(None, description="Filter by resume ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    analysis_type: Optional[str] = Query(None, description="Filter by analysis type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db)
):
    """List analyses with filtering and sorting"""
    try:
        analyses = analysis_service.list_analyses(
            resume_id=resume_id,
            status=status,
            analysis_type=analysis_type,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            db=db
        )
        return analyses
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Get a specific analysis by ID"""
    try:
        analysis = analysis_service.get_analysis(analysis_id, db)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{analysis_id}/results", response_model=AnalysisResultsResponse)
async def get_analysis_results(analysis_id: str, db: Session = Depends(get_db)):
    """Get detailed results of an analysis"""
    try:
        results = analysis_service.get_analysis_results(analysis_id, db)
        if not results:
            raise HTTPException(status_code=404, detail="Analysis not found or not completed")
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{analysis_id}/status")
async def get_analysis_status(analysis_id: str, db: Session = Depends(get_db)):
    """Get current status of an analysis including real-time progress"""
    try:
        # Get base status from database
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        status = {
            "analysis_id": analysis.id,
            "status": analysis.status,
            "analysis_type": analysis.analysis_type,
            "task_id": analysis.task_id,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
            "started_at": analysis.started_at.isoformat() if analysis.started_at else None,
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
            "error_message": analysis.error_message,
            "has_results": analysis.results_dict is not None
        }
        
        # Add real-time progress if available
        if analysis_id in progress_store:
            progress_data = progress_store[analysis_id]
            status.update({
                "stage": progress_data.get('stage'),
                "current_status": progress_data.get('status'),
                "progress_percentage": progress_data.get('progress', 0),
                "jobs_processed": progress_data.get('jobs_processed'),
                "total_jobs": progress_data.get('total_jobs')
            })
        else:
            # Calculate progress based on status
            progress_map = {
                'pending': 0,
                'running': 50,
                'completed': 100,
                'failed': 0,
                'cancelled': 0
            }
            status["progress_percentage"] = progress_map.get(analysis.status, 0)
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{analysis_id}/cancel")
async def cancel_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Cancel a running analysis"""
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if analysis.status in ["completed", "failed", "cancelled"]:
            raise HTTPException(status_code=400, detail="Analysis cannot be cancelled")
        
        # Cancel the task if it exists
        if analysis.task_id:
            celery_service.cancel_task(analysis.task_id, db)
        
        # Update analysis status
        analysis_service.update_analysis_status(analysis_id, "cancelled", db)
        
        # Clear progress
        if analysis_id in progress_store:
            del progress_store[analysis_id]
        
        return {"message": "Analysis cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Delete an analysis and its results"""
    try:
        success = analysis_service.delete_analysis(analysis_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Clear progress
        if analysis_id in progress_store:
            del progress_store[analysis_id]
        
        return {"message": "Analysis deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{analysis_id}/retry")
async def retry_analysis(
    analysis_id: str,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Retry a failed analysis"""
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if analysis.status not in ["failed", "cancelled"]:
            raise HTTPException(status_code=400, detail="Only failed or cancelled analyses can be retried")
        
        # Reset analysis status
        analysis.status = "pending"
        analysis.error_message = None
        analysis.results = None
        db.commit()
        
        # Re-create the analysis using the same data
        analysis_data = AnalysisCreateRequest(
            resume_id=analysis.resume_id,
            job_ids=analysis.job_ids_list,
            analysis_type=analysis.analysis_type
        )
        
        # Delete old analysis and create new one
        db.delete(analysis)
        db.commit()
        
        return await create_analysis(analysis_data, background_tasks, db)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{analysis_id}/export")
async def export_analysis(
    analysis_id: str,
    format: str = Query("json", regex="^(json|pdf)$"),
    include_raw_data: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Export analysis results"""
    try:
        export_data = analysis_service.export_analysis(analysis_id, format, include_raw_data, db)
        if not export_data:
            raise HTTPException(status_code=404, detail="Analysis not found or not completed")
        return export_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{analysis_id}/recommendations")
async def get_analysis_recommendations(analysis_id: str, db: Session = Depends(get_db)):
    """Get actionable recommendations from analysis"""
    try:
        recommendations = analysis_service.get_analysis_recommendations(analysis_id, db)
        if not recommendations:
            raise HTTPException(status_code=404, detail="Analysis not found or not completed")
        return recommendations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{analysis_id}/skill-gaps")
async def get_skill_gaps(analysis_id: str, db: Session = Depends(get_db)):
    """Get skill gap analysis"""
    try:
        skill_gaps = analysis_service.get_skill_gaps(analysis_id, db)
        if not skill_gaps:
            raise HTTPException(status_code=404, detail="Analysis not found or not completed")
        return skill_gaps
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{analysis_id}/compare/{compare_with_id}")
async def compare_analyses(
    analysis_id: str,
    compare_with_id: str,
    db: Session = Depends(get_db)
):
    """Compare two analyses"""
    try:
        comparison = analysis_service.compare_analyses(analysis_id, compare_with_id, db)
        if not comparison:
            raise HTTPException(status_code=404, detail="One or both analyses not found")
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
