"""Base adapter interface for job sites."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SiteAdapter(ABC):
    """Base adapter interface for job sites."""
    
    SELECTORS = {}
    
    @abstractmethod
    def get_site_name(self) -> str:
        """Get the name of the job site."""
        pass
    
    @abstractmethod
    def get_search_url(self, job_title: str, experience_level: str = "") -> str:
        """Generate search URL for job title and experience level."""
        pass
    
    @abstractmethod
    def extract_job_urls_from_page(self, browser) -> List[str]:
        """Extract job URLs from current page."""
        pass
    
    @abstractmethod
    def has_next_page(self, page_html: str) -> bool:
        """Check if there's a next page."""
        pass
    
    @abstractmethod
    def get_next_page_url(self, page_html: str) -> str:
        """Get URL for next page."""
        pass
    
    def extract_job_metadata(self, browser) -> List[Dict[str, Any]]:
        """Extract job metadata from current page."""
        return []