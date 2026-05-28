"""
Session management service
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone

from models.session import AnalysisSession
from models.user import User
from models.resume import Resume
from models.job import Job
from models.analysis import Analysis
from services.user_service import UserService

class SessionService:
    """Service for managing analysis sessions"""
    
    def __init__(self):
        self.user_service = UserService()
    
    def create_session(self, user_id: str, title: str, session_type: str = "comprehensive",
                      description: str = None, configuration: Dict[str, Any] = None,
                      db: Session = None) -> AnalysisSession:
        """
        Create a new analysis session
        
        Args:
            user_id: User ID who owns the session
            title: Session title
            session_type: Type of session (comprehensive, single_job, market_analysis)
            description: Optional session description
            configuration: Session configuration dictionary
            db: Database session
            
        Returns:
            Created AnalysisSession object
        """
        # Ensure user exists
        user = self.user_service.get_or_create_user(user_id, db)
        
        session = AnalysisSession(
            user_id=user_id,
            title=title,
            session_type=session_type,
            description=description,
            status="active"
        )
        
        if configuration:
            session.configuration_dict = configuration
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    def get_session(self, session_id: str, user_id: str = None, db: Session = None) -> Optional[AnalysisSession]:
        """
        Get a session by ID
        
        Args:
            session_id: Session ID
            user_id: Optional user ID for access control
            db: Database session
            
        Returns:
            AnalysisSession object or None if not found
        """
        query = db.query(AnalysisSession).filter(AnalysisSession.id == session_id)
        
        if user_id:
            query = query.filter(AnalysisSession.user_id == user_id)
        
        return query.first()
    
    def list_sessions(self, user_id: str, status: Optional[str] = None,
                     session_type: Optional[str] = None, tags: Optional[List[str]] = None,
                     skip: int = 0, limit: int = 100, sort_by: str = "updated_at",
                     sort_order: str = "desc", db: Session = None) -> List[AnalysisSession]:
        """
        List sessions with filtering and sorting
        
        Args:
            user_id: User ID to filter by
            status: Optional status filter
            session_type: Optional session type filter
            tags: Optional tags to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            db: Database session
            
        Returns:
            List of AnalysisSession objects
        """
        query = db.query(AnalysisSession).filter(AnalysisSession.user_id == user_id)
        
        if status:
            query = query.filter(AnalysisSession.status == status)
        
        if session_type:
            query = query.filter(AnalysisSession.session_type == session_type)
        
        # Apply sorting
        if hasattr(AnalysisSession, sort_by):
            sort_column = getattr(AnalysisSession, sort_by)
            if sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        sessions = query.offset(skip).limit(limit).all()
        
        # Filter by tags if specified (client-side filtering for JSON field)
        if tags:
            filtered_sessions = []
            for session in sessions:
                session_tags = session.tags_list
                if any(tag in session_tags for tag in tags):
                    filtered_sessions.append(session)
            return filtered_sessions
        
        return sessions
    
    def update_session(self, session_id: str, user_id: str, updates: Dict[str, Any],
                      db: Session = None) -> Optional[AnalysisSession]:
        """
        Update a session
        
        Args:
            session_id: Session ID
            user_id: User ID for access control
            updates: Dictionary of fields to update
            db: Database session
            
        Returns:
            Updated AnalysisSession object or None if not found
        """
        session = self.get_session(session_id, user_id, db)
        if not session:
            return None
        
        # Update allowed fields
        allowed_fields = ['title', 'description', 'status', 'session_type']
        for field, value in updates.items():
            if field in allowed_fields and hasattr(session, field):
                setattr(session, field, value)
        
        # Handle special fields
        if 'configuration' in updates:
            session.configuration_dict = updates['configuration']
        
        if 'tags' in updates:
            session.tags_list = updates['tags']
        
        session.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(session)
        
        return session
    
    def delete_session(self, session_id: str, user_id: str, db: Session = None) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session ID
            user_id: User ID for access control
            db: Database session
            
        Returns:
            True if deleted, False if not found
        """
        session = self.get_session(session_id, user_id, db)
        if not session:
            return False
        
        db.delete(session)
        db.commit()
        return True
    
    def add_resume_to_session(self, session_id: str, resume_id: str, user_id: str,
                             db: Session = None) -> bool:
        """
        Add a resume to a session
        
        Args:
            session_id: Session ID
            resume_id: Resume ID to add
            user_id: User ID for access control
            db: Database session
            
        Returns:
            True if added, False if session not found
        """
        session = self.get_session(session_id, user_id, db)
        if not session:
            return False
        
        # Verify resume exists and belongs to user
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            return False
        
        session.add_resume(resume_id)
        db.commit()
        return True
    
    def remove_resume_from_session(self, session_id: str, resume_id: str, user_id: str,
                                  db: Session = None) -> bool:
        """
        Remove a resume from a session
        
        Args:
            session_id: Session ID
            resume_id: Resume ID to remove
            user_id: User ID for access control
            db: Database session
            
        Returns:
            True if removed, False if session not found
        """
        session = self.get_session(session_id, user_id, db)
        if not session:
            return False
        
        session.remove_resume(resume_id)
        db.commit()
        return True
    
    def add_job_to_session(self, session_id: str, job_id: str, user_id: str,
                          db: Session = None) -> bool:
        """
        Add a job to a session
        
        Args:
            session_id: Session ID
            job_id: Job ID to add
            user_id: User ID for access control
            db: Database session
            
        Returns:
            True if added, False if session not found
        """
        session = self.get_session(session_id, user_id, db)
        if not session:
            return False
        
        # Verify job exists
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False
        
        session.add_job(job_id)
        db.commit()
        return True
    
    def remove_job_from_session(self, session_id: str, job_id: str, user_id: str,
                               db: Session = None) -> bool:
        """
        Remove a job from a session
        
        Args:
            session_id: Session ID
            job_id: Job ID to remove
            user_id: User ID for access control
            db: Database session
            
        Returns:
            True if removed, False if session not found
        """
        session = self.get_session(session_id, user_id, db)
        if not session:
            return False
        
        session.remove_job(job_id)
        db.commit()
        return True
    
    def add_analysis_to_session(self, session_id: str, analysis_id: str, user_id: str,
                               db: Session = None) -> bool:
        """
        Add an analysis to a session
        
        Args:
            session_id: Session ID
            analysis_id: Analysis ID to add
            user_id: User ID for access control
            db: Database session
            
        Returns:
            True if added, False if session not found
        """
        session = self.get_session(session_id, user_id, db)
        if not session:
            return False
        
        # Verify analysis exists
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return False
        
        session.add_analysis(analysis_id)
        db.commit()
        return True
    
    def get_session_details(self, session_id: str, user_id: str, db: Session = None) -> Optional[Dict[str, Any]]:
        """
        Get detailed session information including related objects
        
        Args:
            session_id: Session ID
            user_id: User ID for access control
            db: Database session
            
        Returns:
            Dictionary with session details or None if not found
        """
        session = self.get_session(session_id, user_id, db)
        if not session:
            return None
        
        # Get related resumes
        resumes = []
        if session.resume_ids_list:
            resumes = db.query(Resume).filter(
                Resume.id.in_(session.resume_ids_list)
            ).all()
        
        # Get related jobs
        jobs = []
        if session.job_ids_list:
            jobs = db.query(Job).filter(
                Job.id.in_(session.job_ids_list)
            ).all()
        
        # Get related analyses
        analyses = []
        if session.analysis_ids_list:
            analyses = db.query(Analysis).filter(
                Analysis.id.in_(session.analysis_ids_list)
            ).all()
        
        return {
            "session": session.get_summary(),
            "resumes": [
                {
                    "id": resume.id,
                    "filename": resume.filename,
                    "upload_date": resume.upload_date.isoformat() if resume.upload_date else None,
                    "analysis_status": resume.analysis_status
                }
                for resume in resumes
            ],
            "jobs": [
                {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "created_date": job.created_date.isoformat() if job.created_date else None
                }
                for job in jobs
            ],
            "analyses": [
                {
                    "id": analysis.id,
                    "status": analysis.status,
                    "start_date": analysis.start_date.isoformat() if analysis.start_date else None,
                    "completion_date": analysis.completion_date.isoformat() if analysis.completion_date else None,
                    "job_count": analysis.job_count
                }
                for analysis in analyses
            ]
        }
    
    def complete_session(self, session_id: str, user_id: str, overall_score: float = None,
                        db: Session = None) -> bool:
        """
        Mark a session as completed
        
        Args:
            session_id: Session ID
            user_id: User ID for access control
            overall_score: Optional overall match score
            db: Database session
            
        Returns:
            True if completed, False if session not found
        """
        session = self.get_session(session_id, user_id, db)
        if not session:
            return False
        
        session.mark_completed(overall_score)
        db.commit()
        return True
    
    def archive_session(self, session_id: str, user_id: str, db: Session = None) -> bool:
        """
        Archive a session
        
        Args:
            session_id: Session ID
            user_id: User ID for access control
            db: Database session
            
        Returns:
            True if archived, False if session not found
        """
        session = self.get_session(session_id, user_id, db)
        if not session:
            return False
        
        session.archive()
        db.commit()
        return True
    
    def restore_session(self, session_id: str, user_id: str, db: Session = None) -> bool:
        """
        Restore an archived session
        
        Args:
            session_id: Session ID
            user_id: User ID for access control
            db: Database session
            
        Returns:
            True if restored, False if session not found
        """
        session = self.get_session(session_id, user_id, db)
        if not session:
            return False
        
        session.restore()
        db.commit()
        return True
    
    def get_session_statistics(self, user_id: str, db: Session = None) -> Dict[str, Any]:
        """
        Get session statistics for a user
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Dictionary with session statistics
        """
        total_sessions = db.query(AnalysisSession).filter(
            AnalysisSession.user_id == user_id
        ).count()
        
        active_sessions = db.query(AnalysisSession).filter(
            AnalysisSession.user_id == user_id,
            AnalysisSession.status == "active"
        ).count()
        
        completed_sessions = db.query(AnalysisSession).filter(
            AnalysisSession.user_id == user_id,
            AnalysisSession.status == "completed"
        ).count()
        
        archived_sessions = db.query(AnalysisSession).filter(
            AnalysisSession.user_id == user_id,
            AnalysisSession.status == "archived"
        ).count()
        
        # Get session type breakdown
        session_types = db.query(
            AnalysisSession.session_type,
            func.count(AnalysisSession.id)
        ).filter(
            AnalysisSession.user_id == user_id
        ).group_by(AnalysisSession.session_type).all()
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "archived_sessions": archived_sessions,
            "session_types": {session_type: count for session_type, count in session_types}
        }
    
    def auto_create_session_from_analysis(self, analysis_id: str, db: Session = None) -> Optional[AnalysisSession]:
        """
        Automatically create a session from an analysis
        
        Args:
            analysis_id: Analysis ID
            db: Database session
            
        Returns:
            Created AnalysisSession or None if analysis not found
        """
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return None
        
        # Get the resume to determine user
        resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
        if not resume:
            return None
        
        # Create session title based on analysis
        title = f"Analysis Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        session = self.create_session(
            user_id=resume.user_id,
            title=title,
            session_type="comprehensive",
            description=f"Auto-created from analysis {analysis_id}",
            db=db
        )
        
        # Add the resume and jobs to the session
        session.add_resume(analysis.resume_id)
        if analysis.job_ids_list:
            for job_id in analysis.job_ids_list:
                session.add_job(job_id)
        
        session.add_analysis(analysis_id)
        
        db.commit()
        return session