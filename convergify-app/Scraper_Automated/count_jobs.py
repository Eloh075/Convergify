"""Quick script to count available job listings without scraping."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from scraper.browser_manager import BrowserManager
from scraper.adapters.linkedin_adapter import LinkedInAdapter
from scraper.adapters.skills_career_adapter import SkillsCareerAdapter


def count_linkedin_jobs(job_title: str) -> int:
    """Count available jobs on LinkedIn."""
    logger.info(f"Counting LinkedIn jobs for: {job_title}")
    
    browser = BrowserManager(headless=True, timeout=30000)
    adapter = LinkedInAdapter()
    
    try:
        browser.start()
        
        # Navigate to search URL
        search_url = adapter.get_search_url(job_title)
        browser.navigate_to(search_url)
        browser.wait(3)
        
        # Wait for job listings
        browser.wait_for_selector(adapter.SELECTORS.get("job_listings", ""), timeout=10000)
        
        # Extract URLs to count
        urls = adapter.extract_job_urls_from_page(browser)
        count = len(urls)
        
        logger.info(f"LinkedIn: Found {count} jobs on first page")
        return count
        
    except Exception as e:
        logger.error(f"LinkedIn error: {e}")
        return 0
    finally:
        browser.stop()


def count_skills_career_jobs(job_title: str) -> int:
    """Count available jobs on Skills Career."""
    logger.info(f"Counting Skills Career jobs for: {job_title}")
    
    browser = BrowserManager(headless=True, timeout=30000)
    adapter = SkillsCareerAdapter()
    
    try:
        browser.start()
        
        # Navigate to search URL
        search_url = adapter.get_search_url(job_title)
        browser.navigate_to(search_url)
        browser.wait(3)
        
        # Extract URLs to count
        urls = adapter.extract_job_urls_from_page(browser)
        count = len(urls)
        
        logger.info(f"Skills Career: Found {count} jobs on first page")
        return count
        
    except Exception as e:
        logger.error(f"Skills Career error: {e}")
        return 0
    finally:
        browser.stop()


def main():
    """Main function."""
    job_title = "AI Engineer"
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Counting available jobs for: {job_title}")
    logger.info(f"{'='*60}\n")
    
    linkedin_count = count_linkedin_jobs(job_title)
    skills_career_count = count_skills_career_jobs(job_title)
    
    total = linkedin_count + skills_career_count
    
    logger.info(f"\n{'='*60}")
    logger.info(f"RESULTS for '{job_title}':")
    logger.info(f"{'='*60}")
    logger.info(f"LinkedIn: {linkedin_count} jobs (first page)")
    logger.info(f"Skills Career: {skills_career_count} jobs (first page)")
    logger.info(f"Total: {total} jobs")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    main()
