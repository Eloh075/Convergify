"""
Celery task tracking model
"""
from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime
import uuid
import json

from database import Base

class CeleryTask(Base):
    __tablename__ = "celery_tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, unique=True, nullable=False)
    task_name = Column(String, nullable=False)
    status = Column(String, default="pending")
    args = Column(Text)  # JSON array
    kwargs = Column(Text)  # JSON object
    result = Column(Text)  # JSON object
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    @property
    def args_list(self):
        """Get task args as Python list"""
        if self.args:
            try:
                return json.loads(self.args)
            except json.JSONDecodeError:
                return []
        return []
    
    @args_list.setter
    def args_list(self, value):
        """Set task args from Python list"""
        if value:
            self.args = json.dumps(value)
        else:
            self.args = None
    
    @property
    def kwargs_dict(self):
        """Get task kwargs as Python dict"""
        if self.kwargs:
            try:
                return json.loads(self.kwargs)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @kwargs_dict.setter
    def kwargs_dict(self, value):
        """Set task kwargs from Python dict"""
        if value:
            self.kwargs = json.dumps(value)
        else:
            self.kwargs = None
    
    @property
    def result_dict(self):
        """Get task result as Python dict"""
        if self.result:
            try:
                return json.loads(self.result)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @result_dict.setter
    def result_dict(self, value):
        """Set task result from Python dict"""
        if value:
            self.result = json.dumps(value)
        else:
            self.result = None
    
    @property
    def duration(self):
        """Get task duration if completed"""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def is_completed(self):
        """Check if task is completed"""
        return self.status in ["SUCCESS", "FAILURE"] and self.completed_at is not None
    
    def mark_started(self):
        """Mark task as started"""
        self.status = "STARTED"
        self.started_at = datetime.utcnow()
    
    def mark_success(self, result=None):
        """Mark task as successful"""
        self.status = "SUCCESS"
        self.completed_at = datetime.utcnow()
        if result:
            self.result_dict = result
    
    def mark_failure(self, error_message):
        """Mark task as failed"""
        self.status = "FAILURE"
        self.completed_at = datetime.utcnow()
        self.error = error_message
    
    def __repr__(self):
        return f"<CeleryTask(id={self.id}, task_id={self.task_id}, status={self.status})>"