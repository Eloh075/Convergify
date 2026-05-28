"""Skills Career specific scraper."""

from typing import Dict, Any, Optional
from loguru import logger

from scraper.config import create_scraper_config
from scraper.browser_manager import BrowserManager
from scraper.database.job_database import JobDatabase
from scraper.url_scraper import URLScraper
from scraper.adapters.skills_career_adapter import SkillsCareerAdapter
from scraper.experience_level_normalizer import ExperienceLevelNormalizer


class SkillsCareerScraper:
    """Scraper specifically for Skills Career (mycareersfuture.gov.sg)."""
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize Skills Career scraper."""
        self.config = config or create_scraper_config()
        self.browser = BrowserManager(headless=self.config.headless_mode, timeout=self.config.timeout_seconds * 1000)
        self.url_scraper = URLScraper(self.browser)
        self.database = JobDatabase(table_name=self.config.database_table)
        self.adapter = SkillsCareerAdapter()
        self.normalizer = ExperienceLevelNormalizer()
        
        logger.info("SkillsCareerScraper initialized")
    
    def run_session(self, job_title: str, max_urls: int = 25, employment_type: str = "") -> Dict[str, Any]:
        """Execute a complete scraping session for Skills Career."""
        logger.info(f"Starting Skills Career scraping for '{job_title}' (max {max_urls} URLs)")
        if employment_type:
            logger.info(f"Employment type: {employment_type}")
        
        try:
            # Start browser
            self.browser.start()
            
            # Navigate to search URL
            search_url = self.adapter.get_search_url(job_title, employment_type)
            self.browser.navigate_to(search_url)
            
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
            
            # Normalize experience level from employment type
            normalized_level = self.normalizer.normalize_employment_type(employment_type)
            
            # Update metadata with normalized experience level
            for metadata in job_metadata:
                metadata["experience_level"] = normalized_level
            
            # Save to database
            if urls:
                result = self.database.save_job_urls_with_metadata(
                    urls, 
                    "SkillsCareer", 
                    job_title, 
                    job_metadata,
                    normalized_level
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
