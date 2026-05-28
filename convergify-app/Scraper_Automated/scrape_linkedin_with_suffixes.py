"""LinkedIn scraper with suffix expansion for comprehensive job collection."""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from scraper.linkedin_scraper import LinkedInScraper
from scraper.suffix_parser import parse_job_role_and_suffix


# Top 5 high-yield suffixes based on testing (see SUFFIX_EXPANSION_GUIDE.md)
# These suffixes provide 5x data expansion with minimal API calls
RECOMMENDED_SUFFIXES = [
    "",              # Base role (e.g., "Software Engineer")
    " Intern",       # High yield: 60+ jobs
    " Internship",   # High yield: 60+ jobs
    " Graduate",     # High yield: 60+ jobs
    " Junior",       # High yield: 58+ jobs
    " Associate",    # High yield: 58+ jobs
]


def scrape_with_suffixes(base_role: str, suffixes: list = None, max_urls: int = 10000) -> dict:
    """
    Scrape LinkedIn for a job role using suffix expansion.
    
    Args:
        base_role: Base job title (e.g., "Software Engineer")
        suffixes: List of suffixes to append to base role (defaults to RECOMMENDED_SUFFIXES)
        max_urls: Maximum URLs to collect per suffix variation
        
    Returns:
        Dictionary with scraping results
    """
    if suffixes is None:
        suffixes = RECOMMENDED_SUFFIXES
    
    start_time = datetime.now()
    logger.info(f"\n{'#'*80}")
    logger.info(f"# LINKEDIN SUFFIX EXPANSION SCRAPING")
    logger.info(f"# Base Role: {base_role}")
    logger.info(f"# Suffixes: {len(suffixes)}")
    logger.info(f"# Max URLs per suffix: {max_urls}")
    logger.info(f"# Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'#'*80}\n")
    
    results = {
        "base_role": base_role,
        "suffixes_used": suffixes,
        "suffix_results": [],
        "total_new": 0,
        "total_existing": 0,
        "total_collected": 0
    }
    
    for i, suffix in enumerate(suffixes, 1):
        search_query = f"{base_role}{suffix}"
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Suffix {i}/{len(suffixes)}: '{suffix}' (Search: '{search_query}')")
        logger.info(f"{'='*80}")
        
        try:
            scraper = LinkedInScraper()
            # The scraper will automatically parse the search_query and separate base_role and suffix
            result = scraper.run_session(search_query, max_urls)
            
            suffix_data = {
                "suffix": suffix,
                "search_query": search_query,
                "success": result.get("success", False),
                "new_count": result.get("new_count", 0),
                "existing_count": result.get("existing_count", 0),
                "total_collected": result.get("total_collected", 0),
                "error": result.get("error", None)
            }
            
            results["suffix_results"].append(suffix_data)
            
            if suffix_data["success"]:
                results["total_new"] += suffix_data["new_count"]
                results["total_existing"] += suffix_data["existing_count"]
                results["total_collected"] += suffix_data["total_collected"]
                
                logger.info(f"✓ Success: {suffix_data['new_count']} new, {suffix_data['existing_count']} existing")
            else:
                logger.error(f"✗ Failed: {suffix_data['error']}")
            
            # Wait between suffix variations to avoid rate limiting
            if i < len(suffixes):
                logger.info(f"Waiting 3 seconds before next suffix...")
                time.sleep(3)
                
        except Exception as e:
            logger.error(f"Exception while scraping '{search_query}': {e}")
            results["suffix_results"].append({
                "suffix": suffix,
                "search_query": search_query,
                "success": False,
                "error": str(e)
            })
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info(f"\n{'#'*80}")
    logger.info(f"# SCRAPING COMPLETE")
    logger.info(f"{'#'*80}")
    logger.info(f"Base Role: {base_role}")
    logger.info(f"Duration: {duration}")
    logger.info(f"\n--- Final Statistics ---")
    logger.info(f"Suffixes processed: {len(suffixes)}")
    logger.info(f"Total new jobs: {results['total_new']}")
    logger.info(f"Total existing jobs: {results['total_existing']}")
    logger.info(f"Total jobs collected: {results['total_collected']}")
    
    # Detailed breakdown
    logger.info(f"\n--- Suffix Breakdown ---")
    for suffix_data in results["suffix_results"]:
        suffix_display = f"'{suffix_data['suffix']}'" if suffix_data['suffix'] else "(base)"
        status = "✓" if suffix_data["success"] else "✗"
        logger.info(f"{status} {suffix_display}: {suffix_data.get('new_count', 0)} new, {suffix_data.get('existing_count', 0)} existing")
        if suffix_data.get("error"):
            logger.info(f"   Error: {suffix_data['error']}")
    
    logger.info(f"\n{'#'*80}\n")
    
    return results


def main():
    """Main function."""
    # Example: Scrape "AI Engineer" with suffix expansion
    base_role = "AI Engineer"
    
    logger.info("Starting LinkedIn scraping with suffix expansion...")
    results = scrape_with_suffixes(base_role)
    
    logger.info(f"Scraping completed!")
    logger.info(f"Total unique jobs collected: {results['total_new']}")


if __name__ == "__main__":
    main()
