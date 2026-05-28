"""Data models for the MyCareersFuture scraper."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Skill:
    """Represents a skill requirement from a job listing."""
    name: str
    proficiency_level: Optional[str] = None  # beginner, intermediate, advanced
    years_experience: Optional[int] = None
    is_required: bool = True
    skill_category: Optional[str] = None
    framework_mapping: Optional[str] = None  # Skills Framework mapping
    bloom_taxonomy_level: Optional[str] = None  # Bloom's taxonomy mapping


@dataclass
class JobListing:
    """Represents a complete job listing from MyCareersFuture."""
    
    # Core Information
    job_id: str
    title: str
    company_name: str
    company_industry: Optional[str] = None
    company_size: Optional[str] = None
    
    # Job Details
    description: str = ""
    responsibilities: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    employment_type: str = "full-time"  # full-time, part-time, contract, etc.
    seniority_level: Optional[str] = None
    job_category: str = ""
    
    # Skills and Qualifications
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    education_requirements: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    experience_years: Optional[int] = None
    
    # Compensation and Benefits
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "SGD"
    benefits: List[str] = field(default_factory=list)
    
    # Location and Work Arrangement
    location: str = ""
    address: Optional[str] = None
    remote_work_option: bool = False
    work_arrangement: Optional[str] = None  # hybrid, remote, on-site
    
    # Metadata
    posting_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    job_reference_number: Optional[str] = None
    original_url: str = ""
    
    # Data Quality
    extraction_confidence: float = 0.0
    data_completeness_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def validate_required_fields(self) -> bool:
        """Validate that required fields are present."""
        return bool(self.title and self.company_name)
    
    def calculate_completeness_score(self) -> float:
        """Calculate data completeness score based on filled fields."""
        total_fields = 0
        filled_fields = 0
        
        # Core fields (weighted more heavily)
        core_fields = [
            self.title, self.company_name, self.description, 
            self.location, self.employment_type
        ]
        for field in core_fields:
            total_fields += 2  # Weight core fields more
            if field:
                filled_fields += 2
        
        # Optional fields
        optional_fields = [
            self.company_industry, self.company_size, self.seniority_level,
            self.job_category, self.salary_min, self.salary_max, self.address,
            self.posting_date, self.job_reference_number
        ]
        for field in optional_fields:
            total_fields += 1
            if field:
                filled_fields += 1
        
        # List fields
        list_fields = [
            self.responsibilities, self.requirements, self.required_skills,
            self.education_requirements, self.benefits
        ]
        for field in list_fields:
            total_fields += 1
            if field:
                filled_fields += 1
        
        self.data_completeness_score = filled_fields / total_fields if total_fields > 0 else 0.0
        return self.data_completeness_score