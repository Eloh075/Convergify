"""
Celery application configuration for background tasks
"""
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
from config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "career_analysis",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["tasks.analysis_tasks", "tasks.scraping_tasks"]
)

# Configure Celery
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Task routing
    task_routes={
        'tasks.analysis_tasks.*': {'queue': 'analysis'},
        'tasks.scraping_tasks.*': {'queue': 'scraping'},
    },
    
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Task monitoring signals
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Handle task start"""
    logger.info(f"Task {task.name} [{task_id}] started")

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """Handle task completion"""
    logger.info(f"Task {task.name} [{task_id}] completed with state: {state}")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """Handle task failure"""
    logger.error(f"Task {sender.name} [{task_id}] failed: {exception}")

# Health check task
@celery_app.task(bind=True)
def health_check(self):
    """Health check task for monitoring"""
    return {
        "status": "healthy",
        "task_id": self.request.id,
        "timestamp": "now"
    }