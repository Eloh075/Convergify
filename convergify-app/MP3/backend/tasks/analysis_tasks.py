"""
Celery tasks for career analysis processing
"""
from celery import current_task
from celery.exceptions import Retry
from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime, timezone

from celery_app import celery_app
from adapters.skill_extraction_adapter import SkillExtractionAdapter
from adapters.skill_classification_adapter import SkillClassificationAdapter
from adapters.career_analysis_adapter import CareerAnalysisAdapter
from database import SessionLocal
from models import Resume, Job, Analysis
from services.celery_service import CeleryService

logger = logging.getLogger(__name__)

# Initialize adapters
skill_extraction_adapter = SkillExtractionAdapter()
skill_classification_adapter = SkillClassificationAdapter()
career_analysis_adapter = CareerAnalysisAdapter()
celery_service = CeleryService()

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def extract_skills_from_resume(self, resume_id: str, resume_text: str) -> Dict[str, Any]:
    """
    Extract skills from resume text
    
    Args:
        resume_id: Resume ID for tracking
        resume_text: Resume text content
        
    Returns:
        Dictionary containing extracted skills and metadata
    """
    try:
        logger.info(f"Starting skill extraction for resume {resume_id}")
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Extracting skills from resume...'}
        )
        
        # Extract skills using adapter (run async function in event loop)
        result = asyncio.run(skill_extraction_adapter.extract_from_resume(resume_text, resume_id))
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 80, 'total': 100, 'status': 'Processing extraction results...'}
        )
        
        # Update database with extracted skills
        db = SessionLocal()
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if resume and result.get('success'):
                skills = [skill['name'] for skill in result.get('skills', [])]
                resume.skills_list = skills
                resume.analysis_status = 'skills_extracted'
                db.commit()
                
                # Update task status in database
                celery_service.update_task_status(
                    self.request.id, 'SUCCESS', result, db=db
                )
        finally:
            db.close()
        
        # Final progress update
        self.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Skill extraction completed'}
        )
        
        logger.info(f"Skill extraction completed for resume {resume_id}")
        return result
        
    except Exception as e:
        logger.error(f"Skill extraction failed for resume {resume_id}: {e}")
        
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
            logger.info(f"Retrying skill extraction for resume {resume_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        raise

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def classify_skills(self, skills: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Classify skills into categories
    
    Args:
        skills: List of skill names to classify
        context: Optional context information
        
    Returns:
        Dictionary containing classified skills
    """
    try:
        logger.info(f"Starting skill classification for {len(skills)} skills")
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': 'Classifying skills...'}
        )
        
        # Classify skills using adapter (run async function in event loop)
        result = asyncio.run(skill_classification_adapter.classify_skills(skills, context))
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Processing classification results...'}
        )
        
        # Update task status in database
        db = SessionLocal()
        try:
            celery_service.update_task_status(
                self.request.id, 'SUCCESS', result, db=db
            )
        finally:
            db.close()
        
        # Final progress update
        self.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Skill classification completed'}
        )
        
        logger.info(f"Skill classification completed for {len(skills)} skills")
        return result
        
    except Exception as e:
        logger.error(f"Skill classification failed: {e}")
        
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
            logger.info(f"Retrying skill classification (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        raise

@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def analyze_career_path(self, profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze career path and generate recommendations
    
    Args:
        profile: Dictionary containing resume and analysis parameters
        
    Returns:
        Dictionary containing career analysis results
    """
    try:
        analysis_type = profile.get('analysis_type', 'career_guidance')
        logger.info(f"Starting career path analysis: {analysis_type}")
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 15, 'total': 100, 'status': 'Initializing career analysis...'}
        )
        
        # Perform career analysis using adapter (run async function in event loop)
        result = asyncio.run(career_analysis_adapter.analyze_career_path(profile))
        
        # Update progress based on analysis type
        if analysis_type == 'single_job':
            self.update_state(
                state='PROGRESS',
                meta={'current': 70, 'total': 100, 'status': 'Analyzing job fit...'}
            )
        elif analysis_type == 'sector_analysis':
            self.update_state(
                state='PROGRESS',
                meta={'current': 60, 'total': 100, 'status': 'Analyzing sector alignment...'}
            )
        else:
            self.update_state(
                state='PROGRESS',
                meta={'current': 65, 'total': 100, 'status': 'Generating career guidance...'}
            )
        
        # Update database if analysis_id provided
        analysis_id = profile.get('analysis_id')
        if analysis_id and result.get('success'):
            db = SessionLocal()
            try:
                analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
                if analysis:
                    analysis.results_dict = result
                    analysis.mark_completed()
                    db.commit()
                    
                    # Update task status in database
                    celery_service.update_task_status(
                        self.request.id, 'SUCCESS', result, db=db
                    )
            finally:
                db.close()
        
        # Final progress update
        self.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Career analysis completed'}
        )
        
        logger.info(f"Career path analysis completed: {analysis_type}")
        return result
        
    except Exception as e:
        logger.error(f"Career path analysis failed: {e}")
        
        # Update database with error
        analysis_id = profile.get('analysis_id')
        if analysis_id:
            db = SessionLocal()
            try:
                analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
                if analysis:
                    analysis.mark_failed(str(e))
                    db.commit()
                
                celery_service.update_task_status(
                    self.request.id, 'FAILURE', error=str(e), db=db
                )
            finally:
                db.close()
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying career analysis (attempt {self.request.retries + 1})")
            raise self.retry(countdown=120 * (2 ** self.request.retries))
        
        raise

@celery_app.task(bind=True, max_retries=2, default_retry_delay=180)
def comprehensive_analysis(self, resume_id: str, job_ids: List[str], 
                          analysis_type: str = 'comprehensive') -> Dict[str, Any]:
    """
    Perform comprehensive analysis combining multiple engines
    
    Args:
        resume_id: Resume ID to analyze
        job_ids: List of job IDs to analyze against
        analysis_type: Type of analysis to perform
        
    Returns:
        Dictionary containing comprehensive analysis results
    """
    try:
        logger.info(f"Starting comprehensive analysis for resume {resume_id} against {len(job_ids)} jobs")
        
        # Calculate total steps dynamically based on jobs needing processing
        db = SessionLocal()
        
        try:
            # Step 1: Load resume and job data
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': 5,
                    'total': 100,
                    'status': 'Loading resume and job data...',
                    'stage': 'initialization'
                }
            )
            
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            jobs = db.query(Job).filter(Job.id.in_(job_ids)).all()
            
            if not resume:
                raise ValueError(f"Resume {resume_id} not found")
            if not jobs:
                raise ValueError(f"No jobs found for IDs: {job_ids}")
            
            # Step 2: Extract skills from resume if not already done
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': 15,
                    'total': 100,
                    'status': 'Extracting skills from resume...',
                    'stage': 'resume_processing'
                }
            )
            
            if not resume.skills_list:
                skill_result = asyncio.run(skill_extraction_adapter.extract_from_resume(
                    resume.original_text, resume_id
                ))
                if skill_result.get('success'):
                    skills = [skill['name'] for skill in skill_result.get('skills', [])]
                    resume.skills_list = skills
                    db.commit()
            
            # Step 3: Process jobs - extract skills if needed
            total_jobs = len(jobs)
            jobs_needing_processing = [job for job in jobs if not job.skills_processed or not job.skills_list]
            
            logger.info(f"Jobs needing skill extraction: {len(jobs_needing_processing)}/{total_jobs}")
            
            job_skills = {}
            for idx, job in enumerate(jobs, 1):
                # Check if job needs skill extraction
                if not job.skills_processed or not job.skills_list:
                    progress = 15 + int((idx / total_jobs) * 30)  # 15-45% range
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': progress,
                            'total': 100,
                            'status': f'Processing job {idx}/{total_jobs} - Extracting skills from "{job.title}"...',
                            'stage': 'job_processing',
                            'jobs_processed': idx,
                            'total_jobs': total_jobs
                        }
                    )
                    
                    # Extract skills from job description
                    job_skill_result = asyncio.run(skill_extraction_adapter.extract_from_job(
                        job.description, job.id, job.title, job.company
                    ))
                    
                    if job_skill_result.get('success'):
                        skills = [skill['name'] for skill in job_skill_result.get('skills', [])]
                        job.skills_list = skills
                        job.skills_processed = True
                        db.commit()
                        logger.info(f"Extracted {len(skills)} skills from job: {job.title}")
                else:
                    logger.info(f"Job already processed, using existing skills: {job.title}")
                
                job_skills[job.id] = job.skills_list or []
            
            # Step 4: Classify all skills
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': 50,
                    'total': 100,
                    'status': 'Classifying skills into categories...',
                    'stage': 'skill_classification'
                }
            )
            
            all_skills = set(resume.skills_list or [])
            for skills in job_skills.values():
                all_skills.update(skills)
            
            logger.info(f"Classifying {len(all_skills)} unique skills")
            
            classification_result = asyncio.run(skill_classification_adapter.classify_skills(
                list(all_skills)
            ))
            
            # Step 5: Perform strategic career analysis
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': 70,
                    'total': 100,
                    'status': 'Performing strategic career analysis...',
                    'stage': 'career_analysis'
                }
            )
            
            # Prepare profile for career analysis
            profile = {
                'resume_text': resume.original_text,
                'analysis_type': 'single_job' if len(jobs) == 1 else 'market_intelligence',
                'resume_id': resume_id,
                'job_ids': job_ids
            }
            
            if len(jobs) == 1:
                # Single job analysis
                job = jobs[0]
                profile['job_data'] = {
                    'job_title': job.title,
                    'company': job.company,
                    'description': job.description,
                    'required_skills': job.skills_list or [],
                    'location': job.location
                }
                profile['job_id'] = job.id
                logger.info(f"Running single job analysis for: {job.title}")
            else:
                # Group/market intelligence analysis
                profile['jobs_data'] = [
                    {
                        'job_id': job.id,
                        'job_title': job.title,
                        'company': job.company,
                        'description': job.description,
                        'required_skills': job.skills_list or [],
                        'location': job.location
                    }
                    for job in jobs
                ]
                logger.info(f"Running market intelligence analysis for {len(jobs)} jobs")
            
            career_result = asyncio.run(career_analysis_adapter.analyze_career_path(profile))
            
            # Step 6: Compile comprehensive results
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': 90,
                    'total': 100,
                    'status': 'Compiling comprehensive results...',
                    'stage': 'finalization'
                }
            )
            
            comprehensive_result = {
                'success': True,
                'analysis_type': analysis_type,
                'resume_id': resume_id,
                'job_ids': job_ids,
                'resume_skills': resume.skills_list or [],
                'job_skills': job_skills,
                'skill_classification': classification_result,
                'career_analysis': career_result,
                'metadata': {
                    'total_resume_skills': len(resume.skills_list or []),
                    'total_job_skills': sum(len(skills) for skills in job_skills.values()),
                    'total_unique_skills': len(all_skills),
                    'jobs_processed': len(jobs_needing_processing),
                    'analysis_completed_at': datetime.now(timezone.utc).isoformat(),
                    'analysis_mode': 'single_job' if len(jobs) == 1 else 'market_intelligence'
                }
            }
            
            # Update task status in database
            celery_service.update_task_status(
                self.request.id, 'SUCCESS', comprehensive_result, db=db
            )
            
        finally:
            db.close()
        
        # Final progress update
        self.update_state(
            state='SUCCESS',
            meta={
                'current': 100,
                'total': 100,
                'status': 'Analysis complete!',
                'stage': 'completed'
            }
        )
        
        logger.info(f"Comprehensive analysis completed for resume {resume_id}")
        return comprehensive_result
        
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        
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
            logger.info(f"Retrying comprehensive analysis (attempt {self.request.retries + 1})")
            raise self.retry(countdown=180 * (2 ** self.request.retries))
        
        raise

@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def generate_optimized_resume(self, resume_id: str, analysis_results: Dict[str, Any], 
                            target_job_ids: List[str] = None) -> Dict[str, Any]:
    """
    Generate optimized resume based on analysis results using OptimizationService
    
    Args:
        resume_id: Original resume ID
        analysis_results: Results from career analysis
        target_job_ids: List of job IDs this optimization targets
        
    Returns:
        Dictionary containing optimized resume information
    """
    try:
        logger.info(f"Starting resume optimization for resume {resume_id}")
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': 'Initializing optimization service...'}
        )
        
        db = SessionLocal()
        try:
            # Initialize optimization service
            from services.optimization_service import OptimizationService
            optimization_service = OptimizationService()
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'current': 40, 'total': 100, 'status': 'Analyzing optimization opportunities...'}
            )
            
            # Extract target job IDs from analysis results if not provided
            if not target_job_ids:
                target_job_ids = analysis_results.get('job_ids', [])
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'current': 60, 'total': 100, 'status': 'Generating optimized content...'}
            )
            
            # Generate optimized resume using the service
            result = optimization_service.generate_optimized_resume(
                resume_id=resume_id,
                analysis_results=analysis_results,
                target_job_ids=target_job_ids,
                db=db
            )
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'current': 90, 'total': 100, 'status': 'Finalizing optimization...'}
            )
            
            # Add task-specific metadata
            result.update({
                'success': True,
                'task_id': self.request.id,
                'original_resume_id': resume_id,
                'target_job_ids': target_job_ids
            })
            
            # Update task status in database
            celery_service.update_task_status(
                self.request.id, 'SUCCESS', result, db=db
            )
            
        finally:
            db.close()
        
        # Final progress update
        self.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Resume optimization completed'}
        )
        
        logger.info(f"Resume optimization completed for resume {resume_id}")
        return result
        
    except Exception as e:
        logger.error(f"Resume optimization failed: {e}")
        
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
            logger.info(f"Retrying resume optimization (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        raise