"""
Cache Service

Intelligent caching for skill classifications to reduce token usage.
"""
import logging
import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from models.job import Job
from engines.skill_extraction.models import ExtractedSkill

logger = logging.getLogger(__name__)


class CacheStats:
    """Cache statistics"""
    
    def __init__(
        self,
        total_jobs: int = 0,
        cached_jobs: int = 0,
        cache_hit_rate: float = 0.0,
        tokens_saved: int = 0,
        processing_time_saved: float = 0.0
    ):
        self.total_jobs = total_jobs
        self.cached_jobs = cached_jobs
        self.cache_hit_rate = cache_hit_rate
        self.tokens_saved = tokens_saved
        self.processing_time_saved = processing_time_saved
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'total_jobs': self.total_jobs,
            'cached_jobs': self.cached_jobs,
            'cache_hit_rate': self.cache_hit_rate,
            'tokens_saved': self.tokens_saved,
            'processing_time_saved': self.processing_time_saved
        }


class CacheService:
    """Intelligent caching for skill classifications"""
    
    CACHE_VERSION = "1.0"
    MAX_CACHE_AGE_DAYS = 30
    
    # Token estimation constants
    AVG_TOKENS_PER_JOB_EXTRACTION = 500  # Average tokens for skill extraction per job
    AVG_TIME_PER_EXTRACTION = 5.0  # Average seconds per extraction
    
    def __init__(self):
        """Initialize cache service"""
        self.stats = CacheStats()
    
    def get_or_extract_job_skills(
        self,
        job: Job,
        extractor,  # SkillExtractor instance
        db: Session
    ) -> List[ExtractedSkill]:
        """
        Get cached skills or extract fresh
        
        Args:
            job: Job object
            extractor: SkillExtractor instance
            db: Database session
            
        Returns:
            List of ExtractedSkill objects
        """
        # Check if cache is valid
        if self._is_cache_valid(job):
            logger.info(f"Cache HIT for job {job.id} ({job.title})")
            skills = self._load_from_cache(job)
            
            # Update stats
            self.stats.cached_jobs += 1
            self.stats.tokens_saved += self.AVG_TOKENS_PER_JOB_EXTRACTION
            self.stats.processing_time_saved += self.AVG_TIME_PER_EXTRACTION
            
            return skills
        else:
            logger.info(f"Cache MISS for job {job.id} ({job.title}) - extracting skills")
            
            # Extract skills
            skills = extractor.extract_skills(job.description, job.title)
            
            # Save to cache
            self._save_to_cache(job, skills, db)
            
            return skills
    
    def _is_cache_valid(self, job: Job) -> bool:
        """
        Check if cache is valid
        
        Args:
            job: Job object
            
        Returns:
            True if cache is valid, False otherwise
        """
        # Check if cache exists
        if not job.classified_skills:
            logger.debug(f"Job {job.id}: No cached skills")
            return False
        
        # Check version
        if job.classification_version != self.CACHE_VERSION:
            logger.debug(
                f"Job {job.id}: Version mismatch "
                f"(cached: {job.classification_version}, current: {self.CACHE_VERSION})"
            )
            return False
        
        # Check age
        if job.classification_date:
            age = datetime.utcnow() - job.classification_date
            if age.days > self.MAX_CACHE_AGE_DAYS:
                logger.debug(
                    f"Job {job.id}: Cache too old "
                    f"({age.days} days > {self.MAX_CACHE_AGE_DAYS} days)"
                )
                return False
        else:
            logger.debug(f"Job {job.id}: No classification date")
            return False
        
        logger.debug(f"Job {job.id}: Cache is valid")
        return True
    
    def _load_from_cache(self, job: Job) -> List[ExtractedSkill]:
        """
        Load skills from cache
        
        Args:
            job: Job object
            
        Returns:
            List of ExtractedSkill objects
        """
        try:
            skills_data = json.loads(job.classified_skills)
            skills = [ExtractedSkill.from_dict(skill_dict) for skill_dict in skills_data]
            logger.info(f"Loaded {len(skills)} skills from cache for job {job.id}")
            return skills
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to load skills from cache for job {job.id}: {e}")
            return []
    
    def _save_to_cache(
        self,
        job: Job,
        skills: List[ExtractedSkill],
        db: Session
    ):
        """
        Save skills to cache
        
        Args:
            job: Job object
            skills: List of ExtractedSkill objects
            db: Database session
        """
        try:
            # Convert skills to dict format
            skills_data = [skill.dict() for skill in skills]
            
            # Save to job
            job.classified_skills = json.dumps(skills_data)
            job.classification_date = datetime.utcnow()
            job.classification_version = self.CACHE_VERSION
            
            # Commit to database
            db.commit()
            
            logger.info(f"Saved {len(skills)} skills to cache for job {job.id}")
            
        except Exception as e:
            logger.error(f"Failed to save skills to cache for job {job.id}: {e}")
            db.rollback()
    
    def get_cache_stats(self, total_jobs: int) -> CacheStats:
        """
        Get caching statistics
        
        Args:
            total_jobs: Total number of jobs processed
            
        Returns:
            CacheStats object
        """
        self.stats.total_jobs = total_jobs
        
        if total_jobs > 0:
            self.stats.cache_hit_rate = self.stats.cached_jobs / total_jobs
        else:
            self.stats.cache_hit_rate = 0.0
        
        return self.stats
    
    def invalidate_cache(self, job_ids: List[str], db: Session):
        """
        Invalidate cache for specific jobs
        
        Args:
            job_ids: List of job IDs to invalidate
            db: Database session
        """
        try:
            for job_id in job_ids:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.classified_skills = None
                    job.classification_date = None
                    job.classification_version = None
                    logger.info(f"Invalidated cache for job {job_id}")
            
            db.commit()
            logger.info(f"Invalidated cache for {len(job_ids)} jobs")
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            db.rollback()
    
    def invalidate_all_cache(self, db: Session):
        """
        Invalidate all cached skills
        
        Args:
            db: Database session
        """
        try:
            jobs = db.query(Job).filter(Job.classified_skills.isnot(None)).all()
            
            for job in jobs:
                job.classified_skills = None
                job.classification_date = None
                job.classification_version = None
            
            db.commit()
            logger.info(f"Invalidated cache for all {len(jobs)} jobs")
            
        except Exception as e:
            logger.error(f"Failed to invalidate all cache: {e}")
            db.rollback()
    
    def get_cache_summary(self, db: Session) -> dict:
        """
        Get summary of cache status
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with cache summary
        """
        try:
            total_jobs = db.query(Job).count()
            cached_jobs = db.query(Job).filter(
                Job.classified_skills.isnot(None)
            ).count()
            
            # Count by version
            current_version_jobs = db.query(Job).filter(
                Job.classification_version == self.CACHE_VERSION
            ).count()
            
            # Count expired cache
            expired_jobs = 0
            if cached_jobs > 0:
                jobs_with_cache = db.query(Job).filter(
                    Job.classified_skills.isnot(None)
                ).all()
                
                for job in jobs_with_cache:
                    if job.classification_date:
                        age = datetime.utcnow() - job.classification_date
                        if age.days > self.MAX_CACHE_AGE_DAYS:
                            expired_jobs += 1
            
            return {
                'total_jobs': total_jobs,
                'cached_jobs': cached_jobs,
                'current_version_jobs': current_version_jobs,
                'expired_jobs': expired_jobs,
                'cache_version': self.CACHE_VERSION,
                'max_cache_age_days': self.MAX_CACHE_AGE_DAYS,
                'cache_coverage': cached_jobs / total_jobs if total_jobs > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache summary: {e}")
            return {
                'error': str(e)
            }
