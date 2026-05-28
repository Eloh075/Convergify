"""
Standalone script to run the V2 scraper
This is called as a subprocess from the API
"""
import sys
import os
import json
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from scraper.browser_manager import BrowserManager
from scraper.search_handler import SearchHandler
from scraper.sample_extractor import SampleExtractor
from scraper.config import ScraperConfig, setup_logging
from datetime import datetime

async def scrape_jobs(search_term: str, employment_type: str, max_jobs: int):
    """Scrape jobs and return results"""
    setup_logging()
    
    config = ScraperConfig(
        headless=False,  # Set to False to see the browser
        delay_seconds=2.0,
        page_load_timeout=10,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    scraped_jobs = []
    
    try:
        async with BrowserManager(config) as browser:
            search_handler = SearchHandler(browser)
            
            success = await search_handler.perform_search(
                "https://www.mycareersfuture.gov.sg/", 
                search_term, 
                [employment_type]
            )
            
            if not success:
                return {"success": False, "jobs": [], "error": "Search failed"}
            
            sample_extractor = SampleExtractor(browser)
            
            job_urls = []
            for attempt in range(3):
                job_urls = await sample_extractor._collect_job_urls()
                if job_urls:
                    break
                await asyncio.sleep(2)
            
            if not job_urls:
                return {"success": False, "jobs": [], "error": "No job URLs found"}
            
            job_urls_to_process = job_urls[:max_jobs]
            
            for i, job_url in enumerate(job_urls_to_process):
                try:
                    full_url = f"https://www.mycareersfuture.gov.sg{job_url}"
                    await browser.page.goto(full_url)
                    await asyncio.sleep(2)
                    await browser.wait_for_content_load()
                    
                    job_listing = await sample_extractor._extract_job_data_from_detail_page()
                    
                    if job_listing:
                        job_listing.original_url = full_url
                        job_listing.calculate_completeness_score()
                        
                        job_dict = {
                            "job_id": job_listing.job_id,
                            "title": job_listing.title,
                            "company": job_listing.company_name,
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
                            "description": "\n".join(sample_extractor._clean_text_simple(job_listing.description)) if isinstance(sample_extractor._clean_text_simple(job_listing.description), list) else sample_extractor._clean_text_simple(job_listing.description),
                            "responsibilities": "\n".join(sample_extractor._clean_text_simple(job_listing.responsibilities)) if isinstance(sample_extractor._clean_text_simple(job_listing.responsibilities), list) else sample_extractor._clean_text_simple(job_listing.responsibilities)
                        }
                        
                        scraped_jobs.append(job_dict)
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"Error extracting job {i+1}: {e}", file=sys.stderr)
                    continue
            
            return {"success": True, "jobs": scraped_jobs}
            
    except Exception as e:
        return {"success": False, "jobs": [], "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(json.dumps({"success": False, "error": "Invalid arguments"}))
        sys.exit(1)
    
    search_term = sys.argv[1]
    employment_type = sys.argv[2]
    max_jobs = int(sys.argv[3])
    
    result = asyncio.run(scrape_jobs(search_term, employment_type, max_jobs))
    print(json.dumps(result))
