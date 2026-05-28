"""
Job Scraping Adapter - Integration with V2 scraper
"""
import asyncio
import logging
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add V2 scraper parent directory to path
v2_scraper_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'V2 Scraper w debugC'))
if v2_scraper_parent not in sys.path:
    sys.path.insert(0, v2_scraper_parent)

# Now import V2 scraper as a package
from src import browser_manager as v2_browser
from src import search_handler as v2_search
from src import sample_extractor as v2_extractor
from src import config as v2_config

logger = logging.getLogger(__name__)

class JobScrapingAdapter:
    """Adapter for job scraping using V2 scraper"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the job scraping adapter"""
        self.available = True
        self.current_scraping_job = None
        
        # Setup logging for V2 scraper
        v2_config.setup_logging()
        
        logger.info("JobScrapingAdapter initialized with V2 scraper")
    
    async def scrape_jobs(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape jobs using V2 scraper"""
        try:
            # Extract configuration
            search_term = config.get('search_terms', ['developer'])[0]
            employment_type = config.get('employment_type', 'internship')
            max_jobs = config.get('max_jobs', 5)
            
            # Create scraping job ID
            scraping_job_id = f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize scraping job tracking
            self.current_scraping_job = {
                'id': scraping_job_id,
                'status': 'running',
                'progress': 0,
                'total_jobs': 0,
                'scraped_jobs': 0,
                'errors': [],
                'started_at': datetime.now(),
                'estimated_completion': None
            }
            
            logger.info("Starting V2 job scraping: %s, %s, max: %d", search_term, employment_type, max_jobs)
            
            # Update progress
            self.current_scraping_job['progress'] = 20
            
            # Perform V2 scraping
            scraped_jobs = await self._scrape_with_v2(search_term, employment_type, max_jobs)
            
            # Update job status
            self.current_scraping_job['status'] = 'completed'
            self.current_scraping_job['progress'] = 100
            self.current_scraping_job['scraped_jobs'] = len(scraped_jobs)
            
            logger.info("V2 scraper completed: %d jobs", len(scraped_jobs))
            
            # Process results
            return self._process_scraping_results(scraped_jobs, config, scraping_job_id)
            
        except Exception as e:
            logger.error(f"❌ V2 job scraping failed: {e}")
            if self.current_scraping_job:
                self.current_scraping_job['status'] = 'failed'
                self.current_scraping_job['errors'].append(str(e))
            
            return self._create_error_result(str(e), config)
    
    async def _scrape_with_v2(self, search_term: str, employment_type: str, max_jobs: int) -> List[Dict[str, Any]]:
        """Use V2 scraper to scrape jobs"""
        
        # Map frontend employment types to V2 scraper types
        employment_type_mapping = {
            'full-time': 'full-time',
            'part-time': 'part-time', 
            'contract': 'contract',
            'internship': 'internship',
            'all': 'all'
        }
        
        # Use mapped employment type, default to internship if not found
        mapped_employment_type = employment_type_mapping.get(employment_type.lower(), 'internship')
        
        logger.info(f"Mapped employment type: {employment_type} -> {mapped_employment_type}")
        
        config = v2_config.ScraperConfig(
            headless=True,  # Run headless for backend
            delay_seconds=2.0,
            page_load_timeout=10,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        scraped_jobs = []
        
        try:
            async with v2_browser.BrowserManager(config) as browser:
                # Perform search
                search_handler = v2_search.SearchHandler(browser)
                logger.info("Performing V2 search...")
                
                success = await search_handler.perform_search(
                    "https://www.mycareersfuture.gov.sg/", 
                    search_term, 
                    [mapped_employment_type]
                )
                
                if not success:
                    raise Exception("V2 search failed")
                
                self.current_scraping_job['progress'] = 40
                
                # Extract jobs
                sample_extractor = v2_extractor.SampleExtractor(browser)
                
                # Get job URLs with retry logic
                job_urls = []
                for attempt in range(3):
                    job_urls = await sample_extractor._collect_job_urls()
                    if job_urls:
                        break
                    await asyncio.sleep(2)
                
                if not job_urls:
                    raise Exception("No job URLs found")
                
                self.current_scraping_job['total_jobs'] = len(job_urls)
                self.current_scraping_job['progress'] = 50
                
                # Limit to max_jobs
                job_urls_to_process = job_urls[:max_jobs]
                
                # Extract job data
                for i, job_url in enumerate(job_urls_to_process):
                    try:
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
                            
                            # Convert to standardized format
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
                                "description": sample_extractor._clean_text_simple(job_listing.description),
                                "responsibilities": sample_extractor._clean_text_simple(job_listing.responsibilities)
                            }
                            
                            scraped_jobs.append(job_dict)
                            self.current_scraping_job['scraped_jobs'] = len(scraped_jobs)
                            
                            # Update progress
                            progress = 50 + (40 * (i + 1) / len(job_urls_to_process))
                            self.current_scraping_job['progress'] = int(progress)
                        
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"Error extracting job {i+1}: {e}")
                        continue
                
                return scraped_jobs
                
        except Exception as e:
            logger.error(f"V2 scraping error: {e}")
            raise
    
    def _process_scraping_results(self, scraped_jobs: List[Dict[str, Any]], 
                                 config: Dict[str, Any], scraping_job_id: str) -> Dict[str, Any]:
        """Process scraping results into standardized format"""
        
        # Calculate statistics
        total_jobs = len(scraped_jobs)
        avg_completeness = sum(job.get('data_completeness_score', 0) for job in scraped_jobs) / total_jobs if total_jobs > 0 else 0
        
        # Group by company
        companies = {}
        for job in scraped_jobs:
            company = job.get('company', 'Unknown')
            if company not in companies:
                companies[company] = 0
            companies[company] += 1
        
        # Extract unique skills
        all_skills = set()
        for job in scraped_jobs:
            skills = job.get('required_skills', [])
            all_skills.update(skills)
        
        return {
            "success": True,
            "scraping_job_id": scraping_job_id,
            "jobs": scraped_jobs,
            "metadata": {
                "total_jobs_scraped": total_jobs,
                "search_term": config.get('search_terms', [''])[0],
                "employment_type": config.get('employment_type', ''),
                "max_jobs_requested": config.get('max_jobs', 0),
                "scraped_at": datetime.now().isoformat(),
                "average_completeness_score": avg_completeness,
                "unique_companies": len(companies),
                "unique_skills": len(all_skills),
                "scraping_duration": (datetime.now() - self.current_scraping_job['started_at']).total_seconds() if self.current_scraping_job else 0
            },
            "statistics": {
                "companies": dict(sorted(companies.items(), key=lambda x: x[1], reverse=True)),
                "top_skills": list(all_skills)[:20],  # Top 20 skills
                "employment_types": list(set(job.get('employment_type', '') for job in scraped_jobs)),
                "salary_ranges": self._calculate_salary_statistics(scraped_jobs)
            }
        }
    
    def _calculate_salary_statistics(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate salary statistics from scraped jobs"""
        salaries = []
        
        for job in jobs:
            salary_min = job.get('salary_min')
            salary_max = job.get('salary_max')
            
            if salary_min and salary_max:
                avg_salary = (salary_min + salary_max) / 2
                salaries.append(avg_salary)
            elif salary_min:
                salaries.append(salary_min)
            elif salary_max:
                salaries.append(salary_max)
        
        if not salaries:
            return {"available": False}
        
        salaries.sort()
        n = len(salaries)
        
        return {
            "available": True,
            "count": n,
            "min": min(salaries),
            "max": max(salaries),
            "average": sum(salaries) / n,
            "median": salaries[n // 2] if n % 2 == 1 else (salaries[n // 2 - 1] + salaries[n // 2]) / 2
        }
    
    def _create_error_result(self, error_message: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create error result"""
        return {
            "success": False,
            "error": error_message,
            "jobs": [],
            "metadata": {
                "total_jobs_scraped": 0,
                "search_term": config.get('search_terms', [''])[0],
                "employment_type": config.get('employment_type', ''),
                "scraped_at": datetime.now().isoformat(),
                "error_occurred": True
            }
        }
    
    async def get_scraping_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of scraping job"""
        if not self.current_scraping_job or self.current_scraping_job['id'] != job_id:
            return {
                "found": False,
                "error": "Scraping job not found"
            }
        
        job = self.current_scraping_job
        
        return {
            "found": True,
            "id": job['id'],
            "status": job['status'],
            "progress": job['progress'],
            "total_jobs": job['total_jobs'],
            "scraped_jobs": job['scraped_jobs'],
            "errors": job['errors'],
            "started_at": job['started_at'].isoformat(),
            "estimated_completion": job['estimated_completion'].isoformat() if job['estimated_completion'] else None
        }
    
    def is_available(self) -> bool:
        """Check if the job scraping engine is available"""
        return self.available