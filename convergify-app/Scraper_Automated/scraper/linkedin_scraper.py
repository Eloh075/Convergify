"""LinkedIn specific scraper."""

from typing import Dict, Any, Optional
from loguru import logger

from scraper.config import create_scraper_config
from scraper.browser_manager import BrowserManager
from scraper.database.job_database import JobDatabase
from scraper.url_scraper import URLScraper
from scraper.adapters.linkedin_adapter import LinkedInAdapter
from scraper.experience_level_normalizer import ExperienceLevelNormalizer
from scraper.suffix_parser import parse_job_role_and_suffix


class LinkedInScraper:
    """Scraper specifically for LinkedIn."""
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize LinkedIn scraper."""
        self.config = config or create_scraper_config()
        self.browser = BrowserManager(headless=self.config.headless_mode, timeout=self.config.timeout_seconds * 1000)
        self.url_scraper = URLScraper(self.browser)
        self.database = JobDatabase(table_name=self.config.database_table)
        self.adapter = LinkedInAdapter()
        self.normalizer = ExperienceLevelNormalizer()
        
        logger.info("LinkedInScraper initialized")
    
    def run_session(self, job_title: str, max_urls: int = 25, experience_level: str = "") -> Dict[str, Any]:
        """Execute a complete scraping session for LinkedIn."""
        logger.info(f"Starting LinkedIn scraping for '{job_title}' (max {max_urls} URLs)")
        if experience_level:
            logger.info(f"Experience level: {experience_level}")
        
        try:
            # Start browser
            self.browser.start()
            
            # Navigate to search URL with job title and experience level
            search_url = self.adapter.get_search_url(job_title, experience_level)
            self.browser.navigate_to(search_url)
            
            # Wait for job listings to load
            self.browser.wait(3)
            
            # Wait for results to load
            job_selector = self.adapter.SELECTORS.get("job_listings", "")
            if job_selector:
                self.browser.wait_for_selector(job_selector, timeout=10000)
            
            # Configure URL scraper
            self.url_scraper.set_max_pages(self.config.max_pages)
            self.url_scraper.set_max_urls(max_urls)
            self.url_scraper.set_delay_between_pages(self.config.delay_between_requests)
            
            # Scrape URLs using the adapter
            urls = self.url_scraper.handle_pagination(self.adapter)
            
            # Extract job metadata
            job_metadata = self.adapter.extract_job_metadata(self.browser)
            
            # Normalize experience level
            normalized_level = self.normalizer.normalize_linkedin_level(experience_level) if experience_level else ""
            
            # Update metadata with normalized experience level (only if not already set)
            for metadata in job_metadata:
                if normalized_level and not metadata.get("experience_level"):
                    metadata["experience_level"] = normalized_level
            
            # Parse job role and suffix
            base_role, suffix = parse_job_role_and_suffix(job_title)
            
            # Save to database
            if urls:
                result = self.database.save_job_urls_with_metadata(
                    urls, 
                    "LinkedIn", 
                    base_role,  # Store only the base role
                    job_metadata,
                    normalized_level,
                    suffix  # Store suffix separately
                )
                logger.info(f"Scraping session complete: {result['new']} new, {result['existing']} existing")
                
                return {
                    "success": True,
                    "new_count": result['new'],
                    "existing_count": result['existing'],
                    "total_collected": len(urls),
                    "urls": urls,
                    "experience_level": normalized_level
                }
            else:
                logger.warning("No URLs collected during scraping session")
                return {
                    "success": True,
                    "new_count": 0,
                    "existing_count": 0,
                    "total_collected": 0,
                    "urls": [],
                    "experience_level": normalized_level
                }
                
        except Exception as e:
            logger.error(f"Scraping session failed: {e}")
            return {"success": False, "error": str(e)}
        finally:
            # Always stop browser
            self.browser.stop()
