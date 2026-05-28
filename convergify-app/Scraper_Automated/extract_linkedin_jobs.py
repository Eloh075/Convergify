"""Extract job details for LinkedIn jobs with anti-bot stealth measures."""

import sys
import os
import time
import random
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_detail_extraction.engine import JobDetailExtractionEngine
from job_detail_extraction.database import JobDetailDatabase
from job_detail_extraction.config import create_job_detail_config


# LinkedIn Anti-Bot Stealth Configuration
BATCH_SIZE = 25  # Process 25-50 jobs per batch
BATCH_BREAK_MIN = 5 * 60  # 5 minutes in seconds
BATCH_BREAK_MAX = 10 * 60  # 10 minutes in seconds
DAILY_LIMIT = 300  # Max 150-300 requests per day (increased to 300)


def main():
    """Extract LinkedIn jobs with anti-bot stealth measures."""
    logger.info("=" * 80)
    logger.info("LinkedIn Job Detail Extraction - Stealth Mode")
    logger.info("=" * 80)
    logger.info(f"Batch size: {BATCH_SIZE} jobs")
    logger.info(f"Batch break: {BATCH_BREAK_MIN//60}-{BATCH_BREAK_MAX//60} minutes")
    logger.info(f"Daily limit: {DAILY_LIMIT} jobs")
    logger.info("=" * 80)
    
    # Create configuration
    config = create_job_detail_config()
    
    # Create database connection
    database = JobDetailDatabase()
    
    # Get total jobs to extract
    all_jobs = database.get_jobs_to_extract(limit=DAILY_LIMIT, website="LinkedIn")
    total_jobs = len(all_jobs)
    
    if total_jobs == 0:
        logger.info("No LinkedIn jobs need extraction")
        return
    
    logger.info(f"Found {total_jobs} LinkedIn jobs to extract")
    logger.info(f"Will process up to {min(total_jobs, DAILY_LIMIT)} jobs today")
    
    # Limit to daily ceiling
    jobs_today = all_jobs[:DAILY_LIMIT]
    
    # Split into batches
    batches = [jobs_today[i:i + BATCH_SIZE] for i in range(0, len(jobs_today), BATCH_SIZE)]
    
    logger.info(f"Split into {len(batches)} batches")
    
    total_processed = 0
    total_successful = 0
    total_failed = 0
    
    for batch_num, batch in enumerate(batches, 1):
        logger.info("=" * 80)
        logger.info(f"BATCH {batch_num}/{len(batches)} - Processing {len(batch)} jobs")
        logger.info("=" * 80)
        
        # Create engine for this batch
        engine = JobDetailExtractionEngine(config=config, database=database)
        
        # Extract batch
        results = engine.extract_batch(batch)
        
        # Update stats
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_processed += len(results)
        total_successful += successful
        total_failed += failed
        
        logger.info(f"Batch {batch_num} complete: {successful} successful, {failed} failed")
        logger.info(f"Total progress: {total_processed}/{len(jobs_today)} jobs")
        
        # Take a coffee break between batches (except after last batch)
        if batch_num < len(batches):
            break_duration = random.randint(BATCH_BREAK_MIN, BATCH_BREAK_MAX)
            break_minutes = break_duration / 60
            logger.info("=" * 80)
            logger.info(f"☕ COFFEE BREAK - Pausing for {break_minutes:.1f} minutes")
            logger.info(f"Next batch will start at approximately {time.strftime('%H:%M:%S', time.localtime(time.time() + break_duration))}")
            logger.info("=" * 80)
            time.sleep(break_duration)
    
    # Final report
    logger.info("=" * 80)
    logger.info("EXTRACTION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total processed: {total_processed}")
    logger.info(f"Successful: {total_successful}")
    logger.info(f"Failed: {total_failed}")
    logger.info(f"Success rate: {(total_successful/total_processed*100):.2f}%")
    logger.info("=" * 80)
    
    # Check remaining jobs
    remaining = database.get_jobs_to_extract(limit=10000, website="LinkedIn")
    logger.info(f"Remaining LinkedIn jobs: {len(remaining)}")
    
    if len(remaining) > 0:
        logger.info("⚠️  Run this script again tomorrow to continue extraction")
        logger.info("   (LinkedIn daily limit: 150-300 requests per IP)")


if __name__ == "__main__":
    main()
