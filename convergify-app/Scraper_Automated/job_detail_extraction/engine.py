"""Main engine for job detail extraction."""

import time
import random
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from scraper.browser_manager import BrowserManager

from .config import JobDetailExtractorConfig, create_job_detail_config
from .extractors import JobDetailExtractorFactory
from .models import JobDetails
from .database import JobDetailDatabase


class JobDetailExtractionEngine:
    """Main engine for extracting job details."""
    
    def __init__(self, config: Optional[JobDetailExtractorConfig] = None, database: Optional[JobDetailDatabase] = None):
        """Initialize extraction engine."""
        self.config = config or create_job_detail_config()
        self.database = database
        self.browser = BrowserManager(
            headless=self.config.headless_mode,
            timeout=self.config.timeout_seconds * 1000
        )
    
    def extract_single_job(self, url: str, job_role: Optional[str] = None, suffix: Optional[str] = None) -> JobDetails:
        """Extract details from a single job URL."""
        logger.info(f"Extracting job details from: {url}")
        
        try:
            # Create appropriate extractor
            extractor = JobDetailExtractorFactory.create_extractor(url, self.config)
            
            # Start browser (BrowserManager handles its own state)
            self.browser.start()
            
            # Extract details
            job_details = extractor.extract(url, self.browser, job_role or "")
            
            # Set job role and suffix if provided
            if job_role:
                job_details.job_role = job_role
            if suffix:
                job_details.suffix = suffix
            
            # Save to database if available
            if self.database and job_details.success:
                self.database.save_job_details(job_details)
            
            return job_details
            
        except Exception as e:
            logger.error(f"Error extracting job details: {e}")
            return JobDetails(
                url=url,
                website="Unknown",
                job_role=job_role or "",
                suffix=suffix,
                extracted_at=datetime.now(),
                success=False,
                error_message=str(e),
            )
        finally:
            # Stop browser and add random delay between requests
            self.browser.stop()
            
            # LinkedIn needs longer delays (3-7 seconds) to avoid detection
            # Other sites use shorter delays (1-2 seconds)
            if "linkedin.com" in url.lower():
                delay = random.uniform(3.0, 7.0)
            else:
                delay = random.uniform(1.0, 2.0)
            
            logger.debug(f"Waiting {delay:.2f} seconds before next request...")
            time.sleep(delay)
    
    def extract_batch(self, urls: List[Dict[str, Any]]) -> List[JobDetails]:
        """Extract details from a batch of URLs."""
        results = []
        total = len(urls)
        
        logger.info(f"Starting batch extraction of {total} jobs")
        
        for i, job_info in enumerate(urls, 1):
            url = job_info.get("url")
            job_role = job_info.get("job_role")
            suffix = job_info.get("suffix")
            
            if not url:
                logger.warning(f"Skipping job {i}/{total}: No URL provided")
                continue
            
            logger.info(f"Processing job {i}/{total}: {url}")
            
            # Extract details
            job_details = self.extract_single_job(url, job_role, suffix)
            results.append(job_details)
            
            # Log progress
            if job_details.success:
                logger.info(f"✓ Successfully extracted: {job_details.job_title or 'Unknown title'}")
            else:
                logger.error(f"✗ Failed to extract: {job_details.error_message}")
            
            # Check if we should take a break
            if i % 10 == 0:
                logger.info(f"Processed {i}/{total} jobs, taking a short break...")
                time.sleep(5)
        
        # Calculate statistics
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        logger.info(f"Batch extraction complete: {successful} successful, {failed} failed")
        
        return results
    
    def extract_from_database(self, limit: int = 50, website: Optional[str] = None) -> List[JobDetails]:
        """Extract details for jobs in database that haven't been extracted yet."""
        if not self.database:
            logger.error("No database connection available")
            return []
        
        # Get jobs to extract
        jobs_to_extract = self.database.get_jobs_to_extract(limit, website)
        
        if not jobs_to_extract:
            logger.info("No jobs need extraction")
            return []
        
        logger.info(f"Found {len(jobs_to_extract)} jobs to extract from database")
        
        # Extract details
        results = self.extract_batch(jobs_to_extract)
        
        # Update extraction stats
        stats = self.database.get_extraction_stats()
        logger.info(f"Extraction stats: {stats.get('extracted_jobs', 0)}/{stats.get('total_jobs', 0)} extracted")
        
        return results
    
    def get_extraction_report(self, results: List[JobDetails]) -> Dict[str, Any]:
        """Generate extraction report."""
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        # Count by website
        by_website = {}
        for result in results:
            website = result.website
            by_website[website] = by_website.get(website, 0) + 1
        
        # Count by job role
        by_role = {}
        for result in results:
            role = result.job_role or "Unknown"
            by_role[role] = by_role.get(role, 0) + 1
        
        # Common errors
        errors = {}
        for result in results:
            if result.error_message:
                error_key = result.error_message[:100]  # Truncate long errors
                errors[error_key] = errors.get(error_key, 0) + 1
        
        return {
            "total_processed": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "by_website": by_website,
            "by_role": by_role,
            "common_errors": dict(sorted(errors.items(), key=lambda x: x[1], reverse=True)[:5]),
            "sample_extracted": [
                {
                    "url": r.url,
                    "job_title": r.job_title,
                    "company": r.company,
                    "success": r.success,
                }
                for r in results[:5] if r.success
            ],
        }