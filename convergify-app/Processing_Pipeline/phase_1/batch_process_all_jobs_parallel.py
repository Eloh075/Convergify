"""
Parallel Batch Processing - Process all jobs using thread pool with 7 workers

This version uses parallel processing to significantly speed up job processing:
- 7 worker threads process jobs concurrently
- Single database writer thread handles all writes
- Automatic API key rotation with circuit breaker
- Real-time monitoring and progress tracking

Expected speedup: 3.5-4x faster than sequential processing
"""
import sys
import os
import time
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from Scraper_Automated folder
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Scraper_Automated", ".env")
load_dotenv(env_path)

from supabase import create_client
from Processing_Pipeline.phase_1.parallel_processor import ParallelProcessor, ProcessingResult
from Processing_Pipeline.phase_1.config import PipelineConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)


def process_job_task(client, job_data: dict) -> dict:
    """
    Process a single job using the LLM
    
    Args:
        client: GeminiClient instance (with specific API key)
        job_data: Dictionary with job information
        
    Returns:
        Dictionary with classification and skills
    """
    from Processing_Pipeline.phase_1.job_processor import JobProcessor
    
    # Use the client's API key by passing it to JobProcessor
    processor = JobProcessor(gemini_api_key=client.api_key)
    
    result = processor.process_job(
        url=job_data['url'],
        job_title=job_data['job_title'],
        job_description=job_data.get('description', ''),
        job_role=job_data.get('job_role'),
        job_sector=None
    )
    
    return {
        'success': result.success,
        'url': result.url,
        'job_title': result.job_title,
        'classification': {
            'job_role': result.classification.job_role,
            'experience_level': result.classification.experience_level,
            'role_sub_cluster': result.classification.role_sub_cluster,
            'cluster_type': result.classification.cluster_type,
            'classification_confidence': result.classification.classification_confidence,
            'job_sector': result.classification.job_sector
        },
        'skills': [
            {
                'skill_name': s.skill_name,
                'confidence': s.confidence,
                'evidence': s.evidence,
                'category_hint': s.category_hint
            }
            for s in result.skills
        ],
        'error_message': result.error_message
    }


def write_job_result_to_db(supabase, result: ProcessingResult):
    """
    Write job processing result to database
    
    Args:
        supabase: Supabase client
        result: ProcessingResult from parallel processor
    """
    try:
        data = result.data
        
        if not data.get('success'):
            # Mark job as NOT processed (so it can be retried) but log the error
            supabase.table("job_details").update({
                "processed": False,
                "processed_at": None,
                "error_message": data.get('error_message', 'Unknown error')
            }).eq("url", data['url']).execute()
            
            logger.error(f"✗ {data['job_title'][:40]}... - Failed: {data.get('error_message', 'No error')[:80]}")
            return
        
        # Save classification
        supabase.table("job_classifications").upsert({
            "url": data['url'],
            "job_title": data['job_title'],
            "job_role": data['classification']['job_role'],
            "experience_level": data['classification']['experience_level'],
            "role_sub_cluster": data['classification']['role_sub_cluster'],
            "cluster_type": data['classification']['cluster_type'],
            "classification_confidence": data['classification']['classification_confidence'],
            "job_sector": data['classification']['job_sector']
        }).execute()
        
        # Save skills
        for skill in data['skills']:
            supabase.table("job_skills").insert({
                "url": data['url'],
                "skill_name": skill['skill_name'],
                "confidence": skill['confidence'],
                "evidence": skill['evidence'],
                "category_hint": skill['category_hint'],
                "job_role": data['classification']['job_role'],
                "role_sub_cluster": data['classification']['role_sub_cluster'],
                "cluster_type": data['classification']['cluster_type']
            }).execute()
        
        # Mark as processed (clear any previous error_message)
        supabase.table("job_details").update({
            "processed": True,
            "processed_at": datetime.now().isoformat(),
            "error_message": None
        }).eq("url", data['url']).execute()
        
        logger.info(
            f"✓ {data['job_title'][:40]}... "
            f"{data['classification']['experience_level']} | "
            f"{data['classification']['role_sub_cluster'] or 'No cluster'} | "
            f"{len(data['skills'])} skills"
        )
        
    except Exception as e:
        logger.error(f"Database write error for {result.task_id}: {e}")
        
        # Try to mark as NOT processed (so it can be retried) with error
        try:
            supabase.table("job_details").update({
                "processed": False,
                "processed_at": None,
                "error_message": str(e)
            }).eq("url", result.data.get('url', 'unknown')).execute()
        except:
            pass


def main():
    """Parallel batch process all unprocessed jobs"""
    print("=" * 80)
    print("PARALLEL BATCH PROCESSING ALL JOBS - Phase 1")
    print("=" * 80)
    
    # Initialize Supabase client
    supabase = create_client(
        PipelineConfig.SUPABASE_URL,
        PipelineConfig.SUPABASE_KEY
    )
    
    # Get all unprocessed jobs with descriptions
    print("\n📥 Fetching unprocessed jobs...")
    result = supabase.table("job_details")\
        .select("*")\
        .eq("processed", False)\
        .not_.is_("description", "null")\
        .order("url")\
        .execute()
    
    jobs = result.data
    total_jobs = len(jobs)
    
    if total_jobs == 0:
        print("✓ No jobs to process!")
        return
    
    print(f"✓ Found {total_jobs} jobs to process")
    
    # Create tasks for parallel processing
    print("\n📝 Creating tasks...")
    tasks = []
    for job in jobs:
        tasks.append({
            "id": job['url'],
            "data": job,
            "process_func": process_job_task
        })
    print(f"✓ Created {len(tasks)} tasks")
    
    # Initialize parallel processor
    print("\n🚀 Initializing parallel processor...")
    print(f"   Workers: 7")
    print(f"   API Keys: {len(PipelineConfig.GEMINI_API_KEYS)}")
    print(f"   Max retries: 3")
    print(f"   No delay between requests (parallel processing)")
    
    processor = ParallelProcessor(
        num_workers=7,
        max_retries=3
    )
    
    # Process all jobs
    print("\n" + "=" * 80)
    print("STARTING PARALLEL BATCH PROCESSING")
    print("=" * 80)
    
    start_time = time.time()
    
    processor.process_tasks(
        tasks=tasks,
        write_func=lambda r: write_job_result_to_db(supabase, r),
        enable_monitoring=True
    )
    
    elapsed = time.time() - start_time
    
    # Final summary
    print("\n" + "=" * 80)
    print("PARALLEL BATCH PROCESSING COMPLETE")
    print("=" * 80)
    print(f"Total jobs: {total_jobs}")
    print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
    print(f"⚡ Average: {elapsed/total_jobs:.1f} seconds per job")
    print("=" * 80)
    
    # Get stats from database
    print("\n📊 Database Statistics:")
    
    # Count classifications
    exp_result = supabase.table("job_classifications")\
        .select("experience_level", count="exact")\
        .execute()
    print(f"  Total classifications: {len(exp_result.data)}")
    
    # Count skills
    skills_result = supabase.table("job_skills")\
        .select("id", count="exact")\
        .execute()
    print(f"  Total skills extracted: {skills_result.count}")
    
    print("\n✅ Phase 1 complete! Ready for Phase 2 (Skills Normalization)")


if __name__ == "__main__":
    main()
