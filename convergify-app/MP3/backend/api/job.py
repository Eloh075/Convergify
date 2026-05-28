"""
Job management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import sys
import json
import asyncio
from datetime import datetime

from database import get_db
from services.job_service import JobService
from services.celery_service import CeleryService
from services.export_service import ExportService
from schemas.job import JobResponse, JobCreateRequest, JobGroupResponse, JobGroupCreateRequest, ScrapingRequest
from models.job import Job, JobGroup

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
job_service = JobService()
celery_service = CeleryService()
export_service = ExportService()

@router.post("/", response_model=JobResponse)
async def create_job(
    job_data: JobCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new job manually"""
    try:
        job = job_service.create_job(job_data, db)
        return job
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    company: Optional[str] = Query(None, description="Filter by company"),
    location: Optional[str] = Query(None, description="Filter by location"),
    source: Optional[str] = Query(None, description="Filter by source"),
    group_id: Optional[str] = Query(None, description="Filter by job group"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    sort_by: str = Query("created_date", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db)
):
    """List jobs with filtering, sorting, and pagination"""
    try:
        jobs = job_service.list_jobs(
            company=company,
            location=location,
            source=source,
            group_id=group_id,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            db=db
        )
        return jobs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Job Groups endpoints - MOVED BEFORE {job_id} route
@router.post("/groups", response_model=JobGroupResponse)
async def create_job_group(
    group_data: JobGroupCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new job group"""
    try:
        group = job_service.create_job_group(group_data, db)
        return group
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/groups", response_model=List[JobGroupResponse])
async def list_job_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all job groups"""
    try:
        groups = job_service.list_job_groups(skip, limit, db)
        return groups
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/groups/{group_id}", response_model=JobGroupResponse)
async def get_job_group(group_id: str, db: Session = Depends(get_db)):
    """Get a specific job group"""
    try:
        group = job_service.get_job_group(group_id, db)
        if not group:
            raise HTTPException(status_code=404, detail="Job group not found")
        return group
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/groups/{group_id}", response_model=JobGroupResponse)
async def update_job_group(
    group_id: str,
    group_data: JobGroupCreateRequest,
    db: Session = Depends(get_db)
):
    """Update a job group"""
    try:
        group = job_service.update_job_group(group_id, group_data, db)
        if not group:
            raise HTTPException(status_code=404, detail="Job group not found")
        return group
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/groups/{group_id}")
async def delete_job_group(group_id: str, db: Session = Depends(get_db)):
    """Delete a job group"""
    try:
        success = job_service.delete_job_group(group_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Job group not found")
        return {"message": "Job group deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/groups/{group_id}/jobs")
async def add_jobs_to_group(
    group_id: str,
    job_ids: List[str],
    db: Session = Depends(get_db)
):
    """Add jobs to a group"""
    try:
        success = job_service.add_jobs_to_group(group_id, job_ids, db)
        if not success:
            raise HTTPException(status_code=404, detail="Job group not found")
        return {"message": f"Added {len(job_ids)} jobs to group"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/groups/{group_id}/jobs")
async def remove_jobs_from_group(
    group_id: str,
    job_ids: List[str],
    db: Session = Depends(get_db)
):
    """Remove jobs from a group"""
    try:
        success = job_service.remove_jobs_from_group(group_id, job_ids, db)
        if not success:
            raise HTTPException(status_code=404, detail="Job group not found")
        return {"message": f"Removed {len(job_ids)} jobs from group"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/groups/{group_id}/jobs", response_model=List[JobResponse])
async def get_jobs_in_group(
    group_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all jobs in a specific group"""
    try:
        jobs = job_service.get_jobs_in_group(group_id, skip, limit, db)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Other specific routes - MOVED BEFORE {job_id} route
@router.get("/search/")
async def search_jobs(
    q: str = Query(..., min_length=1, description="Search query"),
    search_in: str = Query("all", regex="^(title|company|description|all)$", description="Search scope"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Search jobs by title, company, or description"""
    try:
        jobs = job_service.search_jobs(q, search_in, skip, limit, db)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats/")
async def get_job_stats(db: Session = Depends(get_db)):
    """Get job statistics"""
    try:
        stats = job_service.get_job_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/export/")
async def export_jobs(
    format: str = Query("json", regex="^(json|csv)$"),
    group_id: Optional[str] = Query(None, description="Export specific group"),
    include_skills: bool = Query(True, description="Include extracted skills"),
    db: Session = Depends(get_db)
):
    """Export jobs data"""
    try:
        export_data = export_service.export_jobs_data(format, group_id, include_skills, db)
        return export_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/export/download")
async def download_jobs_export(
    format: str = Query("json", regex="^(json|csv)$"),
    group_id: Optional[str] = Query(None, description="Export specific group"),
    include_skills: bool = Query(True, description="Include extracted skills"),
    db: Session = Depends(get_db)
):
    """Download exported jobs data as file"""
    try:
        export_data = export_service.export_jobs_data(format, group_id, include_skills, db)
        file_path = export_data["file_path"]
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Export file not found")
        
        return FileResponse(
            path=file_path,
            filename=export_data["filename"],
            media_type='application/octet-stream'
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Generic {job_id} routes - MOVED TO END
@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    try:
        job = job_service.get_job(job_id, db)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    job_data: JobCreateRequest,
    db: Session = Depends(get_db)
):
    """Update a job"""
    try:
        job = job_service.update_job(job_id, job_data, db)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{job_id}")
async def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Delete a job"""
    try:
        success = job_service.delete_job(job_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"message": "Job deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk", response_model=List[JobResponse])
async def create_jobs_bulk(
    jobs_data: List[JobCreateRequest],
    db: Session = Depends(get_db)
):
    """Create multiple jobs at once"""
    try:
        jobs = job_service.create_jobs_bulk(jobs_data, db)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/bulk")
async def delete_jobs_bulk(
    job_ids: List[str],
    db: Session = Depends(get_db)
):
    """Delete multiple jobs at once"""
    try:
        deleted_count = job_service.delete_jobs_bulk(job_ids, db)
        return {
            "message": f"Successfully deleted {deleted_count} jobs",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/scrape")
async def start_job_scraping(
    request: ScrapingRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Start job scraping process with real-time progress"""
    try:
        print(f"📥 Received scraping request: {request}")
        print(f"   search_terms: {request.search_terms}")
        print(f"   employment_type: {request.employment_type}")
        print(f"   max_jobs: {request.max_jobs}")
        
        scraping_config = {
            "search_terms": request.search_terms,
            "employment_type": request.employment_type or "full-time",
            "max_jobs": request.max_jobs or 10
        }
        
        print(f"📋 Scraping config: {scraping_config}")
        
        # Start scraping in background and return immediately
        task_id = f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        def run_scraping_sync():
            """Run scraping in a separate process"""
            import subprocess
            import json
            from datetime import datetime
            
            try:
                print(f"🚀 Starting scraper subprocess...")
                
                search_term = scraping_config['search_terms'][0]
                employment_type = scraping_config['employment_type']
                max_jobs = scraping_config['max_jobs']
                
                # Run the scraper as a subprocess
                script_path = os.path.join(os.path.dirname(__file__), '..', 'run_scraper.py')
                proc_result = subprocess.run(
                    [sys.executable, script_path, search_term, employment_type, str(max_jobs)],
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout (increased from 5)
                )
                
                if proc_result.returncode != 0:
                    print(f"❌ Scraper subprocess failed: {proc_result.stderr}")
                    return
                
                # Parse the JSON result
                scraper_result = json.loads(proc_result.stdout)
                print(f"📊 Scraping result: success={scraper_result.get('success')}, jobs={len(scraper_result.get('jobs', []))}")
                
                # Save results to database if successful
                if scraper_result.get('success') and scraper_result.get('jobs'):
                    jobs_data = scraper_result['jobs']
                    saved_jobs = []
                    
                    print(f"💾 Saving {len(jobs_data)} jobs to database...")
                    
                    # Get a new database session for this thread
                    from database import SessionLocal
                    db_session = SessionLocal()
                    
                    try:
                        for job_data in jobs_data:
                            job = Job(
                                title=job_data.get('title', ''),
                                company=job_data.get('company', ''),
                                description=job_data.get('description', ''),
                                location=job_data.get('location', ''),
                                employment_type=job_data.get('employment_type', 'full-time'),
                                salary_min=job_data.get('salary_min'),
                                salary_max=job_data.get('salary_max'),
                                source='mycareersfuture',
                                scraped_date=datetime.now()
                            )
                            
                            # Use property setters for list fields
                            job.requirements_list = job_data.get('requirements', [])
                            job.skills_list = job_data.get('required_skills', [])
                            
                            db_session.add(job)
                            saved_jobs.append(job)
                            print(f"  ✅ Added job: {job.title} at {job.company}")
                        
                        db_session.commit()
                        print(f"💾 Committed {len(saved_jobs)} jobs to database")
                        
                        # Refresh jobs to get their IDs
                        for job in saved_jobs:
                            db_session.refresh(job)
                        
                        # Create a new batch group for this scrape session
                        batch_timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                        search_terms_str = ", ".join(scraping_config['search_terms'])
                        
                        batch_group = JobGroup(
                            name=f"Scraped: {search_terms_str} - {batch_timestamp}",
                            description=f"Batch of {len(saved_jobs)} jobs scraped on {batch_timestamp}",
                            group_type="scraped",
                            job_ids_list=[job.id for job in saved_jobs]
                        )
                        db_session.add(batch_group)
                        db_session.commit()
                        db_session.refresh(batch_group)
                        print(f"📁 Created batch group: {batch_group.name}")
                        
                        # Update jobs to reference the batch group
                        for job in saved_jobs:
                            job.group_id = batch_group.id
                        
                        db_session.commit()
                        
                        print(f"✅ Saved {len(saved_jobs)} jobs to database and added to batch group")
                    finally:
                        db_session.close()
                else:
                    print(f"❌ Scraping failed or returned no jobs")
                    
            except subprocess.TimeoutExpired:
                print(f"❌ Scraper subprocess timed out after 10 minutes")
                print(f"   This might indicate the scraper is stuck or the site is very slow")
                print(f"   Check if the browser window is still open and what page it's on")
            except Exception as e:
                print(f"❌ Background scraping failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Run scraping in a separate thread
        import threading
        thread = threading.Thread(target=run_scraping_sync, daemon=True)
        thread.start()
        
        return {
            "task_id": task_id,
            "status": "started",
            "message": "Job scraping started",
            "config": scraping_config
        }
        
    except Exception as e:
        print(f"❌ Scraping endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/scrape/stream/{task_id}")
async def stream_scraping_progress(task_id: str):
    """Stream scraping progress using Server-Sent Events"""
    
    async def generate_progress():
        """Generate progress updates"""
        # Simulate progress updates (in real implementation, this would read from scraper logs)
        progress_steps = [
            {"progress": 10, "message": "🚀 Initializing job scraper..."},
            {"progress": 20, "message": "🔍 Searching MyCareersFuture..."},
            {"progress": 40, "message": "📋 Found job listings, extracting data..."},
            {"progress": 60, "message": "📊 Processing job details..."},
            {"progress": 80, "message": "💾 Saving jobs to database..."},
            {"progress": 100, "message": "✅ Scraping completed successfully!"}
        ]
        
        for step in progress_steps:
            yield f"data: {json.dumps(step)}\n\n"
            await asyncio.sleep(2)  # Simulate processing time
    
    return StreamingResponse(
        generate_progress(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@router.get("/scraped/pending")
async def get_pending_scraped_jobs(
    task_id: Optional[str] = Query(None, description="Filter by scraping task ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get jobs that are pending review after scraping"""
    try:
        query = db.query(Job).filter(Job.status == "pending_review")
        
        if task_id:
            # Filter by task_id if provided (would need to add task_id to Job model)
            pass
        
        jobs = query.offset(skip).limit(limit).all()
        total = query.count()
        
        return {
            "jobs": [JobResponse.from_orm(job) for job in jobs],
            "total": total,
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/scraped/confirm")
async def confirm_scraped_jobs(
    job_ids: List[str],
    db: Session = Depends(get_db)
):
    """Confirm scraped jobs - changes status from pending_review to active"""
    try:
        # Update job statuses
        updated_count = db.query(Job).filter(
            Job.id.in_(job_ids),
            Job.status == "pending_review"
        ).update(
            {"status": "active"},
            synchronize_session=False
        )
        
        db.commit()
        
        return {
            "message": f"Confirmed {updated_count} jobs",
            "confirmed_count": updated_count,
            "job_ids": job_ids
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/scraped/reject")
async def reject_scraped_jobs(
    job_ids: List[str],
    db: Session = Depends(get_db)
):
    """Reject scraped jobs - deletes them from database"""
    try:
        # Delete rejected jobs
        deleted_count = db.query(Job).filter(
            Job.id.in_(job_ids),
            Job.status == "pending_review"
        ).delete(synchronize_session=False)
        
        db.commit()
        
        return {
            "message": f"Rejected and deleted {deleted_count} jobs",
            "deleted_count": deleted_count,
            "job_ids": job_ids
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/scraping/status/{task_id}")
async def get_scraping_status(task_id: str, db: Session = Depends(get_db)):
    """Get status of a scraping task"""
    try:
        status = celery_service.get_task_status(task_id, db)
        return status
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/scraping/{task_id}/cancel")
async def cancel_scraping(task_id: str, db: Session = Depends(get_db)):
    """Cancel a running scraping task"""
    try:
        result = celery_service.cancel_task(task_id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{job_id}/extract-skills")
async def extract_job_skills(
    job_id: str,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Extract skills from a job description"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Submit skill extraction task
        task_result = celery_service.submit_task(
            "extract_skills_from_job",
            args=[job_id, job.description, job.title, job.company],
            db=db
        )
        
        return {
            "task_id": task_result["task_id"],
            "status": "started",
            "message": "Skill extraction started in background"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk/extract-skills")
async def extract_skills_bulk(
    job_ids: List[str],
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Extract skills from multiple job descriptions"""
    try:
        # Submit enrichment task
        task_result = celery_service.submit_task(
            "enrich_job_data",
            args=[job_ids],
            db=db
        )
        
        return {
            "task_id": task_result["task_id"],
            "status": "started",
            "message": f"Skill extraction started for {len(job_ids)} jobs"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Remaining routes that weren't moved
@router.post("/validate")
async def validate_jobs(
    job_ids: List[str],
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Validate job data quality"""
    try:
        # Submit validation task
        task_result = celery_service.submit_task(
            "validate_scraped_jobs",
            args=[job_ids],
            db=db
        )
        
        return {
            "task_id": task_result["task_id"],
            "status": "started",
            "message": f"Validation started for {len(job_ids)} jobs"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))