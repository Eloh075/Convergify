"""CLI entry point for Indeed job scraping."""

import sys
import os
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger

from scraper.indeed_scraper import IndeedScraper


def run_indeed_scraping(job_title: str, max_urls: int = 25, experience_level: str = "") -> None:
    """Run a scraping session for Indeed."""
    logger.info(f"Starting Indeed scraping for '{job_title}' (max {max_urls} URLs)")
    if experience_level:
        logger.info(f"Experience level: {experience_level}")
    
    try:
        scraper = IndeedScraper()
        result = scraper.run_session(job_title, max_urls, experience_level)
        
        if result.get("success"):
            logger.info(f"Scraping complete!")
            logger.info(f"  New URLs: {result.get('new_count', 0)}")
            logger.info(f"  Existing URLs updated: {result.get('existing_count', 0)}")
            logger.info(f"  Total collected: {result.get('total_collected', 0)}")
        else:
            logger.error(f"Scraping failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Indeed Singapore Job Scraping Tool"
    )
    parser.add_argument(
        "--job-title",
        required=True,
        help="The job title to search for"
    )
    parser.add_argument(
        "--max-urls",
        type=int,
        default=25,
        help="Maximum number of URLs to collect (default: 25)"
    )
    parser.add_argument(
        "--experience-level",
        choices=["internship", "entry", "associate", "mid", "senior", "executive"],
        default="",
        help="Experience level filter (default: none)"
    )
    
    args = parser.parse_args()
    
    run_indeed_scraping(args.job_title, args.max_urls, args.experience_level)


if __name__ == "__main__":
    main()
