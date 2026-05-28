"""Test extraction and save to database."""

import sys
import os
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_detail_extraction.engine import JobDetailExtractionEngine
from job_detail_extraction.config import create_job_detail_config
from job_detail_extraction.database import JobDetailDatabase


def main():
    """Extract jobs from both sites and save to database."""
    
    # Test URLs that exist in job_listings table
    test_urls = [
        {
            "url": "https://www.mycareersfuture.gov.sg/job/information-technology/ai-engineer-full-stack-developer-iotalents-06fdb1899a115964d985219a2b6c2072",
            "job_role": "AI Engineer",
            "site": "MyCareersFuture"
        },
        {
            "url": "https://www.linkedin.com/jobs/view/4143856014/",
            "job_role": "AI Engineer",
            "site": "LinkedIn"
        }
    ]
    
    logger.info("=" * 80)
    logger.info("EXTRACT AND SAVE TO DATABASE - BOTH SITES")
    logger.info("=" * 80)
    
    # Create database
    database = JobDetailDatabase()
    
    # Create engine with database
    config = create_job_detail_config()
    engine = JobDetailExtractionEngine(config=config, database=database)
    
    results = []
    
    # Extract from both sites
    for i, test_case in enumerate(test_urls, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"Test {i}/{len(test_urls)}: {test_case['site']}")
        logger.info(f"{'='*80}")
        logger.info(f"Extracting from: {test_case['url']}")
        
        result = engine.extract_single_job(
            url=test_case['url'],
            job_role=test_case['job_role']
        )
        results.append(result)
        
        if result.success:
            logger.info(f"\n✓ SUCCESS")
            logger.info(f"  Job Title: {result.job_title}")
            logger.info(f"  Company: {result.company}")
            logger.info(f"  Salary: {result.salary_range}")
            logger.info(f"  Saved to database: job_details table")
        else:
            logger.error(f"\n✗ FAILED: {result.error_message}")
    
    # Get stats
    if database.supabase:
        logger.info(f"\n{'='*80}")
        logger.info("DATABASE STATS")
        logger.info(f"{'='*80}")
        
        # Count successful extractions
        successful = sum(1 for r in results if r.success)
        logger.info(f"Extracted this session: {successful}/{len(results)}")
        
        # Overall stats
        stats = database.get_extraction_stats()
        logger.info(f"Total jobs in DB: {stats.get('total_jobs', 0)}")
        logger.info(f"Total extracted: {stats.get('extracted_jobs', 0)}")


if __name__ == "__main__":
    main()
