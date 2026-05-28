"""
Strategic Analysis Models

Data models for semantic matching, evidence extraction, and analysis results.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Evidence:
    """Evidence of skill from resume"""
    found: bool
    text_snippets: List[str] = field(default_factory=list)
    origin_locations: List[str] = field(default_factory=list)  # ["Experience", "Skills"]
    timeline: Optional[str] = None  # "2018-2023", "5+ years", etc.
    confidence: float = 0.0
    
    def __post_init__(self):
        """Validate fields"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'found': self.found,
            'text_snippets': self.text_snippets,
            'origin_locations': self.origin_locations,
            'timeline': self.timeline,
            'confidence': self.confidence
        }


@dataclass
class SkillMatch:
    """Result of matching a skill"""
    skill_name: str
    canonical_name: str
    match_status: str  # Strong Match, Partial Match, Missing
    match_type: str  # Exact, Semantic, Substitution, None
    confidence_score: float
    evidence: Evidence
    substitution_reasoning: Optional[str] = None
    importance: str = "Preferred"  # Must-have, Nice-to-have, Preferred
    market_frequency: float = 0.0
    
    def __post_init__(self):
        """Validate fields"""
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {self.confidence_score}")
        
        valid_match_status = ["Strong Match", "Partial Match", "Missing"]
        if self.match_status not in valid_match_status:
            raise ValueError(f"Match status must be one of {valid_match_status}, got {self.match_status}")
        
        valid_match_type = ["Exact", "Semantic", "Substitution", "None"]
        if self.match_type not in valid_match_type:
            raise ValueError(f"Match type must be one of {valid_match_type}, got {self.match_type}")
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'skill_name': self.skill_name,
            'canonical_name': self.canonical_name,
            'match_status': self.match_status,
            'match_type': self.match_type,
            'confidence_score': self.confidence_score,
            'evidence': self.evidence.dict(),
            'substitution_reasoning': self.substitution_reasoning,
            'importance': self.importance,
            'market_frequency': self.market_frequency
        }


@dataclass
class Recommendation:
    """Detailed recommendation"""
    priority: str  # High, Medium, Low
    category: str  # Skill Development, Resume Optimization, Application Strategy
    title: str
    description: str  # Detailed text with reasoning
    action_items: List[str] = field(default_factory=list)
    evidence_references: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate fields"""
        valid_priority = ["High", "Medium", "Low"]
        if self.priority not in valid_priority:
            raise ValueError(f"Priority must be one of {valid_priority}, got {self.priority}")
        
        valid_category = ["Skill Development", "Resume Optimization", "Application Strategy"]
        if self.category not in valid_category:
            raise ValueError(f"Category must be one of {valid_category}, got {self.category}")
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'priority': self.priority,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'action_items': self.action_items,
            'evidence_references': self.evidence_references
        }


@dataclass
class AnalysisSummary:
    """Summary of analysis"""
    total_skills_required: int
    strong_matches: int
    partial_matches: int
    missing_skills: int
    overall_readiness: str  # Ready, Needs Development, Not Ready
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'total_skills_required': self.total_skills_required,
            'strong_matches': self.strong_matches,
            'partial_matches': self.partial_matches,
            'missing_skills': self.missing_skills,
            'overall_readiness': self.overall_readiness
        }


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    overall_match_score: float
    category_scores: Dict[str, float]  # Must-have: 85%, Nice-to-have: 70%
    skill_matches: List[SkillMatch]
    recommendations: List[Recommendation]
    summary: AnalysisSummary
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'overall_match_score': self.overall_match_score,
            'category_scores': self.category_scores,
            'skill_matches': [sm.dict() for sm in self.skill_matches],
            'recommendations': [r.dict() for r in self.recommendations],
            'summary': self.summary.dict()
        }


@dataclass
class TopSkill:
    """Top skill by market demand"""
    skill_name: str
    demand_percentage: float
    job_count: int
    growth_trend: str = "stable"  # increasing, stable, decreasing
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'skill_name': self.skill_name,
            'demand_percentage': self.demand_percentage,
            'job_count': self.job_count,
            'growth_trend': self.growth_trend
        }


@dataclass
class MarketInsights:
    """Market intelligence data"""
    total_jobs_analyzed: int
    top_skills_by_demand: List[TopSkill]
    must_have_skills: List[str]
    nice_to_have_skills: List[str]
    competition_level: str  # High, Medium, Low
    skill_trends: Dict[str, str] = field(default_factory=dict)  # skill -> "increasing"/"stable"/"decreasing"
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        # Handle top_skills_by_demand being either TopSkill objects or dicts
        if self.top_skills_by_demand and isinstance(self.top_skills_by_demand[0], dict):
            top_skills_data = self.top_skills_by_demand
        else:
            top_skills_data = [ts.dict() for ts in self.top_skills_by_demand]
        
        return {
            'total_jobs_analyzed': self.total_jobs_analyzed,
            'top_skills_by_demand': top_skills_data,
            'must_have_skills': self.must_have_skills,
            'nice_to_have_skills': self.nice_to_have_skills,
            'competition_level': self.competition_level,
            'skill_trends': self.skill_trends
        }


@dataclass
class SkillGap:
    """Prioritized skill gap"""
    skill_name: str
    importance: str
    market_frequency: float
    priority_score: float
    reasoning: str
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'skill_name': self.skill_name,
            'importance': self.importance,
            'market_frequency': self.market_frequency,
            'priority_score': self.priority_score,
            'reasoning': self.reasoning
        }


@dataclass
class CanonicalGroup:
    """
    Represents a canonical skill with its child variants
    """
    canonical_name: str                    # e.g., "Artificial Intelligence (AI)"
    child_skills: List[str]                # e.g., ["AI", "Generative AI", "AI Agents"]
    child_frequencies: Dict[str, int]      # e.g., {"AI": 3, "Generative AI": 2}
    total_job_mentions: int                # Total unique jobs mentioning any child
    aggregated_frequency: float            # total_job_mentions / total_jobs
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'canonical_name': self.canonical_name,
            'child_skills': self.child_skills,
            'child_frequencies': self.child_frequencies,
            'total_job_mentions': self.total_job_mentions,
            'aggregated_frequency': self.aggregated_frequency
        }


@dataclass
class MarketIntelligenceResult(AnalysisResult):
    """Extended result with market intelligence"""
    market_insights: MarketInsights = None
    top_skills: List[TopSkill] = field(default_factory=list)
    skill_gaps_prioritized: List[SkillGap] = field(default_factory=list)
    canonical_groups: Dict[str, 'CanonicalGroup'] = field(default_factory=dict)
    
    def dict(self) -> dict:
        """Convert to dictionary"""
        base_dict = super().dict()
        base_dict.update({
            'market_insights': self.market_insights.dict() if self.market_insights else None,
            'top_skills': [ts.dict() for ts in self.top_skills],
            'skill_gaps_prioritized': [sg.dict() for sg in self.skill_gaps_prioritized],
            'canonical_groups': {k: v.dict() for k, v in self.canonical_groups.items()}
        })
        return base_dict
