"""Data models for skills processing pipeline"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class ExtractedSkill:
    """Skill extracted from job description"""
    skill_name: str
    confidence: float  # 0.0-1.0
    evidence: List[str] = field(default_factory=list)
    category_hint: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "category_hint": self.category_hint
        }


@dataclass
class JobClassification:
    """Job classification result"""
    url: str
    job_title: str
    job_role: Optional[str]  # From job_listings table
    experience_level: str
    role_sub_cluster: Optional[str]  # Just the sub-cluster name (e.g., "Computer Vision")
    cluster_type: Optional[str]  # "specific" or "generalist"
    classification_confidence: float
    job_sector: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "job_title": self.job_title,
            "job_role": self.job_role,
            "experience_level": self.experience_level,
            "role_sub_cluster": self.role_sub_cluster,
            "cluster_type": self.cluster_type,
            "classification_confidence": self.classification_confidence,
            "job_sector": self.job_sector
        }


@dataclass
class JobProcessingResult:
    """Complete result from processing a single job"""
    url: str
    job_title: str
    classification: JobClassification
    skills: List[ExtractedSkill]
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "job_title": self.job_title,
            "classification": self.classification.to_dict(),
            "skills": [s.to_dict() for s in self.skills],
            "success": self.success,
            "error_message": self.error_message
        }
