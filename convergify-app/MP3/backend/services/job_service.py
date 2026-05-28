"""
Job management service
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from models.job import Job, JobGroup
from schemas.job import JobCreateRequest, JobResponse, JobGroupCreateRequest, JobGroupResponse

class JobService:
    """Service for job management operations"""
    
    def create_job(self, job_data: JobCreateRequest, db: Session) -> JobResponse:
        """Create a new job"""
        job = Job(
            title=job_data.title,
            company=job_data.company,
            description=job_data.description,
            location=job_data.location,
            salary_min=job_data.salary_min,
            salary_max=job_data.salary_max,
            source="manual"
        )
        
        # Use the property setters to handle JSON conversion
        job.requirements_list = job_data.requirements or []
        job.skills_list = job_data.skills or []
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return JobResponse.from_job_model(job)
    
    def list_jobs(self, company: Optional[str] = None, location: Optional[str] = None,
                  source: Optional[str] = None, group_id: Optional[str] = None,
                  skip: int = 0, limit: int = 100, sort_by: str = "created_date",
                  sort_order: str = "desc", db: Session = None) -> List[JobResponse]:
        """List jobs with filtering and sorting"""
        query = db.query(Job)
        
        if company:
            query = query.filter(Job.company.ilike(f"%{company}%"))
        
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        
        if source:
            query = query.filter(Job.source == source)
        
        if group_id:
            query = query.filter(Job.group_id == group_id)
        
        # Apply sorting
        if hasattr(Job, sort_by):
            sort_column = getattr(Job, sort_by)
            if sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        jobs = query.offset(skip).limit(limit).all()
        return [JobResponse.from_job_model(job) for job in jobs]
    
    def get_job(self, job_id: str, db: Session) -> Optional[JobResponse]:
        """Get a specific job by ID"""
        job = db.query(Job).filter(Job.id == job_id).first()
        return JobResponse.from_job_model(job) if job else None
    
    def update_job(self, job_id: str, job_data: JobCreateRequest, db: Session) -> Optional[JobResponse]:
        """Update a job"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None
        
        job.title = job_data.title
        job.company = job_data.company
        job.description = job_data.description
        job.location = job_data.location
        job.salary_min = job_data.salary_min
        job.salary_max = job_data.salary_max
        
        # Use property setters for JSON conversion
        job.requirements_list = job_data.requirements or []
        job.skills_list = job_data.skills or []
        
        db.commit()
        db.refresh(job)
        
        return JobResponse.from_job_model(job)
    
    def delete_job(self, job_id: str, db: Session) -> bool:
        """Delete a job"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False
        
        # Remove from any groups
        if job.group_id:
            group = db.query(JobGroup).filter(JobGroup.id == job.group_id).first()
            if group and group.job_ids_list:
                group.job_ids_list = [jid for jid in group.job_ids_list if jid != job_id]
                db.commit()
        
        db.delete(job)
        db.commit()
        return True
    
    def create_jobs_bulk(self, jobs_data: List[JobCreateRequest], db: Session) -> List[JobResponse]:
        """Create multiple jobs at once"""
        jobs = []
        for job_data in jobs_data:
            job = Job(
                title=job_data.title,
                company=job_data.company,
                description=job_data.description,
                location=job_data.location,
                salary_min=job_data.salary_min,
                salary_max=job_data.salary_max,
                source="manual"
            )
            # Use property setters for JSON conversion
            job.requirements_list = job_data.requirements or []
            job.skills_list = job_data.skills or []
            jobs.append(job)
        
        db.add_all(jobs)
        db.commit()
        
        for job in jobs:
            db.refresh(job)
        
        return [JobResponse.from_job_model(job) for job in jobs]
    
    def delete_jobs_bulk(self, job_ids: List[str], db: Session) -> int:
        """Delete multiple jobs at once"""
        # Remove from groups first
        groups = db.query(JobGroup).all()
        for group in groups:
            if group.job_ids_list:
                original_count = len(group.job_ids_list)
                group.job_ids_list = [jid for jid in group.job_ids_list if jid not in job_ids]
                if len(group.job_ids_list) != original_count:
                    db.commit()
        
        # Delete jobs
        deleted_count = db.query(Job).filter(Job.id.in_(job_ids)).delete(synchronize_session=False)
        db.commit()
        
        return deleted_count
    
    def search_jobs(self, query: str, search_in: str, skip: int, limit: int, db: Session) -> List[JobResponse]:
        """Search jobs by title, company, or description"""
        db_query = db.query(Job)
        
        if search_in == "title":
            db_query = db_query.filter(Job.title.ilike(f"%{query}%"))
        elif search_in == "company":
            db_query = db_query.filter(Job.company.ilike(f"%{query}%"))
        elif search_in == "description":
            db_query = db_query.filter(Job.description.ilike(f"%{query}%"))
        else:  # search_in == "all"
            db_query = db_query.filter(
                (Job.title.ilike(f"%{query}%")) |
                (Job.company.ilike(f"%{query}%")) |
                (Job.description.ilike(f"%{query}%"))
            )
        
        jobs = db_query.offset(skip).limit(limit).all()
        return [JobResponse.from_job_model(job) for job in jobs]
    
    def get_job_stats(self, db: Session) -> Dict[str, Any]:
        """Get job statistics"""
        total_jobs = db.query(Job).count()
        
        # Count by source
        source_counts = db.query(Job.source, db.func.count(Job.id)).group_by(Job.source).all()
        
        # Count by company (top 10)
        company_counts = db.query(Job.company, db.func.count(Job.id)).group_by(
            Job.company
        ).order_by(db.func.count(Job.id).desc()).limit(10).all()
        
        # Count by location (top 10)
        location_counts = db.query(Job.location, db.func.count(Job.id)).group_by(
            Job.location
        ).order_by(db.func.count(Job.id).desc()).limit(10).all()
        
        # Jobs with skills extracted
        jobs_with_skills = db.query(Job).filter(Job.skills_list.isnot(None)).count()
        
        return {
            "total_jobs": total_jobs,
            "jobs_with_skills": jobs_with_skills,
            "source_breakdown": {source: count for source, count in source_counts},
            "top_companies": [{"company": company, "count": count} for company, count in company_counts],
            "top_locations": [{"location": location, "count": count} for location, count in location_counts]
        }
    
    def export_jobs(self, format: str, group_id: Optional[str], include_skills: bool, db: Session) -> Dict[str, Any]:
        """Export jobs data"""
        query = db.query(Job)
        
        if group_id:
            query = query.filter(Job.group_id == group_id)
        
        jobs = query.all()
        
        export_data = []
        for job in jobs:
            job_data = {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "description": job.description,
                "requirements": job.requirements,
                "location": job.location,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "source": job.source,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "scraped_date": job.scraped_date.isoformat() if job.scraped_date else None
            }
            
            if include_skills:
                job_data["skills"] = job.skills_list
            
            export_data.append(job_data)
        
        return {
            "format": format,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_jobs": len(export_data),
            "group_id": group_id,
            "data": export_data
        }
    
    # Job Group methods
    def create_job_group(self, group_data: JobGroupCreateRequest, db: Session) -> JobGroupResponse:
        """Create a new job group"""
        group = JobGroup(
            name=group_data.name,
            description=group_data.description,
            job_ids_list=group_data.job_ids or []
        )
        
        db.add(group)
        db.commit()
        db.refresh(group)
        
        # Update jobs to reference this group
        if group_data.job_ids:
            db.query(Job).filter(Job.id.in_(group_data.job_ids)).update(
                {"group_id": group.id}, synchronize_session=False
            )
            db.commit()
        
        return JobGroupResponse.from_job_group_model(group)
    
    def list_job_groups(self, skip: int, limit: int, db: Session) -> List[JobGroupResponse]:
        """List all job groups"""
        groups = db.query(JobGroup).offset(skip).limit(limit).all()
        return [JobGroupResponse.from_job_group_model(group) for group in groups]
    
    def get_job_group(self, group_id: str, db: Session) -> Optional[JobGroupResponse]:
        """Get a specific job group"""
        group = db.query(JobGroup).filter(JobGroup.id == group_id).first()
        return JobGroupResponse.from_job_group_model(group) if group else None
    
    def update_job_group(self, group_id: str, group_data: JobGroupCreateRequest, db: Session) -> Optional[JobGroupResponse]:
        """Update a job group"""
        group = db.query(JobGroup).filter(JobGroup.id == group_id).first()
        if not group:
            return None
        
        # Remove old job references
        if group.job_ids_list:
            db.query(Job).filter(Job.id.in_(group.job_ids_list)).update(
                {"group_id": None}, synchronize_session=False
            )
        
        # Update group
        group.name = group_data.name
        group.description = group_data.description
        group.job_ids_list = group_data.job_ids or []
        group.updated_at = datetime.now(timezone.utc)
        
        # Add new job references
        if group_data.job_ids:
            db.query(Job).filter(Job.id.in_(group_data.job_ids)).update(
                {"group_id": group_id}, synchronize_session=False
            )
        
        db.commit()
        db.refresh(group)
        
        return JobGroupResponse.from_job_group_model(group)
    
    def delete_job_group(self, group_id: str, db: Session) -> bool:
        """Delete a job group"""
        group = db.query(JobGroup).filter(JobGroup.id == group_id).first()
        if not group:
            return False
        
        # Remove job references
        if group.job_ids_list:
            db.query(Job).filter(Job.id.in_(group.job_ids_list)).update(
                {"group_id": None}, synchronize_session=False
            )
        
        db.delete(group)
        db.commit()
        return True
    
    def add_jobs_to_group(self, group_id: str, job_ids: List[str], db: Session) -> bool:
        """Add jobs to a group"""
        group = db.query(JobGroup).filter(JobGroup.id == group_id).first()
        if not group:
            return False
        
        # Update group's job list
        current_job_ids = set(group.job_ids_list or [])
        new_job_ids = current_job_ids.union(set(job_ids))
        group.job_ids_list = list(new_job_ids)
        
        # Update jobs to reference this group
        db.query(Job).filter(Job.id.in_(job_ids)).update(
            {"group_id": group_id}, synchronize_session=False
        )
        
        db.commit()
        return True
    
    def remove_jobs_from_group(self, group_id: str, job_ids: List[str], db: Session) -> bool:
        """Remove jobs from a group"""
        group = db.query(JobGroup).filter(JobGroup.id == group_id).first()
        if not group:
            return False
        
        # Update group's job list
        if group.job_ids_list:
            group.job_ids_list = [jid for jid in group.job_ids_list if jid not in job_ids]
        
        # Remove group reference from jobs
        db.query(Job).filter(Job.id.in_(job_ids)).update(
            {"group_id": None}, synchronize_session=False
        )
        
        db.commit()
        return True
    
    def get_jobs_in_group(self, group_id: str, skip: int, limit: int, db: Session) -> List[JobResponse]:
        """Get all jobs in a specific group"""
        jobs = db.query(Job).filter(Job.group_id == group_id).offset(skip).limit(limit).all()
        return [JobResponse.from_job_model(job) for job in jobs]