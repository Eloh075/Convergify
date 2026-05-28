"""Extract job details for all SkillsFuture (MyCareersFuture) jobs."""

import sys
import os
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_detail_extraction.engine import JobDetailExtractionEngine
from job_detail_extraction.database import JobDetailDatabase
from job_detail_extraction.config import create_job_detail_config


def main():
    """Extract all SkillsFuture jobs from database."""
    logger.info("Starting SkillsFuture job detail extraction...")
    
    # Create configuration
    config = create_job_detail_config()
    
    # Create database connection
    database = JobDetailDatabase()
    
    # Create engine
    engine = JobDetailExtractionEngine(config=config, database=database)
    
    # Extract from database - SkillsCareer only, no limit
    results = engine.extract_from_database(limit=10000, website="SkillsCareer")
    
    # Generate report
    report = engine.get_extraction_report(results)
    
    logger.info("=" * 80)
    logger.info("EXTRACTION REPORT")
    logger.info("=" * 80)
    logger.info(f"Total processed: {report['total_processed']}")
    logger.info(f"Successful: {report['successful']}")
    logger.info(f"Failed: {report['failed']}")
    logger.info(f"Success rate: {report['success_rate']:.2f}%")
    logger.info(f"By website: {report['by_website']}")
    logger.info(f"By role: {report['by_role']}")
    
    if report['common_errors']:
        logger.info("Common errors:")
        for error, count in report['common_errors'].items():
            logger.info(f"  - {error}: {count} times")
    
    logger.info("=" * 80)
    
    return results


if __name__ == "__main__":
    main()
