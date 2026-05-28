"""
Skills Classification Engine

Batch classification of skills with normalization and frequency calculation.
"""
import logging
import json
import time
from typing import List, Dict, Tuple
from collections import defaultdict

from ..gemini_client import GeminiClient
from ..config import EngineConfig
from .taxonomy import SkillTaxonomy
from .models import (
    ClassifiedSkill, ClassifiedJob, NormalizedSkillGroup,
    FrequencyData, ClassificationResult, ProcessingStats, JobSkills
)

logger = logging.getLogger(__name__)


class SkillClassifier:
    """Batch skill classification engine"""
    
    def __init__(self, gemini_api_key: str = None):
        """
        Initialize skill classifier
        
        Args:
            gemini_api_key: Gemini API key (defaults to config)
        """
        self.llm_client = GeminiClient(gemini_api_key)
        self.taxonomy = SkillTaxonomy()
    
    def classify_skills_batch(
        self, 
        all_jobs_skills: List[JobSkills]
    ) -> ClassificationResult:
        """
        Classify all skills from multiple jobs together
        
        Args:
            all_jobs_skills: List of JobSkills objects
            
        Returns:
            ClassificationResult with normalized skills and frequencies
        """
        start_time = time.time()
        logger.info(f"Starting batch classification for {len(all_jobs_skills)} jobs")
        
        # Step 1: Collect all unique skills
        all_skills = []
        for job_skills in all_jobs_skills:
            all_skills.extend(job_skills.skills)
        
        logger.info(f"Total skills to classify: {len(all_skills)}")
        
        # Step 2: Normalize skills (group similar ones)
        # Pass all_jobs_skills to track unique jobs per skill
        normalized_skills = self._normalize_skills(all_skills, all_jobs_skills)
        logger.info(f"Normalized to {len(normalized_skills)} unique skills")
        
        # Step 3: Classify using LLM (batch)
        classified_skills_map = self._classify_batch_llm(normalized_skills, all_jobs_skills)
        
        # Step 4: Calculate market frequencies
        market_frequencies = self._calculate_frequencies(
            normalized_skills, 
            len(all_jobs_skills)
        )
        
        # Step 5: Determine importance based on frequency (store in map)
        importance_map = {}
        for skill_name, freq_data in market_frequencies.items():
            importance = self._determine_importance(
                skill_name, 
                freq_data.normalized_frequency
            )
            importance_map[skill_name] = importance
        
        # Step 6: Build classified jobs
        classified_jobs = []
        for job_skills in all_jobs_skills:
            classified_skills_list = []
            for skill in job_skills.skills:
                # Find canonical name
                canonical_name = skill.skill_name
                for norm_name, norm_group in normalized_skills.items():
                    if skill.skill_name.lower() in [v.lower() for v in norm_group.variants]:
                        canonical_name = norm_name
                        break
                
                # Get classification from map
                if canonical_name in classified_skills_map:
                    classified_skill = classified_skills_map[canonical_name]
                    # Update with original skill's evidence and confidence
                    classified_skill.evidence = skill.evidence
                    classified_skill.confidence = skill.confidence
                    classified_skill.raw_skill = skill.skill_name
                    # Update importance from map
                    if canonical_name in importance_map:
                        classified_skill.importance = importance_map[canonical_name]
                    classified_skills_list.append(classified_skill)
            
            classified_jobs.append(ClassifiedJob(
                job_id=job_skills.job_id,
                job_title=job_skills.job_title,
                classified_skills=classified_skills_list
            ))
        
        # Step 7: Build processing stats
        processing_time = time.time() - start_time
        stats = ProcessingStats(
            total_jobs=len(all_jobs_skills),
            total_skills_extracted=len(all_skills),
            unique_skills_after_normalization=len(normalized_skills),
            llm_calls_made=1,  # Batch call
            processing_time_seconds=processing_time
        )
        
        logger.info(f"Classification complete in {processing_time:.2f}s")
        
        return ClassificationResult(
            classified_jobs=classified_jobs,
            normalized_skills=normalized_skills,
            market_frequencies=market_frequencies,
            processing_stats=stats
        )
    
    def _normalize_skills(
        self, 
        all_skills: List,
        all_jobs_skills: List = None
    ) -> Dict[str, NormalizedSkillGroup]:
        """
        Group similar skills under canonical names
        
        Args:
            all_skills: List of ExtractedSkill objects
            all_jobs_skills: List of JobSkills objects (for tracking unique jobs)
            
        Returns:
            Dictionary mapping canonical name to NormalizedSkillGroup
        """
        # Group by lowercase name first, tracking which jobs have each skill
        skill_groups = defaultdict(lambda: {'variants': [], 'job_ids': set()})
        
        # If we have job context, track which jobs have which skills
        if all_jobs_skills:
            for job_skills in all_jobs_skills:
                for skill in job_skills.skills:
                    normalized = skill.skill_name.lower().strip()
                    skill_groups[normalized]['variants'].append(skill.skill_name)
                    skill_groups[normalized]['job_ids'].add(job_skills.job_id)
        else:
            # Fallback: just group by name (no job tracking)
            for skill in all_skills:
                normalized = skill.skill_name.lower().strip()
                skill_groups[normalized]['variants'].append(skill.skill_name)
        
        # Build normalized groups
        normalized_skills = {}
        for normalized_name, data in skill_groups.items():
            variants = data['variants']
            job_ids = data.get('job_ids', set())
            
            # Use most common variant as canonical (or first one)
            canonical_name = max(set(variants), key=variants.count)
            
            # Get classification from taxonomy
            tier1, tier2 = self.taxonomy.classify_skill(canonical_name)
            
            # FIX: job_count is now the number of UNIQUE JOBS, not total occurrences
            normalized_skills[canonical_name] = NormalizedSkillGroup(
                canonical_name=canonical_name,
                variants=list(set(variants)),  # Unique variants
                tier1=tier1,
                tier2=tier2,
                job_count=len(job_ids) if job_ids else len(variants)  # Unique jobs
            )
        
        return normalized_skills
    
    def _classify_batch_llm(
        self,
        normalized_skills: Dict[str, NormalizedSkillGroup],
        all_jobs_skills: List[JobSkills]
    ) -> Dict[str, ClassifiedSkill]:
        """
        Classify skills using LLM in batch
        
        Args:
            normalized_skills: Normalized skill groups
            all_jobs_skills: All job skills for context
            
        Returns:
            Dictionary mapping canonical name to ClassifiedSkill
        """
        # Build prompt with all skills
        skills_list = [
            {
                'skill_name': name,
                'variants': group.variants,
                'tier1': group.tier1,
                'tier2': group.tier2,
                'frequency': group.job_count
            }
            for name, group in normalized_skills.items()
        ]
        
        prompt = self._build_classification_prompt(skills_list)
        
        try:
            response = self.llm_client.generate_json(prompt)
            # Pass total_jobs for correct frequency calculation
            total_jobs = len(all_jobs_skills)
            return self._parse_classification_response(response, normalized_skills, total_jobs)
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            # NO FALLBACK - fail loudly so we know when LLM isn't working
            raise Exception(f"Skill classification failed: {e}. Check API keys and model availability.")
    
    def _build_classification_prompt(self, skills_list: List[dict]) -> str:
        """Build LLM prompt for batch classification"""
        skills_json = json.dumps(skills_list, indent=2)
        
        prompt = f"""You are classifying skills from multiple job postings.

TAXONOMY (use ONLY these categories):
- Technical:
  * Programming Languages (e.g., Python, Java, JavaScript)
  * Frameworks & Libraries (e.g., React, Django, TensorFlow)
  * Cloud & Infrastructure (e.g., AWS, Docker, Kubernetes)
  * Databases (e.g., PostgreSQL, MongoDB, Redis)
  * Tools & Platforms (e.g., Git, Jira, VS Code)
  * Data & Analytics (e.g., Pandas, Tableau, Power BI)
  * Security (e.g., OAuth, Encryption, Penetration Testing)
  * Testing (e.g., Jest, Pytest, Selenium)
- Business/Ops:
  * Project Management (e.g., Agile, Scrum, Kanban)
  * Business Analysis (e.g., Requirements Gathering, Stakeholder Management)
  * Data Analysis (e.g., Excel, SQL, Statistical Analysis)
  * Product Management (e.g., Roadmapping, User Research)
- Soft Skills:
  * Communication (e.g., Presentation, Technical Writing)
  * Leadership (e.g., Team Management, Mentoring)
  * Problem Solving (e.g., Critical Thinking, Debugging)
  * Collaboration (e.g., Cross-functional Teams, Pair Programming)
  * Adaptability (e.g., Learning New Technologies, Flexibility)

Skills to classify:
{skills_json}

For each skill, provide:
1. **tier1** and **tier2** from taxonomy above (must be valid combination)
2. **skill_type**: Tool, Concept, Certification, or Other
3. **experience_context**: Extract any experience level if mentioned (e.g., "5+ years", "Expert", "Senior")

Return as JSON array with this exact structure:
[
  {{
    "skill_name": "Python",
    "tier1": "Technical",
    "tier2": "Programming Languages",
    "skill_type": "Tool",
    "experience_context": "5+ years"
  }},
  {{
    "skill_name": "Leadership",
    "tier1": "Soft Skills",
    "tier2": "Leadership",
    "skill_type": "Concept",
    "experience_context": null
  }},
  {{
    "skill_name": "AWS Certified Solutions Architect",
    "tier1": "Technical",
    "tier2": "Cloud & Infrastructure",
    "skill_type": "Certification",
    "experience_context": null
  }}
]

IMPORTANT:
- Use the exact canonical skill_name from the input
- Validate tier1/tier2 combinations exist in the taxonomy
- skill_type must be one of: Tool, Concept, Certification, Other
- experience_context can be null if not mentioned
- Return ONLY the JSON array, no other text or explanation
"""
        return prompt.strip()
    
    def _parse_classification_response(
        self,
        response: dict,
        normalized_skills: Dict[str, NormalizedSkillGroup],
        total_jobs: int
    ) -> Dict[str, ClassifiedSkill]:
        """Parse LLM classification response"""
        classified_map = {}
        
        # Handle both direct array and wrapped response
        if isinstance(response, list):
            classifications = response
        elif isinstance(response, dict) and 'classifications' in response:
            classifications = response['classifications']
        else:
            logger.error(f"Unexpected response format: {type(response)}")
            raise Exception(f"LLM returned unexpected format: {type(response)}. Expected list or dict with 'classifications' key.")
        
        for item in classifications:
            try:
                skill_name = item['skill_name']
                
                # Validate tier1/tier2
                tier1 = item.get('tier1', 'Technical')
                tier2 = item.get('tier2', 'Tools & Platforms')
                
                if not self.taxonomy.is_valid_classification(tier1, tier2):
                    logger.warning(f"Invalid classification for {skill_name}: {tier1}/{tier2}")
                    tier1, tier2 = self.taxonomy.classify_skill(skill_name)
                
                # Get frequency data for importance
                norm_group = normalized_skills.get(skill_name)
                if norm_group:
                    # FIX: Divide by total_jobs, not number of unique skills
                    frequency = norm_group.job_count / total_jobs if total_jobs > 0 else 0.0
                    importance = self._determine_importance(skill_name, frequency)
                else:
                    importance = "Preferred"
                
                classified_skill = ClassifiedSkill(
                    raw_skill=skill_name,
                    canonical_name=skill_name,
                    tier1=tier1,
                    tier2=tier2,
                    importance=importance,
                    skill_type=item.get('skill_type', 'Other'),
                    experience_context=item.get('experience_context'),
                    confidence=0.0,  # Will be updated with original skill's confidence
                    evidence=[]  # Will be updated with original skill's evidence
                )
                
                classified_map[skill_name] = classified_skill
                
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to parse classification: {item}, error: {e}")
                continue
        
        return classified_map
    
    # REMOVED: _fallback_classification method
    # Per user request: "remove any fallback related data cuz it either should work or show 0"
    # System now fails loudly when LLM classification fails
    
    def _calculate_frequencies(
        self,
        normalized_skills: Dict[str, NormalizedSkillGroup],
        total_jobs: int
    ) -> Dict[str, FrequencyData]:
        """
        Calculate market frequency for each skill
        
        Args:
            normalized_skills: Normalized skill groups
            total_jobs: Total number of jobs analyzed
            
        Returns:
            Dictionary mapping skill name to FrequencyData
        """
        frequencies = {}
        
        for skill_name, norm_group in normalized_skills.items():
            raw_frequency = norm_group.job_count
            normalized_frequency = raw_frequency / total_jobs if total_jobs > 0 else 0.0
            
            frequencies[skill_name] = FrequencyData(
                skill_name=skill_name,
                raw_frequency=raw_frequency,
                normalized_frequency=normalized_frequency,
                context_breakdown={}  # Could be enhanced with job category breakdown
            )
        
        return frequencies
    
    def _determine_importance(
        self,
        skill: str,
        frequency: float
    ) -> str:
        """
        Determine if skill is Must-have, Nice-to-have, or Preferred
        
        Args:
            skill: Skill name
            frequency: Normalized frequency (0.0 to 1.0)
            
        Returns:
            Importance level
        """
        # Must-have: appears in >60% of jobs
        if frequency > 0.6:
            return "Must-have"
        # Nice-to-have: appears in 30-60% of jobs
        elif frequency >= 0.3:
            return "Nice-to-have"
        # Preferred: appears in <30% of jobs
        else:
            return "Preferred"
