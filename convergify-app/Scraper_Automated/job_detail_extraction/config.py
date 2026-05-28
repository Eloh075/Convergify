"""Configuration for job detail extraction."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class JobDetailExtractorConfig:
    """Configuration for job detail extraction."""
    
    # Browser settings
    headless_mode: bool = True
    timeout_seconds: int = 30
    delay_between_requests: float = 2.0
    
    # Extraction settings
    max_retries: int = 3
    retry_delay: float = 5.0
    
    # LinkedIn selectors (based on analysis)
    linkedin_selectors: Dict[str, str] = None
    
    # SkillsFuture selectors (based on analysis)
    skillsfuture_selectors: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialize default selectors."""
        if self.linkedin_selectors is None:
            self.linkedin_selectors = {
                "job_title": ".top-card-layout__title",
                "company": ".topcard__org-name-link",
                "location": ".topcard__flavor--bullet",
                "date_posted": ".posted-time-ago__text",
                "description": ".description__text",
                "job_criteria_items": ".description__job-criteria-item",
                "criteria_header": ".description__job-criteria-subheader",
                "criteria_text": ".description__job-criteria-text",
            }
        
        if self.skillsfuture_selectors is None:
            # Using data-testid attributes (most reliable for MyCareersFuture)
            self.skillsfuture_selectors = {
                "job_title": "[data-testid='job-details-info-job-title']",
                "employment_type": "[data-testid='job-details-info-employment-type']",
                "seniority": "[data-testid='job-details-info-seniority']",
                "experience": "[data-testid='job-details-info-min-experience']",
                "location": "[data-testid='job-details-info-location-span']",
                "category": "[data-testid='job-details-info-job-categories']",
                "date_posted": "[data-testid='job-details-info-last-posted-date']",
                "expiry_date": "[data-testid='job-details-info-job-expiry-date']",
                "num_applications": "[data-testid='job-details-info-num-of-applications']",
                "salary_range": "[data-testid='salary-range']",
                "salary_type": "[data-testid='salary-type']",
                "description": "[data-testid='job-description']",
                "skills": "[data-testid='skills-needed']",
                "company_about": "[data-testid='company-info-about']",
                # Fallback selectors
                "job_title_fallback": "h1",
                "salary_fallback": ".salary",
            }


def create_job_detail_config() -> JobDetailExtractorConfig:
    """Create default job detail extractor configuration."""
    return JobDetailExtractorConfig()