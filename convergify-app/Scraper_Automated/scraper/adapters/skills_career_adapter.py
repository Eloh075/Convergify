"""Skills Career adapter for job scraping."""

from typing import List, Dict, Any
from urllib.parse import quote
from .base_adapter import SiteAdapter


class SkillsCareerAdapter(SiteAdapter):
    """Adapter for Skills Career (MyCareersFuture) job site."""
    
    SELECTORS = {
        "job_listings": ".job-card",
        "job_link": ".job-card a",
        "pagination_next": ".pagination .next",
        "job_title": ".job-card__title",
        "company": ".job-card__company",
        "location": ".job-card__location",
        "date_posted": ".job-card__date"
    }
    
    def get_site_name(self) -> str:
        """Get the name of the job site."""
        return "SkillsCareer"
    
    def get_search_url(self, job_title: str, experience_level: str = "") -> str:
        """Generate Skills Career search URL."""
        base_url = "https://www.mycareersfuture.gov.sg/search"
        encoded_query = quote(job_title)
        return f"{base_url}?search={encoded_query}&sortBy=new_posting_date"
    
    def extract_job_urls_from_page(self, browser) -> List[str]:
        """Extract job URLs from Skills Career page."""
        try:
            # Wait for job listings to load
            browser.wait_for_selector(self.SELECTORS["job_listings"], timeout=10000)
            
            # Extract job URLs
            job_links = browser.page.query_selector_all(self.SELECTORS["job_link"])
            urls = []
            
            for link in job_links:
                href = link.get_attribute("href")
                if href:
                    # Skip recommended jobs
                    if "event=SuggestedJob" in href:
                        continue
                    
                    # Make absolute URL if needed
                    if href.startswith("/"):
                        href = f"https://www.mycareersfuture.gov.sg{href}"
                    
                    urls.append(href)
            
            return urls
        except Exception as e:
            print(f"Error extracting Skills Career URLs: {e}")
            return []
    
    def has_next_page(self, page_html: str) -> bool:
        """Check if Skills Career has next page."""
        return "pagination" in page_html and "next" in page_html
    
    def get_next_page_url(self, page_html: str) -> str:
        """Get next page URL for Skills Career."""
        # Skills Career uses URL-based pagination
        current_url = ""  # Would need to get from browser
        if "&page=" in current_url:
            # Increment page number
            parts = current_url.split("&page=")
            page_num = int(parts[1].split("&")[0]) + 1
            return parts[0] + f"&page={page_num}"
        else:
            return current_url + "&page=1"
    
    def extract_job_metadata(self, browser) -> List[Dict[str, Any]]:
        """Extract job metadata from Skills Career page."""
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
            print(f"Error extracting Skills Career metadata: {e}")
            return []