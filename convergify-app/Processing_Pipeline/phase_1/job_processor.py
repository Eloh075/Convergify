"""
Job Processor - Extracts classifications and skills from job descriptions
Combines experience level, role sub-cluster, and skills extraction in ONE LLM call
"""
import logging
from typing import Optional
import json

from .gemini_client import GeminiClient
from .config import PipelineConfig
from .models import JobProcessingResult, JobClassification, ExtractedSkill
from .sub_clusters import SUB_CLUSTER_DEFINITIONS

logger = logging.getLogger(__name__)


class JobProcessor:
    """Process jobs to extract classifications and skills"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize job processor"""
        self.llm_client = GeminiClient(gemini_api_key)
        self.confidence_threshold = PipelineConfig.SKILL_CONFIDENCE_THRESHOLD
        self.max_skills = PipelineConfig.MAX_SKILLS_PER_JOB
    
    def process_job(
        self,
        url: str,
        job_title: str,
        job_description: str,
        job_role: Optional[str] = None,
        job_sector: Optional[str] = None
    ) -> JobProcessingResult:
        """
        Process a single job - extract classification and skills in ONE call
        
        Args:
            url: Job URL
            job_title: Job title
            job_description: Full job description text
            job_role: Job role from job_listings table (e.g., "AI Engineer")
            job_sector: Job sector (optional, from job_details table)
            
        Returns:
            JobProcessingResult with classification and skills
        """
        logger.info(f"Processing job: {job_title}")
        
        try:
            # Clean job description: replace smart quotes with straight quotes
            # and fix escape sequences that break JSON parsing
            cleaned_description = job_description
            cleaned_description = cleaned_description.replace('"', '"').replace('"', '"')
            cleaned_description = cleaned_description.replace(''', "'").replace(''', "'")
            cleaned_description = cleaned_description.replace('–', '-').replace('—', '-')  # em/en dashes
            cleaned_description = cleaned_description.replace('\\', '/')  # backslashes to forward slashes
            
            # Build combined prompt (pass job_role to filter sub-clusters)
            prompt = self._build_combined_prompt(job_title, cleaned_description, job_role)
            
            # Call LLM once for everything
            response = self.llm_client.generate_json(prompt)
            
            # Parse response
            classification, skills = self._parse_response(response, url, job_title, job_role, job_sector)
            
            # Filter skills by confidence
            filtered_skills = [
                skill for skill in skills
                if skill.confidence >= self.confidence_threshold
            ][:self.max_skills]
            
            logger.info(
                f"✓ Processed {job_title}: "
                f"{classification.experience_level}, "
                f"{classification.role_sub_cluster or 'No sub-cluster'}, "
                f"{len(filtered_skills)} skills"
            )
            
            return JobProcessingResult(
                url=url,
                job_title=job_title,
                classification=classification,
                skills=filtered_skills,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Failed to process job {url}: {e}")
            return JobProcessingResult(
                url=url,
                job_title=job_title,
                classification=JobClassification(
                    url=url,
                    job_title=job_title,
                    job_role=job_role,
                    experience_level="Unknown",
                    role_sub_cluster=None,
                    cluster_type=None,
                    classification_confidence=0.0,
                    job_sector=job_sector
                ),
                skills=[],
                success=False,
                error_message=str(e)
            )
    
    def _build_combined_prompt(self, job_title: str, job_description: str, job_role: Optional[str] = None) -> str:
        """Build prompt that extracts classification + skills in one call"""
        
        # Build sub-cluster definitions for prompt (filtered by job_role if provided)
        sub_cluster_text = self._format_sub_clusters_for_prompt(job_role)
        
        prompt = f"""Analyze this job posting and extract:
1. Experience Level Classification
2. Role Sub-Cluster (if applicable)
3. Cluster Type (specific vs generalist)
4. All Skills

**Job Title:** {job_title}

**Job Description:**
{job_description}

---

## TASK 1: Experience Level Classification

Classify into ONE of these levels based on years of experience mentioned:
- **Internship**: Students/recent grads, short-term roles
- **Entry Level**: 0-2 years experience
- **Associate**: 2-5 years experience
- **Mid-Senior Level**: 5-8+ years experience
- **Director**: Management of teams/departments
- **Executive**: VP, C-Suite, strategic leadership

## TASK 2: Role Sub-Cluster Classification

{sub_cluster_text}

## TASK 3: Cluster Type Classification

Determine if this is a **specific** or **generalist** role:
- **specific**: Role requires specific stack/technology (e.g., "React developer", "Python backend engineer")
- **generalist**: Role is rotational, pipeline program, or uses vague language like "any programming language", "willingness to learn", "various technologies"

If you classified as "Generalist" sub-cluster, cluster_type MUST be "generalist".
Otherwise, analyze the job description to determine if it's specific or generalist.

## TASK 4: Skills Extraction

Extract ALL skills mentioned (technical + soft skills). For each skill:
- **skill_name**: Specific name (e.g., "Python", not just "programming")
- **confidence**: 0.0-1.0 based on how explicitly mentioned
  - 1.0: Explicitly required (e.g., "5+ years of Python required")
  - 0.8-0.9: Strongly implied (e.g., "Experience with Python development")
  - 0.6-0.7: Mentioned but not emphasized
  - 0.4-0.5: Weakly implied
- **evidence**: Up to 3 exact text snippets mentioning this skill
- **category_hint**: e.g., "Programming Language", "Framework", "Tool", "Soft Skill"

---

## OUTPUT FORMAT (JSON)

Return ONLY valid JSON with this exact structure:

```json
{{
  "experience_level": "Entry Level",
  "role_sub_cluster": "Frontend",
  "cluster_type": "specific",
  "classification_confidence": 0.95,
  "skills": [
    {{
      "skill_name": "React",
      "confidence": 0.95,
      "evidence": ["3+ years of React experience", "Expert in React development"],
      "category_hint": "Framework"
    }},
    {{
      "skill_name": "Leadership",
      "confidence": 0.85,
      "evidence": ["Lead a team of developers"],
      "category_hint": "Soft Skill"
    }}
  ]
}}
```

IMPORTANT:
- Return ONLY the JSON object, no other text
- `role_sub_cluster` must be null or one of the exact sub-cluster names listed above (WITHOUT prefix)
- `cluster_type` must be "specific" or "generalist"
- Include BOTH technical and soft skills
- Confidence should reflect how explicitly the skill is required
- **CRITICAL**: Use ONLY straight quotes (") in the JSON, NEVER use smart/curly quotes (" " ' ') or any special characters that break JSON parsing
"""
        return prompt
    
    def _format_sub_clusters_for_prompt(self, job_role: Optional[str] = None) -> str:
        """Format sub-cluster definitions for the prompt, filtered by job_role if provided"""
        
        if job_role and job_role in SUB_CLUSTER_DEFINITIONS:
            # Only show sub-clusters for this specific job role
            lines = [f"This job is categorized as: **{job_role}**\n"]
            lines.append("Classify into ONE of these sub-clusters if applicable:\n")
            
            clusters = SUB_CLUSTER_DEFINITIONS[job_role]
            for cluster_name, triggers in clusters.items():
                trigger_list = ", ".join(triggers[:5])  # Show first 5 triggers
                lines.append(f"- `{cluster_name}`: Triggers: {trigger_list}")
            
            lines.append(f"\n\nIMPORTANT: Return ONLY one of the sub-cluster names above, or null if none match.")
        else:
            # Show all sub-clusters (fallback if job_role not provided or not recognized)
            lines = ["Only classify into a sub-cluster if the job matches one of these heavyweight roles:\n"]
            
            for role, clusters in SUB_CLUSTER_DEFINITIONS.items():
                lines.append(f"\n**{role}:**")
                for cluster_name, triggers in clusters.items():
                    trigger_list = ", ".join(triggers[:5])  # Show first 5 triggers
                    lines.append(f"- `{cluster_name}`: Triggers: {trigger_list}")
            
            lines.append("\n\nIMPORTANT: Return ONLY the sub-cluster name (e.g., 'Computer Vision'), NOT the prefix (e.g., NOT 'AI - Computer Vision')")
        
        return "\n".join(lines)
    
    def _parse_response(
        self,
        response: dict,
        url: str,
        job_title: str,
        job_role: Optional[str] = None,
        job_sector: Optional[str] = None
    ) -> tuple[JobClassification, list[ExtractedSkill]]:
        """Parse LLM response into classification and skills"""
        
        # Parse classification
        classification = JobClassification(
            url=url,
            job_title=job_title,
            job_role=job_role,
            experience_level=response.get("experience_level", "Unknown"),
            role_sub_cluster=response.get("role_sub_cluster"),
            cluster_type=response.get("cluster_type"),
            classification_confidence=float(response.get("classification_confidence", 0.8)),
            job_sector=job_sector
        )
        
        # Parse skills
        skills = []
        for skill_data in response.get("skills", []):
            try:
                skill = ExtractedSkill(
                    skill_name=skill_data["skill_name"].strip(),
                    confidence=float(skill_data["confidence"]),
                    evidence=skill_data.get("evidence", []),
                    category_hint=skill_data.get("category_hint")
                )
                skills.append(skill)
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to parse skill: {skill_data}, error: {e}")
                continue
        
        return classification, skills
