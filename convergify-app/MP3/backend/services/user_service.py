"""
User management service
"""
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from models import User

class UserService:
    """Service for user management operations"""
    
    def get_or_create_default_user(self, db: Session) -> User:
        """Get or create the default user"""
        user = db.query(User).filter(User.id == "default-user").first()
        
        if not user:
            user = User(
                id="default-user",
                created_at=datetime.now(timezone.utc),
                last_active=datetime.now(timezone.utc)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
    
    def get_or_create_user(self, user_id: str, db: Session) -> User:
        """Get or create a user by ID"""
        if user_id == "default-user":
            return self.get_or_create_default_user(db)
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            user = User(
                id=user_id,
                created_at=datetime.now(timezone.utc),
                last_active=datetime.now(timezone.utc)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
    
    def update_last_active(self, user_id: str, db: Session) -> bool:
        """Update user's last active timestamp"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_active = datetime.now(timezone.utc)
            db.commit()
            return True
        return False