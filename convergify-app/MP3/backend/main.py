"""
Career Analysis Platform - Main FastAPI Application
"""
import sys
import asyncio

# Fix for Windows + Playwright + FastAPI compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
import os
from pathlib import Path

from config import settings
from database import init_db, get_db
from api.resume import router as resume_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    os.makedirs(settings.upload_dir, exist_ok=True)
    init_db()
    yield
    # Shutdown (if needed)

app = FastAPI(
    title="Career Analysis Platform",
    description="Integrated career analysis system with resume optimization and job matching",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],  # Vite and React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(resume_router)

# Import and include other routers
from api.job import router as job_router
from api.analysis import router as analysis_router
from api.session import router as session_router

app.include_router(job_router)
app.include_router(analysis_router)
app.include_router(session_router)

@app.get("/")
async def root():
    return {
        "message": "Career Analysis Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/tasks/{task_id}/status")
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """Get status of a background task"""
    try:
        from services.celery_service import CeleryService
        celery_service = CeleryService()
        
        task_status = celery_service.get_task_status(task_id, db)
        return task_status
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/tasks/queue/stats")
async def get_queue_stats():
    """Get queue statistics"""
    try:
        from services.celery_service import CeleryService
        celery_service = CeleryService()
        
        queue_stats = celery_service.get_queue_stats()
        worker_stats = celery_service.get_worker_stats()
        
        return {
            "queues": queue_stats.get("queues", {}),
            "workers": worker_stats.get("workers", {}),
            "total_workers": worker_stats.get("total_workers", 0),
            "total_active_tasks": worker_stats.get("total_active_tasks", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str, db: Session = Depends(get_db)):
    """Cancel a running task"""
    try:
        from services.celery_service import CeleryService
        celery_service = CeleryService()
        
        result = celery_service.cancel_task(task_id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "upload_dir": os.path.exists(settings.upload_dir)
    }

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Import string format for reload
        host=settings.api_host, 
        port=settings.api_port, 
        reload=settings.debug
    )

# Serve React frontend in production (optional) - RE-ENABLED AFTER API FIX
frontend_path = Path("../Frontend/dist")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve React frontend for all non-API routes"""
        # Check if this is an API request that wasn't handled
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        file_path = frontend_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        
        # Return index.html for client-side routing
        return FileResponse(frontend_path / "index.html")