"""
Resume management service
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from datetime import datetime, timezone

from models import Resume, User, OptimizedResume
from schemas.resume import ResumeCreate, ResumeResponse, ResumeComparison
from services.file_service import FileService
from services.user_service import UserService

class ResumeService:
    """Service for resume management operations"""
    
    def __init__(self):
        self.file_service = FileService()
        self.user_service = UserService()
    
    async def upload_resume(self, file: UploadFile, user_id: str, db: Session) -> Dict[str, Any]:
        """Upload and process a resume file"""
        
        # Get or create user
        if user_id == "default-user":
            user = self.user_service.get_or_create_default_user(db)
        else:
            user = self.user_service.get_user(user_id, db)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
        
        # Process the file
        processing_result = await self.file_service.process_resume_file(file)
        
        if not processing_result["success"]:
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "File processing failed",
                    "errors": processing_result["errors"],
                    "validation": processing_result.get("validation", {})
                }
            )
        
        # Create resume record
        resume = Resume(
            user_id=user_id,
            filename=processing_result["file_info"]["filename"],
            original_text=processing_result["extracted_text"],
            file_path=processing_result["file_path"],
            file_size=processing_result["file_info"]["size"],
            analysis_status="pending" if processing_result["extracted_text"] else "extraction_failed"
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Update user's last active time
        self.user_service.update_last_active(user_id, db)
        
        return {
            "resume": ResumeResponse.from_orm(resume),
            "extracted_text": processing_result["extracted_text"],
            "processing_status": "success" if processing_result["extracted_text"] else "text_extraction_failed",
            "extraction_info": processing_result["extraction_info"],
            "warnings": processing_result["validation"].get("warnings", [])
        }
    
    def get_resumes(self, user_id: str, db: Session, skip: int = 0, limit: int = 100) -> List[ResumeResponse]:
        """Get all resumes for a user"""
        resumes = db.query(Resume).filter(
            Resume.user_id == user_id
        ).offset(skip).limit(limit).all()
        
        return [ResumeResponse.from_orm(resume) for resume in resumes]
    
    def get_resume(self, resume_id: str, user_id: str, db: Session) -> Optional[ResumeResponse]:
        """Get a specific resume"""
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            return None
        
        return ResumeResponse.from_orm(resume)
    
    def delete_resume(self, resume_id: str, user_id: str, db: Session) -> bool:
        """Delete a resume and its file"""
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            return False
        
        # Delete the file
        self.file_service.delete_file(resume.file_path)
        
        # Delete optimized version if exists
        if resume.optimized_version:
            if resume.optimized_version.file_path:
                self.file_service.delete_file(resume.optimized_version.file_path)
        
        # Delete from database
        db.delete(resume)
        db.commit()
        
        return True
    
    def get_resume_comparison(self, resume_id: str, user_id: str, db: Session) -> Optional[ResumeComparison]:
        """Get comparison between original and optimized resume"""
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            return None
        
        comparison = ResumeComparison(
            original=ResumeResponse.from_orm(resume),
            optimized=None,
            changes=[],
            improvement_score=None
        )
        
        if resume.optimized_version:
            from schemas.resume import OptimizedResumeResponse
            comparison.optimized = OptimizedResumeResponse.from_orm(resume.optimized_version)
            comparison.changes = resume.optimized_version.changes_list
            comparison.improvement_score = resume.optimized_version.improvement_score
        
        return comparison
    
    def update_resume_status(self, resume_id: str, status: str, db: Session) -> bool:
        """Update resume analysis status"""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return False
        
        resume.analysis_status = status
        db.commit()
        return True
    
    def set_extracted_skills(self, resume_id: str, skills: List[str], db: Session) -> bool:
        """Set extracted skills for a resume"""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return False
        
        resume.skills_list = skills
        db.commit()
        return True
    
    def get_resume_text(self, resume_id: str, user_id: str, db: Session) -> Optional[str]:
        """Get the original text content of a resume"""
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            return None
        
        return resume.original_text
    
    def search_resumes(self, user_id: str, query: str, db: Session) -> List[ResumeResponse]:
        """Search resumes by filename or content"""
        resumes = db.query(Resume).filter(
            Resume.user_id == user_id,
            (Resume.filename.contains(query) | Resume.original_text.contains(query))
        ).all()
        
        return [ResumeResponse.from_orm(resume) for resume in resumes]
    
    def get_resume_stats(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get resume statistics for a user"""
        total_resumes = db.query(Resume).filter(Resume.user_id == user_id).count()
        
        status_counts = db.query(Resume.analysis_status, db.func.count(Resume.id)).filter(
            Resume.user_id == user_id
        ).group_by(Resume.analysis_status).all()
        
        optimized_count = db.query(Resume).filter(
            Resume.user_id == user_id,
            Resume.optimized_version_id.isnot(None)
        ).count()
        
        return {
            "total_resumes": total_resumes,
            "optimized_resumes": optimized_count,
            "status_breakdown": {status: count for status, count in status_counts}
        }
    
    def list_resumes(self, user_id: Optional[str] = None, status: Optional[str] = None,
                    skip: int = 0, limit: int = 100, sort_by: str = "upload_date",
                    sort_order: str = "desc", db: Session = None) -> List[ResumeResponse]:
        """List resumes with advanced filtering and sorting"""
        query = db.query(Resume)
        
        if user_id:
            query = query.filter(Resume.user_id == user_id)
        
        if status:
            query = query.filter(Resume.analysis_status == status)
        
        # Apply sorting
        if hasattr(Resume, sort_by):
            sort_column = getattr(Resume, sort_by)
            if sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        resumes = query.offset(skip).limit(limit).all()
        return [ResumeResponse.from_orm(resume) for resume in resumes]
    
    def get_resume_metadata(self, resume_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get resume metadata and processing status"""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return None
        
        return {
            "id": resume.id,
            "filename": resume.filename,
            "file_size": resume.file_size,
            "analysis_status": resume.analysis_status,
            "created_at": resume.created_at.isoformat() if resume.created_at else None,
            "updated_at": resume.updated_at.isoformat() if resume.updated_at else None,
            "skills_count": len(resume.skills_list) if resume.skills_list else 0,
            "has_optimized_version": resume.optimized_version_id is not None,
            "text_length": len(resume.original_text) if resume.original_text else 0
        }
    
    def get_resume_history(self, resume_id: str, include_analyses: bool = True,
                          include_optimizations: bool = True, db: Session = None) -> Optional[Dict[str, Any]]:
        """Get complete history of resume analyses and optimizations"""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return None
        
        history = {
            "resume_id": resume_id,
            "resume_info": {
                "filename": resume.filename,
                "created_at": resume.created_at.isoformat() if resume.created_at else None,
                "current_status": resume.analysis_status
            },
            "analyses": [],
            "optimizations": []
        }
        
        if include_analyses:
            from models.analysis import Analysis
            analyses = db.query(Analysis).filter(Analysis.resume_id == resume_id).all()
            history["analyses"] = [
                {
                    "id": analysis.id,
                    "analysis_type": analysis.analysis_type,
                    "status": analysis.status,
                    "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                    "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
                    "job_count": len(analysis.job_ids_list) if analysis.job_ids_list else 0
                }
                for analysis in analyses
            ]
        
        if include_optimizations:
            optimized_resumes = db.query(OptimizedResume).filter(
                OptimizedResume.original_resume_id == resume_id
            ).all()
            history["optimizations"] = [
                {
                    "id": opt.id,
                    "improvement_score": opt.improvement_score,
                    "changes_count": len(opt.changes_list) if opt.changes_list else 0,
                    "created_at": opt.created_at.isoformat() if opt.created_at else None,
                    "target_jobs_count": len(opt.target_jobs_list) if opt.target_jobs_list else 0
                }
                for opt in optimized_resumes
            ]
        
        return history
    
    def get_resume_analyses(self, resume_id: str, status: Optional[str] = None,
                           analysis_type: Optional[str] = None, skip: int = 0,
                           limit: int = 50, db: Session = None) -> List[Dict[str, Any]]:
        """Get all analyses for a resume"""
        from models.analysis import Analysis
        
        query = db.query(Analysis).filter(Analysis.resume_id == resume_id)
        
        if status:
            query = query.filter(Analysis.status == status)
        
        if analysis_type:
            query = query.filter(Analysis.analysis_type == analysis_type)
        
        analyses = query.offset(skip).limit(limit).all()
        
        return [
            {
                "id": analysis.id,
                "analysis_type": analysis.analysis_type,
                "status": analysis.status,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
                "job_ids": analysis.job_ids_list,
                "task_id": analysis.task_id,
                "has_results": analysis.results_dict is not None
            }
            for analysis in analyses
        ]
    
    def get_optimized_resumes(self, resume_id: str, skip: int = 0, limit: int = 10,
                             db: Session = None) -> List[Dict[str, Any]]:
        """Get all optimized versions of a resume"""
        optimized_resumes = db.query(OptimizedResume).filter(
            OptimizedResume.original_resume_id == resume_id
        ).offset(skip).limit(limit).all()
        
        return [
            {
                "id": opt.id,
                "improvement_score": opt.improvement_score,
                "changes_count": len(opt.changes_list) if opt.changes_list else 0,
                "created_at": opt.created_at.isoformat() if opt.created_at else None,
                "target_jobs": opt.target_jobs_list,
                "text_length": len(opt.optimized_text) if opt.optimized_text else 0
            }
            for opt in optimized_resumes
        ]
    
    def compare_resumes(self, resume_id: str, optimized_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Compare original resume with optimized version"""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        optimized = db.query(OptimizedResume).filter(OptimizedResume.id == optimized_id).first()
        
        if not resume or not optimized:
            return None
        
        return {
            "original": {
                "id": resume.id,
                "filename": resume.filename,
                "text": resume.original_text,
                "text_length": len(resume.original_text) if resume.original_text else 0,
                "skills": resume.skills_list or []
            },
            "optimized": {
                "id": optimized.id,
                "text": optimized.optimized_text,
                "text_length": len(optimized.optimized_text) if optimized.optimized_text else 0,
                "improvement_score": optimized.improvement_score,
                "changes": optimized.changes_list or []
            },
            "comparison": {
                "text_length_change": (len(optimized.optimized_text) if optimized.optimized_text else 0) - (len(resume.original_text) if resume.original_text else 0),
                "changes_count": len(optimized.changes_list) if optimized.changes_list else 0,
                "improvement_score": optimized.improvement_score
            }
        }
    
    def delete_optimized_resume(self, resume_id: str, optimized_id: str, db: Session) -> bool:
        """Delete a specific optimized resume version"""
        optimized = db.query(OptimizedResume).filter(
            OptimizedResume.id == optimized_id,
            OptimizedResume.original_resume_id == resume_id
        ).first()
        
        if not optimized:
            return False
        
        # Delete file if exists
        if optimized.file_path:
            self.file_service.delete_file(optimized.file_path)
        
        # Remove reference from original resume if this was the linked version
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume and resume.optimized_version_id == optimized_id:
            resume.optimized_version_id = None
        
        db.delete(optimized)
        db.commit()
        return True
    
    def get_resume_file_path(self, resume_id: str, db: Session) -> Optional[str]:
        """Get the file path for a resume"""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        return resume.file_path if resume else None
    
    def export_optimized_resume(self, resume_id: str, optimized_id: str, format: str, db: Session) -> Optional[str]:
        """Export optimized resume in specified format"""
        optimized = db.query(OptimizedResume).filter(
            OptimizedResume.id == optimized_id,
            OptimizedResume.original_resume_id == resume_id
        ).first()
        
        if not optimized:
            return None
        
        # For now, return a simple text export
        # In a full implementation, this would generate PDF, etc.
        import tempfile
        import os
        
        if format == "txt":
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            temp_file.write(optimized.optimized_text or "")
            temp_file.close()
            return temp_file.name
        elif format == "markdown":
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
            temp_file.write(f"# Optimized Resume\n\n{optimized.optimized_text or ''}")
            temp_file.close()
            return temp_file.name
        else:
            # PDF generation would go here
            return None
    
    def duplicate_resume(self, resume_id: str, new_name: Optional[str], db: Session) -> Optional[Dict[str, Any]]:
        """Create a duplicate of an existing resume"""
        original = db.query(Resume).filter(Resume.id == resume_id).first()
        if not original:
            return None
        
        # Create new resume with copied data
        duplicate = Resume(
            user_id=original.user_id,
            filename=new_name or f"Copy of {original.filename}",
            original_text=original.original_text,
            file_path=None,  # Don't copy file path
            file_size=original.file_size,
            analysis_status="pending",
            skills_list=original.skills_list.copy() if original.skills_list else None
        )
        
        db.add(duplicate)
        db.commit()
        db.refresh(duplicate)
        
        return {
            "id": duplicate.id,
            "filename": duplicate.filename,
            "created_at": duplicate.created_at.isoformat() if duplicate.created_at else None,
            "message": "Resume duplicated successfully"
        }
    
    def export_resume_data(self, resume_id: str, format: str, include_analyses: bool,
                          include_optimizations: bool, db: Session) -> Optional[Dict[str, Any]]:
        """Export complete resume data including analyses and optimizations"""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return None
        
        export_data = {
            "resume": {
                "id": resume.id,
                "filename": resume.filename,
                "original_text": resume.original_text,
                "file_size": resume.file_size,
                "analysis_status": resume.analysis_status,
                "skills": resume.skills_list,
                "created_at": resume.created_at.isoformat() if resume.created_at else None,
                "updated_at": resume.updated_at.isoformat() if resume.updated_at else None
            }
        }
        
        if include_analyses:
            from models.analysis import Analysis
            analyses = db.query(Analysis).filter(Analysis.resume_id == resume_id).all()
            export_data["analyses"] = [
                {
                    "id": analysis.id,
                    "analysis_type": analysis.analysis_type,
                    "status": analysis.status,
                    "job_ids": analysis.job_ids_list,
                    "results": analysis.results_dict,
                    "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                    "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None
                }
                for analysis in analyses
            ]
        
        if include_optimizations:
            optimized_resumes = db.query(OptimizedResume).filter(
                OptimizedResume.original_resume_id == resume_id
            ).all()
            export_data["optimizations"] = [
                {
                    "id": opt.id,
                    "optimized_text": opt.optimized_text,
                    "changes": opt.changes_list,
                    "improvement_score": opt.improvement_score,
                    "target_jobs": opt.target_jobs_list,
                    "created_at": opt.created_at.isoformat() if opt.created_at else None
                }
                for opt in optimized_resumes
            ]
        
        return {
            "format": format,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "data": export_data
        }