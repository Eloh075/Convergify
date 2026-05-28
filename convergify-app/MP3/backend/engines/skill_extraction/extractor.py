"""
Skill Extraction Engine

Extracts skills from job descriptions using LLM with confidence scoring
and evidence tracking.
"""
import logging
import re
from typing import List, Optional
import json

from ..gemini_client import GeminiClient
from ..config import EngineConfig
from .models import ExtractedSkill

logger = logging.getLogger(__name__)


class SkillExtractor:
    """Main skill extraction engine"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize skill extractor
        
        Args:
            gemini_api_key: Gemini API key (defaults to config)
        """
        self.llm_client = GeminiClient(gemini_api_key)
        self.confidence_threshold = EngineConfig.SKILL_CONFIDENCE_THRESHOLD
        self.max_skills = EngineConfig.MAX_SKILLS_PER_JOB
    
    def extract_skills(
        self, 
        job_description: str, 
        job_title: str
    ) -> List[ExtractedSkill]:
        """
        Extract skills from job description
        
        Args:
            job_description: Full job description text
            job_title: Job title for context
            
        Returns:
            List of ExtractedSkill objects with confidence scores
        """
        logger.info(f"Extracting skills from job: {job_title}")
        
        # Preprocess text
        cleaned_description = self._preprocess_text(job_description)
        
        # Build extraction prompt
        prompt = self._build_extraction_prompt(cleaned_description, job_title)
        
        # Call LLM
        try:
            response = self.llm_client.generate_json(prompt)
            
            # Parse response
            skills = self._parse_llm_response(response, cleaned_description)
            
            # Filter by confidence threshold
            filtered_skills = [
                skill for skill in skills 
                if skill.confidence >= self.confidence_threshold
            ]
            
            # Limit to max skills
            filtered_skills = filtered_skills[:self.max_skills]
            
            logger.info(f"Extracted {len(filtered_skills)} skills (filtered from {len(skills)})")
            return filtered_skills
            
        except Exception as e:
            logger.error(f"Failed to extract skills: {str(e)}")
            # Return empty list on failure (graceful degradation)
            return []
    
    def _preprocess_text(self, text: str) -> str:
        """
        Clean and normalize job description text
        
        Args:
            text: Raw job description
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might confuse the LLM
        text = re.sub(r'[^\w\s\-\+\#\.\,\:\;\(\)]', '', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    def _build_extraction_prompt(
        self, 
        job_description: str, 
        job_title: str
    ) -> str:
        """
        Build LLM prompt for skill extraction
        
        Args:
            job_description: Cleaned job description
            job_title: Job title
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Job Title: {job_title}

Job Description:
{job_description}

Extract ALL skills mentioned in this job description. For each skill:
1. Identify the skill name (be specific, e.g., "Python" not just "programming")
2. Rate confidence (0.0-1.0) based on how explicitly it's mentioned:
   - 1.0: Explicitly required (e.g., "5+ years of Python required")
   - 0.8-0.9: Strongly implied (e.g., "Experience with Python development")
   - 0.6-0.7: Mentioned but not emphasized (e.g., "Familiarity with Python")
   - 0.4-0.5: Weakly implied (e.g., "Knowledge of programming languages")
3. Extract the exact text snippet(s) that mention this skill (up to 3 snippets)
4. Suggest a category hint (e.g., "Programming Language", "Framework", "Tool", "Soft Skill")

Return as JSON array with this exact structure:
[
  {{
    "skill_name": "Python",
    "confidence": 0.95,
    "evidence": ["5+ years of Python experience", "Expert in Python development"],
    "category_hint": "Programming Language"
  }},
  {{
    "skill_name": "Leadership",
    "confidence": 0.85,
    "evidence": ["Lead a team of developers"],
    "category_hint": "Soft Skill"
  }}
]

Important:
- Extract BOTH technical and soft skills
- Be specific with skill names
- Include evidence text exactly as it appears
- Confidence should reflect how explicitly the skill is required
- Return ONLY the JSON array, no other text
"""
        return prompt
    
    def _parse_llm_response(
        self, 
        response: dict, 
        original_text: str
    ) -> List[ExtractedSkill]:
        """
        Parse LLM response into structured skill objects
        
        Args:
            response: JSON response from LLM
            original_text: Original job description for validation
            
        Returns:
            List of ExtractedSkill objects
        """
        skills = []
        
        # Handle both direct array and wrapped response
        if isinstance(response, list):
            skills_data = response
        elif isinstance(response, dict) and 'skills' in response:
            skills_data = response['skills']
        else:
            logger.warning(f"Unexpected response format: {type(response)}")
            return []
        
        for skill_data in skills_data:
            try:
                # Validate required fields
                if 'skill_name' not in skill_data or 'confidence' not in skill_data:
                    logger.warning(f"Skipping skill with missing fields: {skill_data}")
                    continue
                
                # Validate evidence exists in original text
                evidence = skill_data.get('evidence', [])
                validated_evidence = []
                
                for ev in evidence:
                    # Check if evidence appears in original text (case-insensitive)
                    if ev.lower() in original_text.lower():
                        validated_evidence.append(ev)
                    else:
                        logger.debug(f"Evidence not found in text: {ev}")
                
                # Create ExtractedSkill object
                skill = ExtractedSkill(
                    skill_name=skill_data['skill_name'].strip(),
                    confidence=float(skill_data['confidence']),
                    evidence=validated_evidence,
                    category_hint=skill_data.get('category_hint')
                )
                
                skills.append(skill)
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Failed to parse skill: {skill_data}, error: {str(e)}")
                continue
        
        return skills
