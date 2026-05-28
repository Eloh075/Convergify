"""Demo script to run LinkedIn scraper in visible mode so you can see the browser in action."""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from scraper.linkedin_scraper import LinkedInScraper
from scraper.config import create_scraper_config


def demo_visible_scraping(job_title: str = "Software Engineer", max_urls: int = 25):
    """
    Run a demo scraping session in visible mode with just one search term.
    
    Args:
        job_title: Job title to search for
        max_urls: Maximum URLs to collect
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"🎬 DEMO: LinkedIn Scraper in VISIBLE MODE")
    logger.info(f"{'='*80}")
    logger.info(f"Job Title: {job_title}")
    logger.info(f"Max URLs: {max_urls}")
    logger.info(f"Mode: VISIBLE BROWSER (you can watch!)")
    logger.info(f"{'='*80}\n")
    
    # Create config but override headless mode
    config = create_scraper_config()
    config.headless_mode = False  # Force visible mode
    
    logger.info("🚀 Starting browser in VISIBLE mode...")
    logger.info("👀 You should see a Chrome browser window open!")
    
    try:
        # Create scraper with visible browser
        scraper = LinkedInScraper(config)
        
        logger.info(f"🔍 Searching LinkedIn for: '{job_title}'")
        logger.info("📱 Watch the browser navigate to LinkedIn...")
        
        # Run the scraping session
        result = scraper.run_session(job_title, max_urls)
        
        # Display results
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 SCRAPING RESULTS")
        logger.info(f"{'='*80}")
        
        if result.get("success"):
            logger.info(f"✅ Success!")
            logger.info(f"🆕 New jobs found: {result.get('new_count', 0)}")
            logger.info(f"📋 Existing jobs: {result.get('existing_count', 0)}")
            logger.info(f"🔗 Total URLs collected: {result.get('total_collected', 0)}")
            
            # Show some sample URLs
            urls = result.get('urls', [])
            if urls:
                logger.info(f"\n📝 Sample URLs collected:")
                for i, url in enumerate(urls[:5], 1):
                    logger.info(f"   {i}. {url}")
                if len(urls) > 5:
                    logger.info(f"   ... and {len(urls) - 5} more")
        else:
            logger.error(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🎬 Demo completed!")
        logger.info(f"{'='*80}")
        
        return result
        
    except Exception as e:
        logger.error(f"💥 Demo failed with exception: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Main function for demo."""
    logger.info("🎭 LinkedIn Scraper Visual Demo")
    logger.info("This will open a visible browser window so you can watch the scraping process!")
    
    # Give user a moment to read
    logger.info("⏰ Starting in 3 seconds...")
    time.sleep(3)
    
    # Run demo with a simple search
    result = demo_visible_scraping("AI Engineer", max_urls=50)
    
    if result.get("success"):
        logger.info("🎉 Demo completed successfully!")
    else:
        logger.error("😞 Demo encountered issues")


if __name__ == "__main__":
    main()