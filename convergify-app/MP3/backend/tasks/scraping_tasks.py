"""
Celery tasks for job scraping operations
"""
from celery import current_task
from celery.exceptions import Retry
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone

from celery_app import celery_app
from adapters.job_scraping_adapter import JobScrapingAdapter
from database import SessionLocal
from models import Job, JobGroup
from services.celery_service import CeleryService

logger = logging.getLogger(__name__)

# Initialize adapters
job_scraping_adapter = JobScrapingAdapter()
celery_service = CeleryService()

@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def scrape_jobs_task(self, scraping_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scrape jobs based on configuration
    
    Args:
        scraping_config: Configuration for job scraping
        
    Returns:
        Dictionary containing scraping results
    """
    import asyncio
    
    try:
        search_terms = scraping_config.get('search_terms', ['developer'])
        employment_type = scraping_config.get('employment_type', 'full-time')
        max_jobs = scraping_config.get('max_jobs', 10)
        
        logger.info(f"Starting job scraping: {search_terms}, {employment_type}, max: {max_jobs}")
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 5, 'total': 100, 'status': 'Initializing job scraping...'}
        )
        
        # Perform scraping using adapter (run async function in event loop)
        scraping_result = asyncio.run(job_scraping_adapter.scrape_jobs(scraping_config))
        
        if not scraping_result.get('success'):
            raise Exception(f"Scraping failed: {scraping_result.get('error', 'Unknown error')}")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 80, 'total': 100, 'status': 'Saving scraped jobs to database...'}
        )
        
        # Save jobs to database
        db = SessionLocal()
        try:
            saved_jobs = []
            scraped_jobs = scraping_result.get('jobs', [])
            
            for job_data in scraped_jobs:
                # Create job record
                job = Job(
                    title=job_data.get('title', ''),
                    company=job_data.get('company', ''),
                    description=job_data.get('description', ''),
                    requirements=job_data.get('requirements', []),
                    location=job_data.get('location', ''),
                    salary_min=job_data.get('salary_min'),
                    salary_max=job_data.get('salary_max'),
                    source=job_data.get('source', 'scraped'),
                    scraped_date=datetime.now(timezone.utc),
                    skills_list=job_data.get('required_skills', [])
                )
                
                db.add(job)
                saved_jobs.append(job)
            
            db.commit()
            
            # Refresh to get IDs
            for job in saved_jobs:
                db.refresh(job)
            
            # Create job group for this scraping session
            scraping_job_id = scraping_result.get('scraping_job_id', 'unknown')
            job_group = JobGroup(
                name=f"Scraped Jobs - {search_terms[0]} ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
                description=f"Jobs scraped for '{search_terms[0]}' on {datetime.now().strftime('%Y-%m-%d')}",
                job_ids_list=[job.id for job in saved_jobs]
            )
            
            db.add(job_group)
            db.commit()
            db.refresh(job_group)
            
            # Update jobs with group ID
            for job in saved_jobs:
                job.group_id = job_group.id
            db.commit()
            
            # Prepare final result
            final_result = {
                'success': True,
                'scraping_job_id': scraping_job_id,
                'job_group_id': job_group.id,
                'jobs_saved': len(saved_jobs),
                'job_ids': [job.id for job in saved_jobs],
                'metadata': scraping_result.get('metadata', {}),
                'statistics': scraping_result.get('statistics', {})
            }
            
            # Update task status in database
            celery_service.update_task_status(
                self.request.id, 'SUCCESS', final_result, db=db
            )
            
        finally:
            db.close()
        
        # Final progress update
        self.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': f'Scraping completed - {len(scraped_jobs)} jobs saved'}
        )
        
        logger.info(f"Job scraping completed: {len(scraped_jobs)} jobs saved")
        return final_result
        
    except Exception as e:
        logger.error(f"Job scraping task failed: {e}")
        
        # Update database with error
        db = SessionLocal()
        try:
            celery_service.update_task_status(
                self.request.id, 'FAILURE', error=str(e), db=db
            )
        finally:
            db.close()
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job scraping (attempt {self.request.retries + 1})")
            raise self.retry(countdown=300 * (2 ** self.request.retries))
        
        raise

@celery_app.task(bind=True, max_retries=1, default_retry_delay=120)
def validate_scraped_jobs(self, job_ids: List[str]) -> Dict[str, Any]:
    """
    Validate scraped job data quality
    
    Args:
        job_ids: List of job IDs to validate
        
    Returns:
        Dictionary containing validation results
    """
    try:
        logger.info(f"Starting validation for {len(job_ids)} scraped jobs")
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Loading jobs for validation...'}
        )
        
        db = SessionLocal()
        try:
            jobs = db.query(Job).filter(Job.id.in_(job_ids)).all()
            
            if not jobs:
                raise ValueError(f"No jobs found for validation")
            
            validation_results = []
            valid_jobs = 0
            invalid_jobs = 0
            
            for i, job in enumerate(jobs):
                # Update progress
                progress = 10 + int((i / len(jobs)) * 80)
                self.update_state(
                    state='PROGRESS',
                    meta={'current': progress, 'total': 100, 'status': f'Validating job {i+1}/{len(jobs)}...'}
                )
                
                # Convert job to dict for validation
                job_data = {
                    'title': job.title,
                    'company': job.company,
                    'description': job.description,
                    'location': job.location,
                    'required_skills': job.skills_list,
                    'employment_type': 'full-time',  # Default
                    'salary_min': job.salary_min,
                    'salary_max': job.salary_max,
                    'data_completeness_score': 0.8,  # Mock score
                    'extraction_confidence': 0.7     # Mock confidence
                }
                
                # Validate using adapter (run async function in event loop)
                validation_result = asyncio.run(job_scraping_adapter.validate_job_data(job_data))
                
                validation_results.append({
                    'job_id': job.id,
                    'job_title': job.title,
                    'valid': validation_result['valid'],
                    'errors': validation_result['errors'],
                    'warnings': validation_result['warnings'],
                    'quality_score': validation_result['quality_score'],
                    'confidence_score': validation_result['confidence_score']
                })
                
                if validation_result['valid']:
                    valid_jobs += 1
                else:
                    invalid_jobs += 1
            
            # Compile final results
            final_result = {
                'success': True,
                'total_jobs_validated': len(jobs),
                'valid_jobs': valid_jobs,
                'invalid_jobs': invalid_jobs,
                'validation_rate': valid_jobs / len(jobs) if jobs else 0,
                'validation_results': validation_results,
                'summary': {
                    'average_quality_score': sum(r['quality_score'] for r in validation_results) / len(validation_results) if validation_results else 0,
                    'average_confidence_score': sum(r['confidence_score'] for r in validation_results) / len(validation_results) if validation_results else 0,
                    'common_errors': self._analyze_common_errors(validation_results),
                    'common_warnings': self._analyze_common_warnings(validation_results)
                }
            }
            
            # Update task status in database
            celery_service.update_task_status(
                self.request.id, 'SUCCESS', final_result, db=db
            )
            
        finally:
            db.close()
        
        # Final progress update
        self.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': f'Validation completed - {valid_jobs}/{len(jobs)} jobs valid'}
        )
        
        logger.info(f"Job validation completed: {valid_jobs}/{len(jobs)} jobs valid")
        return final_result
        
    except Exception as e:
        logger.error(f"Job validation task failed: {e}")
        
        # Update database with error
        db = SessionLocal()
        try:
            celery_service.update_task_status(
                self.request.id, 'FAILURE', error=str(e), db=db
            )
        finally:
            db.close()
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job validation (attempt {self.request.retries + 1})")
            raise self.retry(countdown=120)
        
        raise

@celery_app.task(bind=True, max_retries=1, default_retry_delay=60)
def enrich_job_data(self, job_ids: List[str]) -> Dict[str, Any]:
    """
    Enrich job data with additional analysis
    
    Args:
        job_ids: List of job IDs to enrich
        
    Returns:
        Dictionary containing enrichment results
    """
    try:
        logger.info(f"Starting data enrichment for {len(job_ids)} jobs")
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Loading jobs for enrichment...'}
        )
        
        db = SessionLocal()
        try:
            jobs = db.query(Job).filter(Job.id.in_(job_ids)).all()
            
            if not jobs:
                raise ValueError(f"No jobs found for enrichment")
            
            enriched_jobs = 0
            enrichment_results = []
            
            # Import skill extraction adapter for enrichment
            from adapters.skill_extraction_adapter import SkillExtractionAdapter
            skill_adapter = SkillExtractionAdapter()
            
            for i, job in enumerate(jobs):
                # Update progress
                progress = 10 + int((i / len(jobs)) * 80)
                self.update_state(
                    state='PROGRESS',
                    meta={'current': progress, 'total': 100, 'status': f'Enriching job {i+1}/{len(jobs)}...'}
                )
                
                try:
                    # Extract skills if not already done
                    if not job.skills_list:
                        skill_result = asyncio.run(skill_adapter.extract_from_job(
                            job.description, job.id, job.title, job.company
                        ))
                        
                        if skill_result.get('success'):
                            skills = [skill['name'] for skill in skill_result.get('skills', [])]
                            job.skills_list = skills
                            enriched_jobs += 1
                    
                    enrichment_results.append({
                        'job_id': job.id,
                        'job_title': job.title,
                        'enriched': True,
                        'skills_extracted': len(job.skills_list or []),
                        'enrichment_type': 'skill_extraction'
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to enrich job {job.id}: {e}")
                    enrichment_results.append({
                        'job_id': job.id,
                        'job_title': job.title,
                        'enriched': False,
                        'error': str(e)
                    })
            
            # Commit all changes
            db.commit()
            
            # Compile final results
            final_result = {
                'success': True,
                'total_jobs_processed': len(jobs),
                'jobs_enriched': enriched_jobs,
                'enrichment_rate': enriched_jobs / len(jobs) if jobs else 0,
                'enrichment_results': enrichment_results,
                'summary': {
                    'total_skills_extracted': sum(r.get('skills_extracted', 0) for r in enrichment_results),
                    'average_skills_per_job': sum(r.get('skills_extracted', 0) for r in enrichment_results) / len(enrichment_results) if enrichment_results else 0
                }
            }
            
            # Update task status in database
            celery_service.update_task_status(
                self.request.id, 'SUCCESS', final_result, db=db
            )
            
        finally:
            db.close()
        
        # Final progress update
        self.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': f'Enrichment completed - {enriched_jobs}/{len(jobs)} jobs enriched'}
        )
        
        logger.info(f"Job enrichment completed: {enriched_jobs}/{len(jobs)} jobs enriched")
        return final_result
        
    except Exception as e:
        logger.error(f"Job enrichment task failed: {e}")
        
        # Update database with error
        db = SessionLocal()
        try:
            celery_service.update_task_status(
                self.request.id, 'FAILURE', error=str(e), db=db
            )
        finally:
            db.close()
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job enrichment (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60)
        
        raise

def _analyze_common_errors(validation_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze common validation errors"""
    error_counts = {}
    
    for result in validation_results:
        for error in result.get('errors', []):
            if error in error_counts:
                error_counts[error] += 1
            else:
                error_counts[error] = 1
    
    # Return top 5 most common errors
    common_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return [{'error': error, 'count': count} for error, count in common_errors]

def _analyze_common_warnings(validation_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze common validation warnings"""
    warning_counts = {}
    
    for result in validation_results:
        for warning in result.get('warnings', []):
            if warning in warning_counts:
                warning_counts[warning] += 1
            else:
                warning_counts[warning] = 1
    
    # Return top 5 most common warnings
    common_warnings = sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return [{'warning': warning, 'count': count} for warning, count in common_warnings]