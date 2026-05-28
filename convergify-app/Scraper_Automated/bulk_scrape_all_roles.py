"""Bulk scraping script for all 30 job roles using LinkedIn and Skills Career."""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from scraper.linkedin_scraper import LinkedInScraper
from scraper.skills_career_scraper import SkillsCareerScraper


# Top 6 High-Volume Job Roles
JOB_ROLES = [
    "Software Engineer",
    "Data Analyst",
    "AI Engineer",
    "Full Stack Developer",
    "Business Analyst",
    "Product Manager"
]


def scrape_role(job_title: str, max_urls: int = 10000) -> dict:
    """Scrape a single job role from both LinkedIn and Skills Career."""
    results = {
        "job_title": job_title,
        "linkedin": {"success": False, "new": 0, "existing": 0, "total": 0, "error": None},
        "skills_career": {"success": False, "new": 0, "existing": 0, "total": 0, "error": None}
    }
    
    # Scrape from LinkedIn
    logger.info(f"\n{'='*80}")
    logger.info(f"Scraping LinkedIn for: {job_title}")
    logger.info(f"{'='*80}")
    try:
        linkedin_scraper = LinkedInScraper()
        linkedin_result = linkedin_scraper.run_session(job_title, max_urls)
        
        if linkedin_result.get("success"):
            results["linkedin"]["success"] = True
            results["linkedin"]["new"] = linkedin_result.get("new_count", 0)
            results["linkedin"]["existing"] = linkedin_result.get("existing_count", 0)
            results["linkedin"]["total"] = linkedin_result.get("total_collected", 0)
            logger.info(f"✓ LinkedIn: {results['linkedin']['new']} new, {results['linkedin']['existing']} existing")
        else:
            results["linkedin"]["error"] = linkedin_result.get("error", "Unknown error")
            logger.error(f"✗ LinkedIn failed: {results['linkedin']['error']}")
    except Exception as e:
        results["linkedin"]["error"] = str(e)
        logger.error(f"✗ LinkedIn exception: {e}")
    
    # Wait between scrapers to avoid rate limiting
    time.sleep(3)
    
    # Scrape from Skills Career
    logger.info(f"\n{'='*80}")
    logger.info(f"Scraping Skills Career for: {job_title}")
    logger.info(f"{'='*80}")
    try:
        skills_scraper = SkillsCareerScraper()
        skills_result = skills_scraper.run_session(job_title, max_urls)
        
        if skills_result.get("success"):
            results["skills_career"]["success"] = True
            results["skills_career"]["new"] = skills_result.get("new_count", 0)
            results["skills_career"]["existing"] = skills_result.get("existing_count", 0)
            results["skills_career"]["total"] = skills_result.get("total_collected", 0)
            logger.info(f"✓ Skills Career: {results['skills_career']['new']} new, {results['skills_career']['existing']} existing")
        else:
            results["skills_career"]["error"] = skills_result.get("error", "Unknown error")
            logger.error(f"✗ Skills Career failed: {results['skills_career']['error']}")
    except Exception as e:
        results["skills_career"]["error"] = str(e)
        logger.error(f"✗ Skills Career exception: {e}")
    
    return results


def main():
    """Main bulk scraping function."""
    start_time = datetime.now()
    logger.info(f"\n{'#'*80}")
    logger.info(f"# BULK SCRAPING STARTED: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"# Total job roles: {len(JOB_ROLES)}")
    logger.info(f"# Max URLs per role per site: ALL (no limit)")
    logger.info(f"# Sites: LinkedIn, Skills Career")
    logger.info(f"{'#'*80}\n")
    
    all_results = []
    total_linkedin_jobs = 0
    total_skills_career_jobs = 0
    
    for i, job_title in enumerate(JOB_ROLES, 1):
        logger.info(f"\n{'*'*80}")
        logger.info(f"* ROLE {i}/{len(JOB_ROLES)}: {job_title}")
        logger.info(f"{'*'*80}")
        
        try:
            result = scrape_role(job_title, max_urls=10000)
            all_results.append(result)
            
            # Update totals
            total_linkedin_jobs += result["linkedin"]["new"]
            total_skills_career_jobs += result["skills_career"]["new"]
            
            # Progress summary
            logger.info(f"\n--- Progress Summary ---")
            logger.info(f"Completed: {i}/{len(JOB_ROLES)} roles")
            logger.info(f"Total LinkedIn jobs: {total_linkedin_jobs}")
            logger.info(f"Total Skills Career jobs: {total_skills_career_jobs}")
            logger.info(f"Total jobs collected: {total_linkedin_jobs + total_skills_career_jobs}")
            
        except Exception as e:
            logger.error(f"Failed to scrape {job_title}: {e}")
            all_results.append({
                "job_title": job_title,
                "linkedin": {"success": False, "error": str(e)},
                "skills_career": {"success": False, "error": str(e)}
            })
        
        # Wait between roles to avoid rate limiting
        if i < len(JOB_ROLES):
            logger.info(f"\nWaiting 5 seconds before next role...")
            time.sleep(5)
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info(f"\n{'#'*80}")
    logger.info(f"# BULK SCRAPING COMPLETED")
    logger.info(f"{'#'*80}")
    logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duration: {duration}")
    logger.info(f"\n--- Final Statistics ---")
    logger.info(f"Total roles processed: {len(all_results)}")
    logger.info(f"Total LinkedIn jobs: {total_linkedin_jobs}")
    logger.info(f"Total Skills Career jobs: {total_skills_career_jobs}")
    logger.info(f"Total jobs collected: {total_linkedin_jobs + total_skills_career_jobs}")
    
    # Detailed results
    logger.info(f"\n--- Detailed Results ---")
    for result in all_results:
        job_title = result["job_title"]
        linkedin = result["linkedin"]
        skills = result["skills_career"]
        
        logger.info(f"\n{job_title}:")
        logger.info(f"  LinkedIn: {'✓' if linkedin['success'] else '✗'} "
                   f"({linkedin.get('new', 0)} new, {linkedin.get('existing', 0)} existing)")
        if linkedin.get("error"):
            logger.info(f"    Error: {linkedin['error']}")
        
        logger.info(f"  Skills Career: {'✓' if skills['success'] else '✗'} "
                   f"({skills.get('new', 0)} new, {skills.get('existing', 0)} existing)")
        if skills.get("error"):
            logger.info(f"    Error: {skills['error']}")
    
    logger.info(f"\n{'#'*80}")
    logger.info(f"# SCRAPING SESSION COMPLETE")
    logger.info(f"{'#'*80}\n")


if __name__ == "__main__":
    main()
