"""Direct V2 scraper integration - copy/paste approach."""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from .browser_manager import BrowserManager
from .search_handler import SearchHandler
from .sample_extractor import SampleExtractor
from .config import ScraperConfig, setup_logging


class JobScraper:
    """Direct V2 scraper integration."""
    
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        
    async def scrape_jobs(self, search_term: str, employment_type: str = "internship", max_jobs: int = 10) -> List[Dict[str, Any]]:
        """Scrape jobs directly using V2 scraper code."""
        
        print(f"🚀 Starting direct V2 scraper: {search_term}, {employment_type}, max: {max_jobs}")
        
        setup_logging()
        
        config = ScraperConfig(
            headless=True,
            delay_seconds=2.0,
            page_load_timeout=5,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        scraped_jobs = []
        
        try:
            async with BrowserManager(config) as browser:
                # Perform search
                search_handler = SearchHandler(browser)
                print("🔍 Performing search...")
                
                success = await search_handler.perform_search(
                    "https://www.mycareersfuture.gov.sg/", 
                    search_term, 
                    [employment_type]
                )
                
                if not success:
                    print("❌ Search failed")
                    return []
                
                print("✅ Search completed successfully")
                
                # Extract jobs
                sample_extractor = SampleExtractor(browser)
                
                # Get job URLs with retry logic
                print("📋 Collecting job URLs...")
                job_urls = []
                
                # Try multiple times to collect URLs
                for attempt in range(3):
                    job_urls = await sample_extractor._collect_job_urls()
                    if job_urls:
                        break
                    print(f"   Attempt {attempt + 1}: No URLs found, waiting and retrying...")
                    await asyncio.sleep(2)
                
                if not job_urls:
                    print("❌ No actual search results found")
                    print("ℹ️  The search results page only contains recommended jobs, not direct search matches.")
                    return []
                
                print(f"✅ Found {len(job_urls)} job URLs")
                
                # Limit to max_jobs
                job_urls_to_process = job_urls[:max_jobs]
                print(f"📊 Processing first {len(job_urls_to_process)} jobs...")
                
                # Extract job data
                for i, job_url in enumerate(job_urls_to_process):
                    try:
                        print(f"   Extracting job {i+1}/{len(job_urls_to_process)}: {job_url.split('/')[-1][:50]}...")
                        
                        # Navigate to job detail page
                        full_url = f"https://www.mycareersfuture.gov.sg{job_url}"
                        await browser.page.goto(full_url)
                        await asyncio.sleep(2)
                        await browser.wait_for_content_load()
                        
                        # Extract job data
                        job_listing = await sample_extractor._extract_job_data_from_detail_page()
                        
                        if job_listing:
                            job_listing.original_url = full_url
                            job_listing.calculate_completeness_score()
                            
                            # Convert to dict for JSON serialization with better structure
                            job_dict = {
                                "job_id": job_listing.job_id,
                                "title": job_listing.title,
                                "company_name": job_listing.company_name,
                                "location": job_listing.location,
                                "employment_type": job_listing.employment_type,
                                "salary_min": job_listing.salary_min,
                                "salary_max": job_listing.salary_max,
                                "salary_currency": job_listing.salary_currency,
                                "required_skills": job_listing.required_skills,
                                "requirements": job_listing.requirements,
                                "experience_years": job_listing.experience_years,
                                "education_requirements": job_listing.education_requirements,
                                "posting_date": job_listing.posting_date.isoformat() if job_listing.posting_date else None,
                                "source_url": job_listing.original_url,
                                "data_completeness_score": job_listing.data_completeness_score,
                                "extraction_confidence": job_listing.extraction_confidence,
                                "scraped_at": datetime.now().isoformat(),
                                "job_description": {
                                    "full_text": sample_extractor._clean_text_simple(job_listing.description),
                                    "roles_and_responsibilities": sample_extractor._clean_text_simple(job_listing.responsibilities)
                                }
                            }
                            
                            scraped_jobs.append(job_dict)
                            print(f"      ✅ {job_listing.title} at {job_listing.company_name} (Completeness: {job_listing.data_completeness_score:.1%})")
                        else:
                            print(f"      ❌ Failed to extract job data")
                        
                        # Small delay between jobs
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        print(f"      ❌ Error extracting job {i+1}: {e}")
                        continue
                
                print(f"✅ Successfully extracted {len(scraped_jobs)} jobs!")
                return scraped_jobs
                
        except Exception as e:
            print(f"❌ Scraping failed: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def is_available(self) -> bool:
        """Check if scraper is available"""
        return True