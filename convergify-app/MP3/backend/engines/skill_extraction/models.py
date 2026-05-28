"""
Data models for Skill Extraction Engine
"""
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class ExtractedSkill:
    """Represents a skill extracted from a job description"""
    
    skill_name: str
    confidence: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)  # Text snippets from job description
    category_hint: Optional[str] = None  # Initial category suggestion
    
    def __post_init__(self):
        """Validate the extracted skill data"""
        if not self.skill_name or not self.skill_name.strip():
            raise ValueError("skill_name cannot be empty")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        if not isinstance(self.evidence, list):
            raise ValueError("evidence must be a list")
    
    def dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'skill_name': self.skill_name,
            'confidence': self.confidence,
            'evidence': self.evidence,
            'category_hint': self.category_hint
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ExtractedSkill':
        """Create from dictionary"""
        return cls(
            skill_name=data['skill_name'],
            confidence=data['confidence'],
            evidence=data.get('evidence', []),
            category_hint=data.get('category_hint')
        )


@dataclass
class JobSkills:
    """Container for all skills extracted from a job"""
    
    job_id: str
    job_title: str
    skills: List[ExtractedSkill] = field(default_factory=list)
    
    def dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'job_id': self.job_id,
            'job_title': self.job_title,
            'skills': [skill.dict() for skill in self.skills]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'JobSkills':
        """Create from dictionary"""
        return cls(
            job_id=data['job_id'],
            job_title=data['job_title'],
            skills=[ExtractedSkill.from_dict(s) for s in data.get('skills', [])]
        )
