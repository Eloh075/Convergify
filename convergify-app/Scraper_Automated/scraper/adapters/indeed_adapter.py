"""Indeed adapter for job scraping."""

from typing import List, Dict, Any
from urllib.parse import quote
from .base_adapter import SiteAdapter


class IndeedAdapter(SiteAdapter):
    """Adapter for Indeed job site."""
    
    SELECTORS = {
        "job_listings": ".job_seen_beacon",
        "job_link": ".jobTitle a",
        "pagination_next": ".np:last-child",
        "job_title": ".jobTitle",
        "company": ".companyName",
        "location": ".companyLocation",
        "date_posted": ".date"
    }
    
    def get_site_name(self) -> str:
        """Get the name of the job site."""
        return "Indeed"
    
    def get_search_url(self, job_title: str, experience_level: str = "") -> str:
        """Generate Indeed search URL."""
        base_url = "https://sg.indeed.com/jobs"
        
        # Combine job title and experience level for search
        search_query = job_title
        if experience_level:
            search_query = f"{job_title} {experience_level}"
        
        encoded_query = quote(search_query)
        return f"{base_url}?q={encoded_query}&l=Singapore"
    
    def extract_job_urls_from_page(self, browser) -> List[str]:
        """Extract job URLs from Indeed page."""
        try:
            # Wait for job listings to load
            browser.wait_for_selector(self.SELECTORS["job_listings"], timeout=10000)
            
            # Extract job URLs
            job_links = browser.page.query_selector_all(self.SELECTORS["job_link"])
            urls = []
            
            for link in job_links:
                href = link.get_attribute("href")
                if href:
                    # Make absolute URL if needed
                    if href.startswith("/"):
                        href = f"https://sg.indeed.com{href}"
                    
                    urls.append(href)
            
            return urls
        except Exception as e:
            print(f"Error extracting Indeed URLs: {e}")
            return []
    
    def has_next_page(self, page_html: str) -> bool:
        """Check if Indeed has next page."""
        return "np:last-child" in page_html and "Next" in page_html
    
    def get_next_page_url(self, page_html: str) -> str:
        """Get next page URL for Indeed."""
        # Indeed uses JavaScript pagination, return empty to use click method
        return ""
    
    def extract_job_metadata(self, browser) -> List[Dict[str, Any]]:
        """Extract job metadata from Indeed page."""
        try:
            job_cards = browser.page.query_selector_all(self.SELECTORS["job_listings"])
            metadata = []
            
            for card in job_cards:
                try:
                    title_elem = card.query_selector(self.SELECTORS["job_title"])
                    company_elem = card.query_selector(self.SELECTORS["company"])
                    location_elem = card.query_selector(self.SELECTORS["location"])
                    date_elem = card.query_selector(self.SELECTORS["date_posted"])
                    
                    job_data = {
                        "title": title_elem.inner_text().strip() if title_elem else "",
                        "company": company_elem.inner_text().strip() if company_elem else "",
                        "location": location_elem.inner_text().strip() if location_elem else "Singapore",
                        "date_posted": date_elem.inner_text().strip() if date_elem else "",
                        "experience_level": ""
                    }
                    metadata.append(job_data)
                except:
                    # If individual job parsing fails, add empty metadata
                    metadata.append({
                        "title": "",
                        "company": "",
                        "location": "Singapore",
                        "date_posted": "",
                        "experience_level": ""
                    })
            
            return metadata
        except Exception as e:
            print(f"Error extracting Indeed metadata: {e}")
            return []