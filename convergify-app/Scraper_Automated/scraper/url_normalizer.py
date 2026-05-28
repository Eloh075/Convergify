"""URL normalizer to handle duplicate LinkedIn URLs with different tracking parameters."""

import re
from urllib.parse import urlparse, parse_qs
from loguru import logger


class URLNormalizer:
    """Normalizes URLs to remove tracking parameters and extract canonical job IDs."""
    
    @staticmethod
    def normalize_linkedin_url(url: str) -> str:
        """
        Normalize LinkedIn job URL by extracting the job ID.
        
        Example:
        Input: https://www.linkedin.com/jobs/view/ai-developer-ai-analyst-at-seatrium-4345578671/?refId=...&trackingId=...
        Output: https://www.linkedin.com/jobs/view/4345578671/
        
        Args:
            url: LinkedIn job URL with potential tracking parameters
            
        Returns:
            Normalized URL with just the job ID
        """
        try:
            # Extract job ID from URL path
            # Pattern 1: /jobs/view/[JOB_ID]/ (already normalized)
            match = re.search(r'/jobs/view/(\d+)/?', url)
            if match:
                job_id = match.group(1)
                normalized = f"https://www.linkedin.com/jobs/view/{job_id}/"
                logger.debug(f"Normalized LinkedIn URL: {url} -> {normalized}")
                return normalized
            
            # Pattern 2: /jobs/view/[job-title-slug-JOB_ID]/ (with slug)
            # Job ID is always the last numeric sequence in the path before query params
            match = re.search(r'/jobs/view/[^/]*?(\d{10})/?', url)
            if match:
                job_id = match.group(1)
                normalized = f"https://www.linkedin.com/jobs/view/{job_id}/"
                logger.debug(f"Normalized LinkedIn URL: {url} -> {normalized}")
                return normalized
            
            # Fallback: remove query parameters
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            # Remove trailing slash inconsistencies
            base_url = base_url.rstrip('/') + '/'
            return base_url
            
        except Exception as e:
            logger.warning(f"Failed to normalize LinkedIn URL: {url}, error: {e}")
            return url
    
    @staticmethod
    def normalize_skills_career_url(url: str) -> str:
        """
        Normalize Skills Career (MyCareersFuture) job URL.
        
        Example:
        Input: https://www.mycareersfuture.gov.sg/job/information-technology/ai-engineer-abc123?source=MCF&event=SuggestedJob
        Output: https://www.mycareersfuture.gov.sg/job/information-technology/ai-engineer-abc123
        
        Args:
            url: Skills Career job URL with potential tracking parameters
            
        Returns:
            Normalized URL without query parameters
        """
        try:
            # Remove query parameters (source, event, etc.)
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            return base_url
            
        except Exception as e:
            logger.warning(f"Failed to normalize Skills Career URL: {url}, error: {e}")
            return url
    
    @staticmethod
    def normalize_url(url: str, site: str = "auto") -> str:
        """
        Normalize URL based on site type.
        
        Args:
            url: Job URL to normalize
            site: Site type ("linkedin", "skills_career", or "auto" for auto-detection)
            
        Returns:
            Normalized URL
        """
        if site == "auto":
            if "linkedin.com" in url:
                site = "linkedin"
            elif "mycareersfuture.gov.sg" in url:
                site = "skills_career"
        
        if site == "linkedin":
            return URLNormalizer.normalize_linkedin_url(url)
        elif site == "skills_career":
            return URLNormalizer.normalize_skills_career_url(url)
        else:
            # Unknown site, just remove query parameters
            try:
                parsed = urlparse(url)
                return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            except:
                return url
    
    @staticmethod
    def extract_job_id(url: str) -> str:
        """
        Extract job ID from URL.
        
        Args:
            url: Job URL
            
        Returns:
            Job ID string, or empty string if not found
        """
        try:
            # LinkedIn: extract numeric ID (10 digits)
            if "linkedin.com" in url:
                match = re.search(r'(\d{10})', url)
                if match:
                    return match.group(1)
            
            # Skills Career: extract hash from path
            elif "mycareersfuture.gov.sg" in url:
                match = re.search(r'/job/[^/]+/[^/]+-([a-f0-9]+)', url)
                if match:
                    return match.group(1)
            
            return ""
            
        except Exception as e:
            logger.warning(f"Failed to extract job ID from URL: {url}, error: {e}")
            return ""
