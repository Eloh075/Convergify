"""
Data models for Phase 2 - Skills Normalization
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class CanonicalSkill:
    """Canonical skill representation"""
    id: Optional[int] = None
    canonical_name: str = ""
    
    def dict(self) -> dict:
        return {
            'id': self.id,
            'canonical_name': self.canonical_name
        }


@dataclass
class SkillAlias:
    """Mapping from raw skill to canonical skill"""
    id: Optional[int] = None
    raw_skill: str = ""
    canonical_skill_id: int = 0
    
    def dict(self) -> dict:
        return {
            'id': self.id,
            'raw_skill': self.raw_skill,
            'canonical_skill_id': self.canonical_skill_id
        }


@dataclass
class SkillClassification:
    """Classification of a canonical skill"""
    id: Optional[int] = None
    canonical_skill_id: int = 0
    job_role: str = ""
    tier1: str = ""  # Technical, Business/Ops, Soft Skills
    tier2: str = ""  # Programming Languages, Frameworks, etc.
    skill_type: str = ""  # Tool, Concept, Certification, Other
    experience_context: Optional[str] = None
    
    def dict(self) -> dict:
        return {
            'id': self.id,
            'canonical_skill_id': self.canonical_skill_id,
            'job_role': self.job_role,
            'tier1': self.tier1,
            'tier2': self.tier2,
            'skill_type': self.skill_type,
            'experience_context': self.experience_context
        }


@dataclass
class SkillFrequency:
    """Market frequency data for a skill in a specific context"""
    id: Optional[int] = None
    canonical_skill_id: int = 0
    job_role: str = ""
    role_sub_cluster: Optional[str] = None
    experience_level: str = ""
    cluster_type: str = ""
    raw_frequency: int = 0
    normalized_frequency: float = 0.0
    unique_jobs: int = 0
    total_jobs_in_context: int = 0
    importance: str = ""  # Must-have, Nice-to-have, Preferred
    
    def dict(self) -> dict:
        return {
            'id': self.id,
            'canonical_skill_id': self.canonical_skill_id,
            'job_role': self.job_role,
            'role_sub_cluster': self.role_sub_cluster,
            'experience_level': self.experience_level,
            'cluster_type': self.cluster_type,
            'raw_frequency': self.raw_frequency,
            'normalized_frequency': self.normalized_frequency,
            'unique_jobs': self.unique_jobs,
            'total_jobs_in_context': self.total_jobs_in_context,
            'importance': self.importance
        }


@dataclass
class NormalizationResult:
    """Result of skill normalization"""
    total_raw_skills: int = 0
    already_known: int = 0
    unknown_skills: int = 0
    chunks_created: int = 0
    new_canonical_skills: int = 0
    total_aliases_created: int = 0
    processing_time_seconds: float = 0.0
    
    def dict(self) -> dict:
        return {
            'total_raw_skills': self.total_raw_skills,
            'already_known': self.already_known,
            'unknown_skills': self.unknown_skills,
            'chunks_created': self.chunks_created,
            'new_canonical_skills': self.new_canonical_skills,
            'total_aliases_created': self.total_aliases_created,
            'processing_time_seconds': self.processing_time_seconds
        }


@dataclass
class ClassificationResult:
    """Result of skill classification"""
    job_role: str = ""
    total_skills: int = 0
    classified_skills: int = 0
    processing_time_seconds: float = 0.0
    
    def dict(self) -> dict:
        return {
            'job_role': self.job_role,
            'total_skills': self.total_skills,
            'classified_skills': self.classified_skills,
            'processing_time_seconds': self.processing_time_seconds
        }


@dataclass
class FrequencyResult:
    """Result of frequency calculation"""
    total_contexts: int = 0
    total_skills_processed: int = 0
    processing_time_seconds: float = 0.0
    
    def dict(self) -> dict:
        return {
            'total_contexts': self.total_contexts,
            'total_skills_processed': self.total_skills_processed,
            'processing_time_seconds': self.processing_time_seconds
        }
