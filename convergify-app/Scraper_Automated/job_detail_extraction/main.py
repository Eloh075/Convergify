"""Main script for job detail extraction."""

import sys
import os
from loguru import logger

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from job_detail_extraction.engine import JobDetailExtractionEngine
from job_detail_extraction.database import JobDetailDatabase
from job_detail_extraction.config import create_job_detail_config


def extract_job_details_from_database(limit: int = 50, website: str = None):
    """Extract job details for jobs in database."""
    logger.info("Starting job detail extraction...")
    
    # Create configuration
    config = create_job_detail_config()
    
    # Create database (in a real scenario, you'd have a Supabase client)
    # For now, we'll create a mock database
    database = JobDetailDatabase()
    
    # Create engine
    engine = JobDetailExtractionEngine(config=config, database=database)
    
    # Extract from database
    results = engine.extract_from_database(limit=limit, website=website)
    
    # Generate report
    report = engine.get_extraction_report(results)
    
    logger.info(f"Extraction complete: {report}")
    return results


def extract_single_job(url: str, job_role: str = None, suffix: str = None):
    """Extract details from a single job URL."""
    logger.info(f"Extracting job details from: {url}")
    
    config = create_job_detail_config()
    engine = JobDetailExtractionEngine(config=config)
    
    result = engine.extract_single_job(url, job_role, suffix)
    
    if result.success:
        logger.info(f"Successfully extracted: {result.job_title} at {result.company}")
    else:
        logger.error(f"Failed to extract: {result.error_message}")
    
    return result


def main():
    """Main function for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract job details from URLs")
    parser.add_argument("--url", help="Single URL to extract")
    parser.add_argument("--limit", type=int, default=10, help="Limit for database extraction")
    parser.add_argument("--website", help="Filter by website (LinkedIn, SkillsFuture)")
    parser.add_argument("--batch", action="store_true", help="Extract from database")
    
    args = parser.parse_args()
    
    if args.url:
        # Extract single URL
        result = extract_single_job(args.url)
        print(f"Extraction result: {result}")
    elif args.batch:
        # Batch extract from database
        results = extract_job_details_from_database(
            limit=args.limit, 
            website=args.website
        )
        print(f"Extracted {len(results)} jobs")
    else:
        print("Please specify --url or --batch")


if __name__ == "__main__":
    main()