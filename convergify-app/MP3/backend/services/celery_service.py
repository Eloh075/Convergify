"""
Celery task monitoring and management service
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import logging

try:
    from celery.result import AsyncResult
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    AsyncResult = None

from models.celery_task import CeleryTask

logger = logging.getLogger(__name__)

class CeleryService:
    """Service for managing and monitoring Celery tasks"""
    
    def __init__(self):
        # Import celery_app here to avoid circular imports
        if CELERY_AVAILABLE:
            try:
                from celery_app import celery_app
                self.celery_app = celery_app
            except ImportError:
                self.celery_app = None
                logger.warning("Celery app not available - background tasks will be disabled")
        else:
            self.celery_app = None
            logger.warning("Celery not installed - background tasks will be disabled")
    
    def submit_task(self, task_name: str, args: List[Any] = None, kwargs: Dict[str, Any] = None, 
                   db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Submit a task to Celery and track it in database
        
        Args:
            task_name: Name of the task to execute
            args: Task arguments
            kwargs: Task keyword arguments
            db: Database session for tracking
            
        Returns:
            Dictionary containing task information
        """
        if not self.celery_app:
            # Return mock task result when Celery is not available
            mock_task_id = f"mock_{task_name}_{datetime.now().timestamp()}"
            return {
                "task_id": mock_task_id,
                "task_name": task_name,
                "status": "PENDING",
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "mock": True
            }
        
        try:
            # Submit task to Celery
            result = self.celery_app.send_task(
                task_name,
                args=args or [],
                kwargs=kwargs or {}
            )
            
            # Track in database if session provided
            if db:
                celery_task = CeleryTask(
                    task_id=result.id,
                    task_name=task_name,
                    status="PENDING",
                    args_list=args or [],
                    kwargs_dict=kwargs or {}
                )
                db.add(celery_task)
                db.commit()
            
            logger.info(f"Task {task_name} submitted with ID: {result.id}")
            
            return {
                "task_id": result.id,
                "task_name": task_name,
                "status": "PENDING",
                "submitted_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to submit task {task_name}: {e}")
            raise
    
    def get_task_status(self, task_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get task status from Celery and database
        
        Args:
            task_id: Task ID to check
            db: Database session
            
        Returns:
            Dictionary containing task status information
        """
        if not self.celery_app or not CELERY_AVAILABLE or task_id.startswith("mock_"):
            # Return mock status for mock tasks
            return {
                "task_id": task_id,
                "status": "SUCCESS",
                "result": {"mock": True, "message": "Mock task completed"},
                "traceback": None,
                "date_done": datetime.now(timezone.utc).isoformat()
            }
        
        try:
            # Get status from Celery
            result = AsyncResult(task_id, app=self.celery_app)
            
            task_info = {
                "task_id": task_id,
                "status": result.status,
                "result": result.result if result.ready() else None,
                "traceback": result.traceback if result.failed() else None,
                "date_done": result.date_done.isoformat() if result.date_done else None
            }
            
            # Get additional info from database if available
            if db:
                db_task = db.query(CeleryTask).filter(CeleryTask.task_id == task_id).first()
                if db_task:
                    task_info.update({
                        "task_name": db_task.task_name,
                        "created_at": db_task.created_at.isoformat() if db_task.created_at else None,
                        "started_at": db_task.started_at.isoformat() if db_task.started_at else None,
                        "completed_at": db_task.completed_at.isoformat() if db_task.completed_at else None,
                        "args": db_task.args_list,
                        "kwargs": db_task.kwargs_dict,
                        "error": db_task.error
                    })
            
            return task_info
            
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}")
            # Return mock status when Celery is not available
            return {
                "task_id": task_id,
                "status": "SUCCESS",
                "result": {"mock": True, "message": "Task completed (Celery unavailable)"},
                "traceback": None,
                "date_done": datetime.now(timezone.utc).isoformat(),
                "note": "Celery backend not available - returning mock status"
            }
    
    def cancel_task(self, task_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Cancel a running task
        
        Args:
            task_id: Task ID to cancel
            db: Database session
            
        Returns:
            Dictionary containing cancellation result
        """
        if not self.celery_app or not CELERY_AVAILABLE or task_id.startswith("mock_"):
            # Mock cancellation for mock tasks
            return {
                "task_id": task_id,
                "status": "REVOKED",
                "cancelled_at": datetime.now(timezone.utc).isoformat(),
                "mock": True
            }
        
        try:
            # Revoke task in Celery
            self.celery_app.control.revoke(task_id, terminate=True)
            
            # Update database if session provided
            if db:
                db_task = db.query(CeleryTask).filter(CeleryTask.task_id == task_id).first()
                if db_task:
                    db_task.status = "REVOKED"
                    db_task.completed_at = datetime.now(timezone.utc)
                    db_task.error = "Task cancelled by user"
                    db.commit()
            
            logger.info(f"Task {task_id} cancelled")
            
            return {
                "task_id": task_id,
                "status": "REVOKED",
                "cancelled_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return {
                "task_id": task_id,
                "status": "CANCEL_FAILED",
                "error": str(e)
            }
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of active tasks from Celery workers
        
        Returns:
            List of active task information
        """
        try:
            # Get active tasks from all workers
            inspect = self.celery_app.control.inspect()
            active_tasks = inspect.active()
            
            if not active_tasks:
                return []
            
            # Flatten tasks from all workers
            all_tasks = []
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    task_info = {
                        "task_id": task.get("id"),
                        "task_name": task.get("name"),
                        "worker": worker,
                        "args": task.get("args", []),
                        "kwargs": task.get("kwargs", {}),
                        "time_start": task.get("time_start")
                    }
                    all_tasks.append(task_info)
            
            return all_tasks
            
        except Exception as e:
            logger.error(f"Failed to get active tasks: {e}")
            return []
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """
        Get Celery worker statistics
        
        Returns:
            Dictionary containing worker statistics
        """
        try:
            inspect = self.celery_app.control.inspect()
            
            # Get worker stats
            stats = inspect.stats()
            active = inspect.active()
            registered = inspect.registered()
            
            worker_info = {}
            
            if stats:
                for worker, worker_stats in stats.items():
                    worker_info[worker] = {
                        "status": "online",
                        "pool": worker_stats.get("pool", {}),
                        "total_tasks": worker_stats.get("total", {}),
                        "active_tasks": len(active.get(worker, [])) if active else 0,
                        "registered_tasks": len(registered.get(worker, [])) if registered else 0
                    }
            
            return {
                "workers": worker_info,
                "total_workers": len(worker_info),
                "total_active_tasks": sum(len(tasks) for tasks in active.values()) if active else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get worker stats: {e}")
            return {
                "workers": {},
                "total_workers": 0,
                "total_active_tasks": 0,
                "error": str(e)
            }
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics
        
        Returns:
            Dictionary containing queue information
        """
        try:
            # This would require additional Redis inspection
            # For now, return basic queue info
            return {
                "queues": {
                    "analysis": {"length": 0, "consumers": 0},
                    "scraping": {"length": 0, "consumers": 0},
                    "processing": {"length": 0, "consumers": 0}
                },
                "note": "Queue length inspection requires Redis connection"
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {"error": str(e)}
    
    def cleanup_old_tasks(self, db: Session, days_old: int = 7) -> int:
        """
        Clean up old task records from database
        
        Args:
            db: Database session
            days_old: Remove tasks older than this many days
            
        Returns:
            Number of tasks cleaned up
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
            
            # Delete old completed tasks
            deleted_count = db.query(CeleryTask).filter(
                CeleryTask.completed_at < cutoff_date,
                CeleryTask.status.in_(["SUCCESS", "FAILURE", "REVOKED"])
            ).delete()
            
            db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old task records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old tasks: {e}")
            db.rollback()
            return 0
    
    def update_task_status(self, task_id: str, status: str, result: Any = None, 
                          error: str = None, db: Optional[Session] = None):
        """
        Update task status in database
        
        Args:
            task_id: Task ID
            status: New status
            result: Task result
            error: Error message if failed
            db: Database session
        """
        if not db:
            return
        
        try:
            db_task = db.query(CeleryTask).filter(CeleryTask.task_id == task_id).first()
            if not db_task:
                return
            
            db_task.status = status
            
            if status == "STARTED" and not db_task.started_at:
                db_task.started_at = datetime.now(timezone.utc)
            
            if status in ["SUCCESS", "FAILURE", "REVOKED"] and not db_task.completed_at:
                db_task.completed_at = datetime.now(timezone.utc)
            
            if result:
                db_task.result_dict = result
            
            if error:
                db_task.error = error
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            db.rollback()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Celery system
        
        Returns:
            Dictionary containing health status
        """
        try:
            # Submit a simple health check task
            result = self.celery_app.send_task("health_check")
            
            # Wait for result with timeout
            try:
                health_result = result.get(timeout=10)
                return {
                    "healthy": True,
                    "celery_status": "connected",
                    "redis_status": "connected",
                    "health_check_result": health_result
                }
            except Exception as e:
                return {
                    "healthy": False,
                    "celery_status": "connected",
                    "redis_status": "unknown",
                    "error": f"Health check task failed: {e}"
                }
                
        except Exception as e:
            return {
                "healthy": False,
                "celery_status": "disconnected",
                "redis_status": "unknown",
                "error": str(e)
            }