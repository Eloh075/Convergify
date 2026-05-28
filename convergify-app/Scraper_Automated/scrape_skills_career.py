"""CLI entry point for Skills Career job scraping."""

import sys
import os
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger

from scraper.skills_career_scraper import SkillsCareerScraper


def run_skills_career_scraping(job_title: str, max_urls: int = 25, employment_type: str = "") -> None:
    """Run a scraping session for Skills Career."""
    logger.info(f"Starting Skills Career scraping for '{job_title}' (max {max_urls} URLs)")
    if employment_type:
        logger.info(f"Employment type: {employment_type}")
    
    try:
        scraper = SkillsCareerScraper()
        result = scraper.run_session(job_title, max_urls, employment_type)
        
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
        description="Skills Career Job Scraping Tool"
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
        "--employment-type",
        choices=["internship", "permanent", "fulltime", "parttime", "contract", "temporary", "freelance"],
        default="",
        help="Employment type filter (default: none)"
    )
    
    args = parser.parse_args()
    
    run_skills_career_scraping(args.job_title, args.max_urls, args.employment_type)


if __name__ == "__main__":
    main()
