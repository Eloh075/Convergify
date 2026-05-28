"""URL scraper component for extracting job listing URLs from search results."""

from typing import List, Optional
from loguru import logger
from scraper.url_normalizer import URLNormalizer


class URLScraper:
    """Component for scraping job listing URLs from search result pages."""
    
    def __init__(self, browser_manager):
        """Initialize URL scraper with browser manager."""
        self.browser = browser_manager
        self.collected_urls: List[str] = []
        self.max_pages: int = 10
        self.max_urls: int = 25  # Default max URLs to collect
        self.delay_between_pages: int = 2
        self.normalizer = URLNormalizer()
    
    def set_max_pages(self, max_pages: int) -> None:
        """Set maximum number of pages to scrape."""
        self.max_pages = max_pages
    
    def set_max_urls(self, max_urls: int) -> None:
        """Set maximum number of URLs to collect."""
        self.max_urls = max_urls
    
    def set_delay_between_pages(self, delay: int) -> None:
        """Set delay between page navigations."""
        self.delay_between_pages = delay
    
    def extract_urls(self, adapter) -> List[str]:
        """Extract all job listing URLs from current page."""
        urls = adapter.extract_job_urls_from_page(self.browser)
        
        logger.info(f"Extracted {len(urls)} URLs from current page")
        return urls
    
    def handle_pagination(self, adapter) -> List[str]:
        """Navigate through all result pages and collect URLs."""
        all_urls: List[str] = []
        page_count = 0
        consecutive_empty_pages = 0  # Track empty pages to stop pagination
        
        while page_count < self.max_pages:
            # Extract URLs from current page
            current_urls = self.extract_urls(adapter)
            
            # If no URLs found, increment empty page counter
            if len(current_urls) == 0:
                consecutive_empty_pages += 1
                logger.info(f"Page {page_count + 1}: No URLs found (empty page {consecutive_empty_pages})")
                # Stop if we get 2 consecutive empty pages
                if consecutive_empty_pages >= 2:
                    logger.info("Found 2 consecutive empty pages, stopping pagination")
                    break
            else:
                consecutive_empty_pages = 0  # Reset counter when we find URLs
                all_urls.extend(current_urls)
                logger.info(f"Page {page_count + 1}: Collected {len(current_urls)} URLs (Total: {len(all_urls)})")
            
            # Check if we've collected enough URLs
            if len(all_urls) >= self.max_urls:
                logger.info(f"Reached max URL limit ({self.max_urls})")
                break
            
            # Check if there's a next page
            page_html = self.browser.page.content()
            if not adapter.has_next_page(page_html):
                logger.info("No more pages found")
                break
            
            # Navigate to next page
            next_url = adapter.get_next_page_url(page_html)
            if next_url:
                self.browser.navigate_to(next_url)
                self.browser.wait(self.delay_between_pages)
            else:
                # Try clicking pagination button
                try:
                    self.browser.click_element(adapter.SELECTORS.get("pagination_next", ""))
                    self.browser.wait(self.delay_between_pages)
                except:
                    logger.info("Could not click next button, stopping pagination")
                    break
            
            page_count += 1
        
        # Deduplicate all collected URLs
        unique_urls = self.deduplicate(all_urls)
        
        # Trim to max_urls if needed
        if len(unique_urls) > self.max_urls:
            unique_urls = unique_urls[:self.max_urls]
        
        logger.info(f"Total unique URLs collected: {len(unique_urls)}")
        
        return unique_urls
    
    def _extract_urls_from_html(self, page_html: str) -> List[str]:
        """Extract URLs from page HTML using adapter's selectors."""
        # This method will be implemented by site-specific scrapers
        # For now, return empty list - actual implementation in site-specific scraper
        return []
    
    def deduplicate(self, urls: List[str]) -> List[str]:
        """Remove duplicate URLs from collection using normalization."""
        seen = set()
        unique_urls = []
        
        for url in urls:
            # Normalize URL to remove tracking parameters
            normalized = self.normalizer.normalize_url(url)
            
            if normalized not in seen:
                seen.add(normalized)
                unique_urls.append(normalized)  # Store normalized URL
        
        logger.info(f"Deduplicated {len(urls)} URLs to {len(unique_urls)} unique URLs")
        return unique_urls
    
    def get_collected_urls(self) -> List[str]:
        """Get all URLs collected so far."""
        return self.collected_urls
    
    def clear_collected_urls(self) -> None:
        """Clear collected URLs."""
        self.collected_urls = []
        logger.info("Cleared collected URLs")