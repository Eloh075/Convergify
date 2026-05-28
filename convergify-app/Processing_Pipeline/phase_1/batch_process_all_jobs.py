"""
Batch process all jobs through the skills processing pipeline
"""
import sys
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from Scraper_Automated folder
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Scraper_Automated", ".env")
load_dotenv(env_path)

from supabase import create_client
from Processing_Pipeline.phase_1.job_processor import JobProcessor
from Processing_Pipeline.phase_1.config import PipelineConfig



def process_and_save_job(processor, supabase, job, job_num, total_jobs):
    """Process a single job and save to database"""
    url = job['url']
    job_title = job.get('job_title', 'Unknown')
    job_role = job.get('job_role', 'Unknown')
    
    print(f"\n[{job_num}/{total_jobs}] {job_role} | {job_title[:40]}...")
    
    try:
        # Process the job
        result = processor.process_job(
            url=url,
            job_title=job_title,
            job_description=job.get('description', ''),
            job_role=job_role,
            job_sector=None
        )
        
        if result.success:
            # Save classification
            supabase.table("job_classifications").upsert({
                "url": result.url,
                "job_title": result.classification.job_title,
                "job_role": result.classification.job_role,
                "experience_level": result.classification.experience_level,
                "role_sub_cluster": result.classification.role_sub_cluster,
                "cluster_type": result.classification.cluster_type,
                "classification_confidence": result.classification.classification_confidence,
                "job_sector": result.classification.job_sector
            }).execute()
            
            # Save skills
            for skill in result.skills:
                supabase.table("job_skills").insert({
                    "url": result.url,
                    "skill_name": skill.skill_name,
                    "confidence": skill.confidence,
                    "evidence": skill.evidence,
                    "category_hint": skill.category_hint,
                    "job_role": result.classification.job_role,
                    "role_sub_cluster": result.classification.role_sub_cluster,
                    "cluster_type": result.classification.cluster_type
                }).execute()
            
            # Mark as processed
            supabase.table("job_details").update({
                "processed": True,
                "processed_at": datetime.now().isoformat()
            }).eq("url", result.url).execute()
            
            print(f"  ✓ {result.classification.experience_level} | {result.classification.role_sub_cluster or 'No cluster'} | {len(result.skills)} skills")
            return True
            
        else:
            print(f"  ❌ Failed: {result.error_message[:80]}")
            
            # Mark as processed but with error
            supabase.table("job_details").update({
                "processed": True,
                "processed_at": datetime.now().isoformat(),
                "error_message": result.error_message
            }).eq("url", url).execute()
            
            return False
            
    except Exception as e:
        print(f"  ❌ Exception: {str(e)[:80]}")
        
        # Mark as processed but with error
        try:
            supabase.table("job_details").update({
                "processed": True,
                "processed_at": datetime.now().isoformat(),
                "error_message": str(e)
            }).eq("url", url).execute()
        except:
            pass
        
        return False


def main():
    """Batch process all unprocessed jobs"""
    print("=" * 80)
    print("Batch Processing All Jobs - Phase 1")
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
    
    # Initialize processor
    print("\n🤖 Initializing job processor with Gemma 3 12B...")
    processor = JobProcessor()
    
    # Process all jobs
    print("\n" + "=" * 80)
    print("Starting batch processing...")
    print("=" * 80)
    
    start_time = time.time()
    success_count = 0
    fail_count = 0
    
    for i, job in enumerate(jobs, 1):
        success = process_and_save_job(processor, supabase, job, i, total_jobs)
        
        if success:
            success_count += 1
        else:
            fail_count += 1
        
        # Progress update every 10 jobs
        if i % 10 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = (total_jobs - i) * avg_time
            print(f"\n📊 Progress: {i}/{total_jobs} ({i/total_jobs*100:.1f}%) | Success: {success_count} | Failed: {fail_count}")
            print(f"⏱️  Elapsed: {elapsed/60:.1f}m | Est. remaining: {remaining/60:.1f}m")
        
        # 2 second delay between requests
        if i < total_jobs:
            time.sleep(2)
    
    # Final summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 80)
    print(f"Total jobs: {total_jobs}")
    print(f"✅ Successful: {success_count} ({success_count/total_jobs*100:.1f}%)")
    print(f"❌ Failed: {fail_count} ({fail_count/total_jobs*100:.1f}%)")
    print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
    print(f"⚡ Average: {elapsed/total_jobs:.1f} seconds per job")
    print("=" * 80)
    
    # Get stats from database
    print("\n📊 Database Statistics:")
    
    # Count by experience level
    exp_result = supabase.table("job_classifications")\
        .select("experience_level", count="exact")\
        .execute()
    print(f"  Total classifications: {len(exp_result.data)}")
    
    # Count total skills
    skills_result = supabase.table("job_skills")\
        .select("id", count="exact")\
        .execute()
    print(f"  Total skills extracted: {skills_result.count}")
    
    print("\n✅ Phase 1 complete! Ready for Phase 2 (Skills Normalization)")


if __name__ == "__main__":
    main()
