"""
Strategic Analysis Engine

Semantic matching with evidence extraction and comprehensive recommendations.
"""
from .analyzer import StrategicAnalyzer
from .evidence_extractor import EvidenceExtractor
from .models import (
    Evidence,
    SkillMatch,
    Recommendation,
    AnalysisSummary,
    AnalysisResult,
    TopSkill,
    MarketInsights,
    SkillGap,
    MarketIntelligenceResult
)

__all__ = [
    'StrategicAnalyzer',
    'EvidenceExtractor',
    'Evidence',
    'SkillMatch',
    'Recommendation',
    'AnalysisSummary',
    'AnalysisResult',
    'TopSkill',
    'MarketInsights',
    'SkillGap',
    'MarketIntelligenceResult'
]
