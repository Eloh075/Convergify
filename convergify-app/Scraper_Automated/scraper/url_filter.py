"""URL filter for filtering out unwanted job URLs."""

from typing import List


class URLFilter:
    """Filters job URLs based on various criteria."""
    
    def __init__(self):
        """Initialize URL filter."""
        self.excluded_patterns = [
            "event=SuggestedJob",  # Skills Career recommended jobs
            "sponsored",           # Sponsored job listings
            "promoted",           # Promoted job listings
        ]
    
    def filter_urls(self, urls: List[str]) -> List[str]:
        """Filter out unwanted URLs."""
        filtered_urls = []
        
        for url in urls:
            if self.should_include_url(url):
                filtered_urls.append(url)
        
        return filtered_urls
    
    def should_include_url(self, url: str) -> bool:
        """Check if URL should be included."""
        # Check for excluded patterns
        for pattern in self.excluded_patterns:
            if pattern in url:
                return False
        
        # Check for valid job URL patterns
        if self.is_valid_job_url(url):
            return True
        
        return False
    
    def is_valid_job_url(self, url: str) -> bool:
        """Check if URL is a valid job listing URL."""
        valid_patterns = [
            "/jobs/view/",          # LinkedIn job URLs
            "/job/",                # Skills Career job URLs
            "/viewjob?jk=",         # Indeed job URLs
        ]
        
        return any(pattern in url for pattern in valid_patterns)
    
    def is_job_apps_card(self, url: str) -> bool:
        """Check if URL is a job apps card (not a real job)."""
        job_apps_patterns = [
            "job-apps",
            "application",
            "apply-now"
        ]
        
        return any(pattern in url.lower() for pattern in job_apps_patterns)