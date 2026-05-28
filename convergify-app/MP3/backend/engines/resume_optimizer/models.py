"""
Resume Optimizer Models

Data models for optimized resumes and change tracking.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Change:
    """Single change in resume"""
    change_type: str  # Enhancement, Reordering, Formatting, Clarification
    original_text: str
    optimized_text: str
    reason: str
    location: str  # Section name (Experience, Skills, etc.)
    confidence: float = 0.8
    
    def __post_init__(self):
        """Validate fields"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        valid_types = ["Enhancement", "Reordering", "Formatting", "Clarification"]
        if self.change_type not in valid_types:
            raise ValueError(f"Change type must be one of {valid_types}, got {self.change_type}")
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'change_type': self.change_type,
            'original_text': self.original_text,
            'optimized_text': self.optimized_text,
            'reason': self.reason,
            'location': self.location,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Change':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class OptimizedResume:
    """Optimized resume with change tracking"""
    optimized_text: str
    changes: List[Change] = field(default_factory=list)
    validation_passed: bool = True
    optimization_summary: str = ""
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'optimized_text': self.optimized_text,
            'changes': [c.dict() for c in self.changes],
            'validation_passed': self.validation_passed,
            'optimization_summary': self.optimization_summary
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OptimizedResume':
        """Create from dictionary"""
        changes = [Change.from_dict(c) for c in data.get('changes', [])]
        return cls(
            optimized_text=data['optimized_text'],
            changes=changes,
            validation_passed=data.get('validation_passed', True),
            optimization_summary=data.get('optimization_summary', '')
        )
