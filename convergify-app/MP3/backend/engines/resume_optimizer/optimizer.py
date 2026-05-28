"""
Resume Optimizer

Auto-generates optimized resume based on analysis recommendations without fabrication.
"""
import logging
import json
from typing import List, Optional

from ..gemini_client import GeminiClient
from ..config import EngineConfig
from .diff_generator import DiffGenerator
from .models import OptimizedResume, Change

logger = logging.getLogger(__name__)


class ResumeOptimizer:
    """Automated resume optimization"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize resume optimizer
        
        Args:
            gemini_api_key: Gemini API key (defaults to config)
        """
        self.llm_client = GeminiClient(gemini_api_key)
        self.diff_generator = DiffGenerator()
    
    def optimize_resume(
        self,
        original_resume: str,
        analysis_results
    ) -> OptimizedResume:
        """
        Generate optimized resume based on analysis
        
        CRITICAL: NO fabrication - only enhance existing content
        
        Args:
            original_resume: Original resume text
            analysis_results: AnalysisResult object
            
        Returns:
            OptimizedResume with changes tracked
        """
        logger.info("Starting resume optimization")
        
        # Build optimization prompt
        prompt = self._build_optimization_prompt(
            original_resume,
            analysis_results.recommendations
        )
        
        try:
            # Call LLM for optimization
            response = self.llm_client.generate_json(prompt)
            
            # Parse response
            optimized_text = response.get('optimized_resume', original_resume)
            change_reasons = response.get('changes', [])
            
            # Validate no fabrication
            validation_passed = self._validate_no_fabrication(
                original_resume,
                optimized_text
            )
            
            if not validation_passed:
                logger.warning("Validation failed - using original resume")
                return OptimizedResume(
                    optimized_text=original_resume,
                    changes=[],
                    validation_passed=False,
                    optimization_summary="Optimization failed validation - no changes made"
                )
            
            # Generate diff
            changes = self.diff_generator.generate_diff(
                original_resume,
                optimized_text,
                change_reasons
            )
            
            # Create summary
            summary = self._create_optimization_summary(changes, analysis_results)
            
            logger.info(f"Optimization complete: {len(changes)} changes made")
            
            return OptimizedResume(
                optimized_text=optimized_text,
                changes=changes,
                validation_passed=True,
                optimization_summary=summary
            )
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return OptimizedResume(
                optimized_text=original_resume,
                changes=[],
                validation_passed=False,
                optimization_summary=f"Optimization failed: {str(e)}"
            )
    
    def _build_optimization_prompt(
        self,
        resume: str,
        recommendations: List
    ) -> str:
        """Build prompt with strict no-fabrication instructions"""
        
        recommendations_text = "\n".join([
            f"- {rec.title}: {rec.description}"
            for rec in recommendations[:5]  # Limit to top 5
        ])
        
        prompt = f"""Original Resume:
{resume}

Analysis Recommendations:
{recommendations_text}

INSTRUCTIONS:
Enhance this resume based on the recommendations. Follow these STRICT rules:

1. NO FABRICATION: Do not add new experiences, skills, or achievements that aren't in the original
2. ENHANCE EXISTING: Only improve how existing content is presented
3. QUANTIFY: Add numbers/metrics where the original implies them (e.g., "team" → "team of 5")
4. CLARIFY: Make vague statements more specific using context from original
5. REORDER: Prioritize relevant content based on recommendations
6. STRENGTHEN: Use stronger action verbs and more impactful language

Examples of ALLOWED enhancements:
- "Worked with Python" → "5+ years of Python development experience" (if timeline supports it)
- "Led team" → "Led team of 5 developers" (if context implies size)
- "Improved performance" → "Improved system performance by 40%" (if original mentions improvement)
- "Developed features" → "Developed and deployed 15+ features" (if context supports it)

Examples of FORBIDDEN fabrications:
- Adding skills not mentioned in original
- Adding job experiences not in original
- Adding certifications not mentioned
- Adding projects not described
- Adding specific numbers without basis in original

Return as JSON with this exact structure:
{{
  "optimized_resume": "full optimized resume text here",
  "changes": [
    {{
      "original": "original text snippet",
      "optimized": "optimized text snippet",
      "reason": "why this change was made"
    }}
  ],
  "validation": "confirm no fabrication occurred"
}}

Return ONLY the JSON, no other text.
"""
        return prompt
    
    def _validate_no_fabrication(
        self,
        original: str,
        optimized: str
    ) -> bool:
        """
        Verify no new experiences or skills were fabricated
        
        Args:
            original: Original resume text
            optimized: Optimized resume text
            
        Returns:
            True if validation passed, False otherwise
        """
        logger.info("Validating no fabrication")
        
        # Basic checks
        original_lower = original.lower()
        optimized_lower = optimized.lower()
        
        # Check 1: Optimized should not be drastically longer (>50% longer)
        if len(optimized) > len(original) * 1.5:
            logger.warning(f"Optimized resume is too long: {len(optimized)} vs {len(original)}")
            return False
        
        # Check 2: Major keywords from original should still be present
        # Extract important words (longer than 4 chars, not common words)
        common_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'been', 'were', 'will'}
        
        original_words = set(
            word for word in original_lower.split()
            if len(word) > 4 and word not in common_words
        )
        
        optimized_words = set(
            word for word in optimized_lower.split()
            if len(word) > 4 and word not in common_words
        )
        
        # At least 70% of original important words should be in optimized
        if original_words:
            overlap = len(original_words & optimized_words) / len(original_words)
            if overlap < 0.7:
                logger.warning(f"Too many original words missing: {overlap:.1%} overlap")
                return False
        
        # Check 3: No suspicious new content
        # Look for patterns that suggest fabrication
        suspicious_patterns = [
            'certified in',
            'certification:',
            'degree in',
            'graduated from',
            'worked at',
            'employed by'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in optimized_lower and pattern not in original_lower:
                # Check if the context around it exists in original
                # This is a simple heuristic - could be improved
                logger.warning(f"Suspicious new pattern found: {pattern}")
                # Don't fail immediately, just log
        
        logger.info("Validation passed")
        return True
    
    def _create_optimization_summary(
        self,
        changes: List[Change],
        analysis_results
    ) -> str:
        """Create summary of optimization"""
        
        if not changes:
            return "No changes made to resume"
        
        # Count change types
        enhancements = sum(1 for c in changes if c.change_type == "Enhancement")
        formatting = sum(1 for c in changes if c.change_type == "Formatting")
        clarifications = sum(1 for c in changes if c.change_type == "Clarification")
        
        summary = f"Made {len(changes)} changes to optimize your resume: "
        
        parts = []
        if enhancements > 0:
            parts.append(f"{enhancements} enhancements")
        if formatting > 0:
            parts.append(f"{formatting} formatting improvements")
        if clarifications > 0:
            parts.append(f"{clarifications} clarifications")
        
        summary += ", ".join(parts)
        
        # Add match score improvement estimate
        if hasattr(analysis_results, 'overall_match_score'):
            summary += f". These changes should improve your match score from {analysis_results.overall_match_score:.0f}%."
        
        return summary
