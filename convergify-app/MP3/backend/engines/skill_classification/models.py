"""
Skills Classification Models

Data models for classified skills, normalization, and frequency data.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class ClassifiedSkill:
    """Skill with full classification"""
    raw_skill: str
    canonical_name: str
    tier1: str  # Technical, Business/Ops, Soft Skills
    tier2: str  # Programming Languages, Frameworks, etc.
    importance: str  # Must-have, Nice-to-have, Preferred
    skill_type: str  # Tool, Concept, Certification, Other
    experience_context: Optional[str] = None  # "5+ years", "Expert level", etc.
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate fields"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        valid_importance = ["Must-have", "Nice-to-have", "Preferred"]
        if self.importance not in valid_importance:
            raise ValueError(f"Importance must be one of {valid_importance}, got {self.importance}")
        
        valid_types = ["Tool", "Concept", "Certification", "Other"]
        if self.skill_type not in valid_types:
            raise ValueError(f"Skill type must be one of {valid_types}, got {self.skill_type}")
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'raw_skill': self.raw_skill,
            'canonical_name': self.canonical_name,
            'tier1': self.tier1,
            'tier2': self.tier2,
            'importance': self.importance,
            'skill_type': self.skill_type,
            'experience_context': self.experience_context,
            'confidence': self.confidence,
            'evidence': self.evidence
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ClassifiedSkill':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class NormalizedSkillGroup:
    """Group of similar skills normalized to canonical name"""
    canonical_name: str
    variants: List[str]  # ["Python", "python programming", "Python 3.x"]
    tier1: str
    tier2: str
    combined_frequency: float = 0.0
    job_count: int = 0
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'canonical_name': self.canonical_name,
            'variants': self.variants,
            'tier1': self.tier1,
            'tier2': self.tier2,
            'combined_frequency': self.combined_frequency,
            'job_count': self.job_count
        }


@dataclass
class FrequencyData:
    """Market frequency data for a skill"""
    skill_name: str
    raw_frequency: int  # Total occurrences
    normalized_frequency: float  # 0.0 to 1.0 (percentage of jobs)
    context_breakdown: Dict[str, int] = field(default_factory=dict)  # Frequency by job category
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'skill_name': self.skill_name,
            'raw_frequency': self.raw_frequency,
            'normalized_frequency': self.normalized_frequency,
            'context_breakdown': self.context_breakdown
        }


@dataclass
class ClassifiedJob:
    """Job with classified skills"""
    job_id: str
    job_title: str
    classified_skills: List[ClassifiedSkill]
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'job_id': self.job_id,
            'job_title': self.job_title,
            'classified_skills': [s.dict() for s in self.classified_skills]
        }


@dataclass
class ProcessingStats:
    """Statistics about classification processing"""
    total_jobs: int
    total_skills_extracted: int
    unique_skills_after_normalization: int
    llm_calls_made: int
    processing_time_seconds: float
    cache_hits: int = 0
    cache_misses: int = 0
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'total_jobs': self.total_jobs,
            'total_skills_extracted': self.total_skills_extracted,
            'unique_skills_after_normalization': self.unique_skills_after_normalization,
            'llm_calls_made': self.llm_calls_made,
            'processing_time_seconds': self.processing_time_seconds,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses
        }


@dataclass
class ClassificationResult:
    """Result of batch classification"""
    classified_jobs: List[ClassifiedJob]
    normalized_skills: Dict[str, NormalizedSkillGroup]
    market_frequencies: Dict[str, FrequencyData]
    processing_stats: ProcessingStats
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'classified_jobs': [j.dict() for j in self.classified_jobs],
            'normalized_skills': {k: v.dict() for k, v in self.normalized_skills.items()},
            'market_frequencies': {k: v.dict() for k, v in self.market_frequencies.items()},
            'processing_stats': self.processing_stats.dict()
        }


@dataclass
class JobSkills:
    """Container for all skills from a job"""
    job_id: str
    job_title: str
    skills: List  # List of ExtractedSkill objects
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'job_id': self.job_id,
            'job_title': self.job_title,
            'skills': [s.dict() for s in self.skills]
        }
