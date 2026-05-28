"""
Skill Canonicalization Cache Model

Caches canonical skill mappings to reduce LLM calls.
"""
from sqlalchemy import Column, String, Float, DateTime, Integer, Index
from datetime import datetime
from database import Base


class SkillCanonical(Base):
    """
    Cache for canonical skill mappings
    
    Maps specific skill names to their canonical parent names.
    Example: "Generative AI" -> "Artificial Intelligence (AI)"
    """
    __tablename__ = "skill_canonical_cache"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_name = Column(String, nullable=False, unique=True, index=True)
    canonical_name = Column(String, nullable=False, index=True)
    confidence = Column(Float, default=1.0)  # LLM confidence in mapping
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Create composite index for faster lookups
    __table_args__ = (
        Index('idx_skill_canonical_lookup', 'skill_name', 'canonical_name'),
    )
    
    def __repr__(self):
        return f"<SkillCanonical(skill='{self.skill_name}', canonical='{self.canonical_name}', confidence={self.confidence})>"
