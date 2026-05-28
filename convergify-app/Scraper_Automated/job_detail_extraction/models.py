"""Data models for job detail extraction."""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class JobDetails:
    """Complete job details extracted from a job posting."""
    
    # Basic information
    url: str
    website: str
    job_role: str = ""
    suffix: Optional[str] = None
    
    # Job metadata
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    date_posted: Optional[str] = None
    application_deadline: Optional[str] = None
    
    # Employment terms
    job_type: Optional[str] = None  # Full-time, Part-time, Intern, Contract, Permanent
    experience_level: Optional[str] = None  # Junior, Senior, Mid-level, Entry-level
    seniority_level: Optional[str] = None  # Executive, Professional, Manager, etc.
    salary_range: Optional[str] = None  # e.g., "$6,000 to $7,800 Monthly"
    
    # Classification
    industry: Optional[str] = None
    job_sector: Optional[str] = None
    category: Optional[str] = None
    
    # Content
    description: Optional[str] = None
    skills: Optional[List[str]] = None  # List of skills
    
    # Technical fields
    extracted_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        result = {
            "url": self.url,
            "website": self.website,
            "job_role": self.job_role,
            "suffix": self.suffix,
            "job_title": self.job_title,
            "company": self.company,
            "location": self.location,
            "date_posted": self.date_posted,
            "application_deadline": self.application_deadline,
            "job_type": self.job_type,
            "experience_level": self.experience_level,
            "seniority_level": self.seniority_level,
            "salary_range": self.salary_range,
            "industry": self.industry,
            "job_sector": self.job_sector,
            "category": self.category,
            "description": self.description,
            "skills": self.skills,
            "extracted_at": self.extracted_at.isoformat() if self.extracted_at else None,
            "success": self.success,
            "error_message": self.error_message,
        }
        
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobDetails":
        """Create from dictionary."""
        # Handle datetime conversion
        extracted_at = None
        if "extracted_at" in data and data["extracted_at"]:
            try:
                extracted_at = datetime.fromisoformat(data["extracted_at"])
            except:
                pass
        
        return cls(
            url=data.get("url", ""),
            website=data.get("website", ""),
            job_role=data.get("job_role", ""),
            suffix=data.get("suffix"),
            job_title=data.get("job_title"),
            company=data.get("company"),
            location=data.get("location"),
            date_posted=data.get("date_posted"),
            application_deadline=data.get("application_deadline"),
            job_type=data.get("job_type"),
            experience_level=data.get("experience_level"),
            seniority_level=data.get("seniority_level"),
            salary_range=data.get("salary_range"),
            industry=data.get("industry"),
            job_sector=data.get("job_sector"),
            category=data.get("category"),
            description=data.get("description"),
            skills=data.get("skills"),
            extracted_at=extracted_at,
            success=data.get("success", False),
            error_message=data.get("error_message"),
            raw_data=data.get("raw_data"),
        )