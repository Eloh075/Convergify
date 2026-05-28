"""
Strategic Analyzer

Performs semantic matching with evidence extraction and generates comprehensive recommendations.
"""
import logging
import json
from typing import List, Dict, Optional
from datetime import datetime

from ..gemini_client import GeminiClient
from ..config import EngineConfig
from .evidence_extractor import EvidenceExtractor
from .models import (
    SkillMatch, Evidence, AnalysisResult, AnalysisSummary,
    Recommendation, MarketInsights, TopSkill, SkillGap,
    MarketIntelligenceResult
)

logger = logging.getLogger(__name__)


class StrategicAnalyzer:
    """Strategic career analysis with semantic matching"""
    
    def __init__(self, gemini_api_key: Optional[str] = None, db_session=None):
        """
        Initialize strategic analyzer
        
        Args:
            gemini_api_key: Gemini API key (defaults to config)
            db_session: Optional database session for caching canonical mappings
        """
        self.llm_client = GeminiClient(gemini_api_key)
        self.evidence_extractor = EvidenceExtractor()
        self.db_session = db_session
    
    def analyze_single_job(
        self,
        resume_text: str,
        classification_result
    ) -> AnalysisResult:
        """
        Analyze resume against single job
        
        Args:
            resume_text: Full resume text
            classification_result: ClassificationResult from classifier
            
        Returns:
            AnalysisResult with matches and recommendations
        """
        logger.info("Starting single job analysis")
        
        # Get skills from first job
        if not classification_result.classified_jobs:
            raise ValueError("No classified jobs found")
        
        job = classification_result.classified_jobs[0]
        required_skills = job.classified_skills
        
        # Perform semantic matching (no canonical grouping for single job)
        skill_matches, _ = self._semantic_match_skills(
            resume_text, 
            required_skills,
            classification_result.market_frequencies
        )
        
        # Calculate match scores
        overall_score = self._calculate_match_score(skill_matches)
        category_scores = self._calculate_category_scores(skill_matches)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            skill_matches,
            classification_result.market_frequencies
        )
        
        # Create summary
        summary = self._create_summary(skill_matches)
        
        logger.info(f"Analysis complete: {overall_score:.1f}% match")
        
        return AnalysisResult(
            overall_match_score=overall_score,
            category_scores=category_scores,
            skill_matches=skill_matches,
            recommendations=recommendations,
            summary=summary
        )
    
    def analyze_market_intelligence(
        self,
        resume_text: str,
        classification_result
    ) -> MarketIntelligenceResult:
        """
        Analyze resume against multiple jobs for market insights
        
        Args:
            resume_text: Full resume text
            classification_result: ClassificationResult from classifier
            
        Returns:
            MarketIntelligenceResult with market insights and canonical groups
        """
        logger.info(f"Starting market intelligence analysis for {len(classification_result.classified_jobs)} jobs")
        
        # Collect all unique skills across all jobs
        all_skills = []
        skill_importance_map = {}
        all_job_skills = []  # All skills with duplicates for frequency counting
        
        for job in classification_result.classified_jobs:
            for skill in job.classified_skills:
                # Add to all_job_skills for frequency counting
                all_job_skills.append(skill.canonical_name)
                
                # Use canonical name to avoid duplicates in unique list
                if skill.canonical_name not in skill_importance_map:
                    all_skills.append(skill)
                    skill_importance_map[skill.canonical_name] = skill.importance
        
        logger.info(f"Analyzing {len(all_skills)} unique skills across all jobs")
        logger.info(f"Total skill mentions: {len(all_job_skills)}")
        
        # Perform semantic matching WITH canonical grouping
        skill_matches, canonical_groups = self._semantic_match_skills(
            resume_text,
            all_skills,
            classification_result.market_frequencies,
            all_job_skills=all_job_skills,
            total_jobs=len(classification_result.classified_jobs)
        )
        
        logger.info(f"Created {len(canonical_groups)} canonical groups")
        
        # Calculate match scores
        overall_score = self._calculate_match_score(skill_matches)
        category_scores = self._calculate_category_scores(skill_matches)
        
        # Generate market insights using canonical groups
        market_insights = self._generate_market_insights(
            classification_result,
            skill_matches,
            canonical_groups
        )
        
        # Identify top skills using canonical groups
        top_skills = self._identify_top_skills(classification_result, canonical_groups)
        
        # Prioritize skill gaps
        skill_gaps = self._prioritize_skill_gaps(
            skill_matches,
            classification_result.market_frequencies
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            skill_matches,
            classification_result.market_frequencies,
            market_insights
        )
        
        # Create summary
        summary = self._create_summary(skill_matches)
        
        logger.info(f"Market intelligence analysis complete: {overall_score:.1f}% match")
        
        return MarketIntelligenceResult(
            overall_match_score=overall_score,
            category_scores=category_scores,
            skill_matches=skill_matches,
            recommendations=recommendations,
            summary=summary,
            market_insights=market_insights,
            top_skills=top_skills,
            skill_gaps_prioritized=skill_gaps,
            canonical_groups=canonical_groups
        )
    
    def _semantic_match_skills(
        self,
        resume_text: str,
        required_skills: List,
        market_frequencies: Dict = None,
        all_job_skills: List[str] = None,
        total_jobs: int = 0
    ) -> tuple:
        """
        Perform semantic matching (not keyword) with canonical grouping
        
        Args:
            resume_text: Full resume text
            required_skills: List of ClassifiedSkill objects
            market_frequencies: Dict of skill frequencies from classification
            all_job_skills: All skills from all jobs (for canonical grouping)
            total_jobs: Total number of jobs analyzed
            
        Returns:
            Tuple of (List[SkillMatch], Dict[str, CanonicalGroup])
        """
        logger.info(f"Performing semantic matching for {len(required_skills)} skills")
        
        # Try to use Gemini 2.5 Flash for large outputs
        # If quota exceeded or response too large, fall back to batching with default model
        try:
            return self._semantic_match_skills_chunk(
                resume_text, required_skills, market_frequencies, 
                use_large_model=True, all_job_skills=all_job_skills, total_jobs=total_jobs
            )
        except Exception as e:
            error_str = str(e)
            # Check if we should fall back to batching
            should_batch = (
                ("429" in error_str or "quota" in error_str.lower() or "too large" in error_str.lower()) 
                and len(required_skills) > 20
            )
            
            if should_batch:
                logger.warning(f"Large model failed ({error_str[:100]}), falling back to batching with default model")
                # Batch process with smaller model
                CHUNK_SIZE = 20
                all_matches = []
                all_canonical_groups = {}
                for i in range(0, len(required_skills), CHUNK_SIZE):
                    chunk = required_skills[i:i + CHUNK_SIZE]
                    logger.info(f"Processing chunk {i//CHUNK_SIZE + 1}/{(len(required_skills) + CHUNK_SIZE - 1)//CHUNK_SIZE} ({len(chunk)} skills)")
                    chunk_matches, chunk_groups = self._semantic_match_skills_chunk(
                        resume_text, chunk, market_frequencies, 
                        use_large_model=False, all_job_skills=all_job_skills, total_jobs=total_jobs
                    )
                    all_matches.extend(chunk_matches)
                    all_canonical_groups.update(chunk_groups)
                return all_matches, all_canonical_groups
            else:
                raise
    
    def _call_large_model_with_rotation(self, prompt: str, retry_count: int = 0) -> Dict:
        """
        Call Gemini 2.5 Flash with proper API key rotation support
        
        Args:
            prompt: The prompt to send
            retry_count: Current retry count
            
        Returns:
            JSON response dict
        """
        import google.generativeai as genai
        import json
        
        MAX_RETRIES = len(self.llm_client.available_keys) if self.llm_client.use_rotation else 3
        if retry_count >= MAX_RETRIES:
            raise Exception(f"Max retries ({MAX_RETRIES}) exceeded for large model")
        
        try:
            # Configure with current API key
            genai.configure(api_key=self.llm_client.api_key)
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            # Generate with large output limit
            generation_config = genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=32768,  # 32K output
                response_mime_type="application/json"
            )
            
            response = model.generate_content(prompt, generation_config=generation_config)
            response_text = response.text.strip()
            
            # Parse JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                if len(response_text) > 20000:
                    raise ValueError(
                        f"Response too large ({len(response_text)} chars) and truncated. "
                        f"Consider reducing prompt size or processing in smaller chunks."
                    )
                else:
                    raise ValueError(f"Invalid JSON response from model: {str(e)}")
                    
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini 2.5 Flash error (attempt {retry_count + 1}): {error_msg}")
            
            # Check if it's a quota error
            is_quota_error = (
                "429" in error_msg or 
                "quota" in error_msg.lower() or
                "rate limit" in error_msg.lower()
            )
            
            # Try rotating key
            if is_quota_error and self.llm_client.use_rotation:
                logger.info("Quota exceeded, attempting to rotate API key...")
                if self.llm_client._rotate_key():
                    logger.info("Successfully rotated to new API key, retrying...")
                    return self._call_large_model_with_rotation(prompt, retry_count + 1)
            
            raise
    
    def _semantic_match_skills_chunk(
        self,
        resume_text: str,
        required_skills: List,
        market_frequencies: Dict = None,
        use_large_model: bool = True,
        all_job_skills: List[str] = None,
        total_jobs: int = 0
    ) -> tuple:
        """
        Process skills for semantic matching with canonical grouping
        
        Returns:
            Tuple of (List[SkillMatch], Dict[str, CanonicalGroup])
        """
        from .models import CanonicalGroup
        
        skill_matches = []
        canonical_groups = {}
        
        # Build prompt for LLM (includes canonical grouping if all_job_skills provided)
        prompt = self._build_semantic_matching_prompt(resume_text, required_skills, all_job_skills)
        
        try:
            if use_large_model:
                # Use Gemini 2.5 Flash directly with rotation support
                logger.info(f"Using gemini-2.5-flash for semantic matching ({len(required_skills)} skills)")
                response = self._call_large_model_with_rotation(prompt)
            else:
                # Use default model with smaller output limit
                logger.info(f"Using default model for semantic matching ({len(required_skills)} skills)")
                response = self.llm_client.generate_json(
                    prompt,
                    max_tokens=8192  # Smaller limit for default model
                )
            
            # Parse semantic matches
            matches_data = response.get('semantic_matches', []) if isinstance(response, dict) else response
            
            for match_data in matches_data:
                try:
                    skill_name = match_data['skill_name']
                    
                    # Find corresponding required skill
                    required_skill = next(
                        (s for s in required_skills if s.canonical_name == skill_name),
                        None
                    )
                    
                    if not required_skill:
                        continue
                    
                    # Extract evidence from resume
                    evidence = self.evidence_extractor.extract_evidence(resume_text, skill_name)
                    
                    # Get actual market frequency from market_frequencies dict
                    market_freq = 0.0
                    if market_frequencies and skill_name in market_frequencies:
                        freq_data = market_frequencies[skill_name]
                        market_freq = freq_data.normalized_frequency if hasattr(freq_data, 'normalized_frequency') else 0.0
                    
                    # Reconcile LLM confidence with evidence confidence
                    llm_confidence = float(match_data.get('confidence_score', 0.0))
                    final_confidence = self._reconcile_confidence(
                        llm_confidence, 
                        evidence.confidence if evidence.found else 0.0,
                        evidence.found
                    )
                    
                    # Log significant mismatches for debugging
                    if llm_confidence > 0.7 and evidence.confidence < 0.3:
                        logger.warning(
                            f"Confidence mismatch for {skill_name}: "
                            f"LLM={llm_confidence:.2f}, Evidence={evidence.confidence:.2f}"
                        )
                    
                    # Create skill match
                    skill_match = SkillMatch(
                        skill_name=skill_name,
                        canonical_name=skill_name,
                        match_status=match_data.get('match_status', 'Missing'),
                        match_type=match_data.get('match_type', 'None'),
                        confidence_score=final_confidence,
                        evidence=evidence,
                        substitution_reasoning=match_data.get('reasoning'),
                        importance=required_skill.importance,
                        market_frequency=market_freq
                    )
                    
                    skill_matches.append(skill_match)
                    
                except (KeyError, ValueError) as e:
                    logger.warning(f"Failed to parse skill match: {match_data}, error: {e}")
                    continue
            
            # Parse canonical groups if provided
            if isinstance(response, dict) and 'canonical_groups' in response and all_job_skills and total_jobs > 0:
                canonical_data = response['canonical_groups']
                logger.info(f"Parsing {len(canonical_data)} canonical groups")
                canonical_groups = self._parse_canonical_groups(canonical_data, all_job_skills, total_jobs, self.db_session)
            
        except Exception as e:
            logger.error(f"Semantic matching failed: {e}")
            # DO NOT use fallback - fail loudly so we know when LLM isn't working
            raise Exception(f"LLM semantic matching failed: {e}. Check API keys and model availability.")
        
        logger.info(f"Matched {len(skill_matches)} skills, created {len(canonical_groups)} canonical groups")
        return skill_matches, canonical_groups
    
    def _build_semantic_matching_prompt(
        self,
        resume_text: str,
        required_skills: List,
        all_job_skills: List[str] = None
    ) -> str:
        """Build LLM prompt for semantic matching with optional canonical grouping"""
        
        skills_json = json.dumps([
            {
                'skill_name': skill.canonical_name,
                'importance': skill.importance,
                'tier1': skill.tier1,
                'tier2': skill.tier2
            }
            for skill in required_skills
        ], indent=2)
        
        # Base prompt for semantic matching
        base_prompt = f"""Analyze this resume against required skills using SEMANTIC MATCHING (not keyword matching).

RESUME:
{resume_text[:3000]}

REQUIRED SKILLS:
{skills_json}

TASK 1: Semantic Matching
For EACH required skill, determine:

1. **Match Status** (choose one):
   - "Strong Match": Skill is clearly demonstrated with strong evidence
   - "Partial Match": Related skill or weak evidence of the skill
   - "Missing": No evidence of this skill in the resume

2. **Match Type** (choose one):
   - "Exact": Resume mentions the exact skill name
   - "Semantic": Resume demonstrates the skill through related work (e.g., "built ML models" for "Machine Learning")
   - "Substitution": Resume has an equivalent/substitute skill (e.g., "PostgreSQL" for "SQL databases")
   - "None": No evidence found

3. **Confidence Score**: 0.0 to 1.0
   - 0.9-1.0: Explicit mention with years of experience
   - 0.7-0.9: Clear evidence through project descriptions
   - 0.5-0.7: Implied through related skills or brief mentions
   - 0.3-0.5: Weak evidence or tangential relation
   - 0.0-0.3: No evidence or very weak connection

4. **Reasoning**: 1-2 sentences explaining your assessment with specific evidence from the resume

EXAMPLES:

✅ Strong Match Examples:
- Skill: "Python" → Resume: "5 years of Python development" → Exact, 0.95, "Explicitly states 5 years of Python experience"
- Skill: "Machine Learning" → Resume: "Built predictive models using TensorFlow and scikit-learn" → Semantic, 0.85, "Demonstrates ML through model building with ML frameworks"

⚠️ Partial Match Examples:
- Skill: "React" → Resume: "Frontend development with JavaScript and Vue.js" → Substitution, 0.50, "Has frontend framework experience but with Vue, not React"

❌ Missing Examples:
- Skill: "Blockchain" → Resume: No blockchain-related content → None, 0.0, "No evidence of blockchain knowledge or experience"
"""
        
        # Add canonical grouping task if all_job_skills provided
        if all_job_skills:
            # Get unique skills
            unique_skills = list(set(all_job_skills))
            skills_list = json.dumps(unique_skills[:100], indent=2)  # Limit to first 100 for prompt size
            
            canonical_prompt = f"""

TASK 2: Canonical Grouping
Group semantically related job skills under canonical parent names.

ALL JOB SKILLS:
{skills_list}

Rules for canonical grouping:
1. Group related skills under the most common/recognizable name
2. Examples:
   - "AI", "Generative AI", "AI Agents", "Machine Learning", "Deep Learning" → "Artificial Intelligence (AI)"
   - "React.js", "ReactJS", "React Native" → "React"
   - "Node.js", "NodeJS" → "Node.js"
   - "Python", "Python 3", "Python Programming" → "Python"
3. If a skill is already canonical (no clear parent), map it to itself
4. Preserve all original skill names as children

RETURN FORMAT (JSON object with both tasks):
{{
  "semantic_matches": [
    {{
      "skill_name": "Python",
      "match_status": "Strong Match",
      "match_type": "Exact",
      "confidence_score": 0.95,
      "reasoning": "Resume explicitly mentions 5 years of Python development experience"
    }}
  ],
  "canonical_groups": {{
    "Artificial Intelligence (AI)": ["AI", "Generative AI", "AI Agents", "Machine Learning", "Deep Learning"],
    "React": ["React.js", "ReactJS", "React Native"],
    "Python": ["Python", "Python 3", "Python Programming"]
  }}
}}
"""
            return (base_prompt + canonical_prompt).strip()
        else:
            # Return just semantic matches
            return_format = """

RETURN FORMAT (JSON array only, no other text):
[
  {
    "skill_name": "Python",
    "match_status": "Strong Match",
    "match_type": "Exact",
    "confidence_score": 0.95,
    "reasoning": "Resume explicitly mentions 5 years of Python development experience"
  }
]

IMPORTANT:
- Be generous with Semantic matches (look for related work, not just keywords)
- Use Substitution for equivalent skills
- Only mark as Missing if there's truly no related evidence
- Return ONLY the JSON array
"""
            return (base_prompt + return_format).strip()
    
    def _parse_canonical_groups(
        self,
        canonical_data: Dict[str, List[str]],
        all_job_skills: List[str],
        total_jobs: int,
        db_session = None
    ) -> Dict[str, 'CanonicalGroup']:
        """
        Parse canonical groups from LLM response and calculate aggregated frequencies
        
        Args:
            canonical_data: Dict mapping canonical_name -> [child_skills]
            all_job_skills: All skills from all jobs (with duplicates from each job)
            total_jobs: Total number of jobs analyzed
            db_session: Optional database session for caching canonical mappings
            
        Returns:
            Dict mapping canonical_name -> CanonicalGroup with aggregated stats
        """
        from .models import CanonicalGroup
        from collections import Counter
        
        canonical_groups = {}
        
        # Count all skill occurrences
        skill_counter = Counter(all_job_skills)
        
        # Cache canonical mappings if db_session provided
        if db_session:
            self._cache_canonical_mappings(canonical_data, db_session)
        
        for canonical_name, child_skills in canonical_data.items():
            # Count how many times each child appears
            child_frequencies = {}
            total_mentions = 0
            
            for child_skill in child_skills:
                count = skill_counter.get(child_skill, 0)
                if count > 0:
                    child_frequencies[child_skill] = count
                    total_mentions += count
            
            # Calculate aggregated frequency (unique jobs mentioning any child)
            # Assuming each job contributes at most once per skill
            # This is a simplification - ideally we'd track job IDs
            unique_job_mentions = min(total_mentions, total_jobs)
            aggregated_frequency = unique_job_mentions / total_jobs if total_jobs > 0 else 0.0
            
            if child_frequencies:  # Only add if we found mentions
                canonical_groups[canonical_name] = CanonicalGroup(
                    canonical_name=canonical_name,
                    child_skills=child_skills,
                    child_frequencies=child_frequencies,
                    total_job_mentions=unique_job_mentions,
                    aggregated_frequency=aggregated_frequency
                )
        
        return canonical_groups
    
    def _cache_canonical_mappings(
        self,
        canonical_data: Dict[str, List[str]],
        db_session
    ):
        """
        Cache canonical skill mappings to database
        
        Args:
            canonical_data: Dict mapping canonical_name -> [child_skills]
            db_session: Database session
        """
        try:
            from models.skill_canonical import SkillCanonical
            from sqlalchemy.exc import IntegrityError
            
            cached_count = 0
            for canonical_name, child_skills in canonical_data.items():
                for child_skill in child_skills:
                    # Skip if child is same as canonical (self-mapping)
                    if child_skill == canonical_name:
                        continue
                    
                    # Check if mapping already exists
                    existing = db_session.query(SkillCanonical).filter(
                        SkillCanonical.skill_name == child_skill
                    ).first()
                    
                    if not existing:
                        # Create new mapping
                        mapping = SkillCanonical(
                            skill_name=child_skill,
                            canonical_name=canonical_name,
                            confidence=1.0
                        )
                        db_session.add(mapping)
                        cached_count += 1
                    elif existing.canonical_name != canonical_name:
                        # Update if canonical changed
                        logger.info(f"Updating canonical mapping: {child_skill} from {existing.canonical_name} to {canonical_name}")
                        existing.canonical_name = canonical_name
                        existing.updated_at = datetime.utcnow()
                        cached_count += 1
            
            if cached_count > 0:
                db_session.commit()
                logger.info(f"Cached {cached_count} new/updated canonical mappings")
        
        except Exception as e:
            logger.warning(f"Failed to cache canonical mappings: {e}")
            db_session.rollback()
    
    def _get_cached_canonical_mappings(
        self,
        skill_names: List[str],
        db_session
    ) -> Dict[str, str]:
        """
        Get cached canonical mappings from database
        
        Args:
            skill_names: List of skill names to look up
            db_session: Database session
            
        Returns:
            Dict mapping skill_name -> canonical_name for cached skills
        """
        try:
            from models.skill_canonical import SkillCanonical
            
            # Query all cached mappings for these skills
            cached = db_session.query(SkillCanonical).filter(
                SkillCanonical.skill_name.in_(skill_names)
            ).all()
            
            mappings = {c.skill_name: c.canonical_name for c in cached}
            
            if mappings:
                logger.info(f"Found {len(mappings)} cached canonical mappings (cache hit rate: {len(mappings)/len(skill_names)*100:.1f}%)")
            
            return mappings
        
        except Exception as e:
            logger.warning(f"Failed to retrieve cached canonical mappings: {e}")
            return {}
    
    # REMOVED: _fallback_evidence_matching method
    # Per user request: "remove any fallback related data cuz it either should work or show 0"
    # System now fails loudly when LLM semantic matching fails
    
    def _reconcile_confidence(
        self,
        llm_confidence: float,
        evidence_confidence: float,
        evidence_found: bool
    ) -> float:
        """
        Reconcile LLM confidence with evidence confidence
        
        Args:
            llm_confidence: Confidence from LLM semantic matching
            evidence_confidence: Confidence from evidence extraction
            evidence_found: Whether evidence was found
            
        Returns:
            Reconciled confidence score
        """
        # If evidence strongly supports LLM, keep LLM confidence
        if evidence_found and evidence_confidence > 0.5:
            # Evidence supports LLM, use average weighted toward evidence
            return (llm_confidence * 0.4 + evidence_confidence * 0.6)
        
        # If evidence weakly supports LLM, reduce confidence
        elif evidence_found and evidence_confidence <= 0.5:
            # Weak evidence, average the two
            return (llm_confidence + evidence_confidence) / 2.0
        
        # If no evidence found, significantly reduce LLM confidence
        else:
            # No evidence found, but LLM thinks it's there (semantic match)
            # Reduce confidence but don't eliminate (LLM might see semantic evidence)
            return llm_confidence * 0.4
    
    def _calculate_match_score(self, skill_matches: List[SkillMatch]) -> float:
        """Calculate overall match score"""
        if not skill_matches:
            return 0.0
        
        total_weight = 0.0
        weighted_score = 0.0
        
        for match in skill_matches:
            # Weight by importance
            if match.importance == "Must-have":
                weight = 3.0
            elif match.importance == "Nice-to-have":
                weight = 2.0
            else:  # Preferred
                weight = 1.0
            
            # Score by match status
            if match.match_status == "Strong Match":
                score = 1.0
            elif match.match_status == "Partial Match":
                score = 0.5
            else:  # Missing
                score = 0.0
            
            weighted_score += score * weight
            total_weight += weight
        
        return (weighted_score / total_weight * 100) if total_weight > 0 else 0.0
    
    def _calculate_category_scores(
        self,
        skill_matches: List[SkillMatch]
    ) -> Dict[str, float]:
        """Calculate scores by importance category"""
        categories = {
            "Must-have": [],
            "Nice-to-have": [],
            "Preferred": []
        }
        
        for match in skill_matches:
            if match.match_status == "Strong Match":
                score = 100.0
            elif match.match_status == "Partial Match":
                score = 50.0
            else:
                score = 0.0
            
            categories[match.importance].append(score)
        
        category_scores = {}
        for category, scores in categories.items():
            if scores:
                category_scores[category] = sum(scores) / len(scores)
            else:
                category_scores[category] = 0.0
        
        return category_scores
    
    def _generate_recommendations(
        self,
        skill_matches: List[SkillMatch],
        market_frequencies: Dict,
        market_insights: Optional[MarketInsights] = None
    ) -> List[Recommendation]:
        """Generate detailed recommendations"""
        recommendations = []
        
        # Find missing must-have skills
        missing_must_have = [
            m for m in skill_matches
            if m.match_status == "Missing" and m.importance == "Must-have"
        ]
        
        if missing_must_have:
            rec = Recommendation(
                priority="High",
                category="Skill Development",
                title="Develop Critical Missing Skills",
                description=f"You are missing {len(missing_must_have)} must-have skills that are essential for this role. "
                           f"Focus on developing these skills through courses, projects, or certifications to significantly improve your candidacy.",
                action_items=[
                    f"Learn {skill.skill_name}" for skill in missing_must_have[:3]
                ],
                evidence_references=[
                    f"{skill.skill_name} is required but not found in resume"
                    for skill in missing_must_have[:3]
                ]
            )
            recommendations.append(rec)
        
        # Find partial matches that could be strengthened
        partial_matches = [
            m for m in skill_matches
            if m.match_status == "Partial Match"
        ]
        
        if partial_matches:
            rec = Recommendation(
                priority="Medium",
                category="Resume Optimization",
                title="Strengthen Partial Skill Matches",
                description=f"You have {len(partial_matches)} skills that partially match requirements. "
                           f"Enhance your resume to better showcase these skills with specific examples and quantifiable achievements.",
                action_items=[
                    f"Add more details about {skill.skill_name} experience"
                    for skill in partial_matches[:3]
                ],
                evidence_references=[
                    f"{skill.skill_name}: {skill.substitution_reasoning or 'Needs more evidence'}"
                    for skill in partial_matches[:3]
                ]
            )
            recommendations.append(rec)
        
        # Application strategy
        strong_matches = [
            m for m in skill_matches
            if m.match_status == "Strong Match"
        ]
        
        if strong_matches:
            rec = Recommendation(
                priority="High",
                category="Application Strategy",
                title="Highlight Your Strong Matches",
                description=f"You have {len(strong_matches)} strong skill matches. "
                           f"Emphasize these skills in your cover letter and during interviews to demonstrate your fit for the role.",
                action_items=[
                    f"Prepare examples demonstrating {skill.skill_name}"
                    for skill in strong_matches[:3]
                ],
                evidence_references=[
                    f"{skill.skill_name}: Strong evidence found"
                    for skill in strong_matches[:3]
                ]
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _create_summary(self, skill_matches: List[SkillMatch]) -> AnalysisSummary:
        """Create analysis summary"""
        strong = sum(1 for m in skill_matches if m.match_status == "Strong Match")
        partial = sum(1 for m in skill_matches if m.match_status == "Partial Match")
        missing = sum(1 for m in skill_matches if m.match_status == "Missing")
        
        # Determine overall readiness
        match_rate = strong / len(skill_matches) if skill_matches else 0
        if match_rate >= 0.7:
            readiness = "Ready"
        elif match_rate >= 0.4:
            readiness = "Needs Development"
        else:
            readiness = "Not Ready"
        
        return AnalysisSummary(
            total_skills_required=len(skill_matches),
            strong_matches=strong,
            partial_matches=partial,
            missing_skills=missing,
            overall_readiness=readiness
        )
    
    def _generate_market_insights(
        self,
        classification_result,
        skill_matches: List[SkillMatch],
        canonical_groups: Dict = None
    ) -> MarketInsights:
        """Generate market intelligence data using canonical groups for accurate demand"""
        
        # Build top skills from canonical groups if available, otherwise use skill matches
        top_skills_data = []
        
        if canonical_groups:
            # Use canonical groups for aggregated demand scores
            logger.info(f"Using {len(canonical_groups)} canonical groups for market insights")
            for canonical_name, group in canonical_groups.items():
                # Get importance from skill matches
                importance = "Preferred"
                for skill_match in skill_matches:
                    if skill_match.skill_name == canonical_name:
                        importance = skill_match.importance
                        break
                
                top_skills_data.append({
                    'skill': canonical_name,
                    'demand_score': group.aggregated_frequency,
                    'job_count': group.total_job_mentions,
                    'child_skills': group.child_frequencies,  # Include breakdown
                    'growth_trend': 'stable',  # Default - requires historical data
                    'importance': importance
                })
        else:
            # Fallback to skill matches (old behavior)
            for skill_match in skill_matches:
                if skill_match.match_status in ["Strong Match", "Partial Match"]:
                    freq_data = classification_result.market_frequencies.get(skill_match.skill_name)
                    
                    top_skills_data.append({
                        'skill': skill_match.skill_name,
                        'demand_score': skill_match.market_frequency,
                        'job_count': freq_data.raw_frequency if freq_data else 1,
                        'growth_trend': 'stable',
                        'importance': skill_match.importance
                    })
        
        # Sort by demand score descending
        top_skills_data.sort(key=lambda x: x['demand_score'], reverse=True)
        
        # Identify must-have and nice-to-have skills from matched skills
        must_have = []
        nice_to_have = []
        
        for skill_match in skill_matches:
            if skill_match.importance == "Must-have":
                must_have.append(skill_match.skill_name)
            elif skill_match.importance == "Nice-to-have":
                nice_to_have.append(skill_match.skill_name)
        
        # Determine competition level
        total_jobs = len(classification_result.classified_jobs)
        if total_jobs >= 10:
            competition = "High"
        elif total_jobs >= 5:
            competition = "Medium"
        else:
            competition = "Low"
        
        return MarketInsights(
            total_jobs_analyzed=total_jobs,
            top_skills_by_demand=top_skills_data,
            must_have_skills=must_have,
            nice_to_have_skills=nice_to_have,
            competition_level=competition,
            skill_trends={}
        )
    
    def _identify_top_skills(self, classification_result, canonical_groups: Dict = None) -> List[TopSkill]:
        """Identify top skills by market demand using canonical groups if available"""
        top_skills = []
        
        if canonical_groups:
            # Use canonical groups for aggregated demand
            sorted_groups = sorted(
                canonical_groups.items(),
                key=lambda x: x[1].aggregated_frequency,
                reverse=True
            )
            
            for canonical_name, group in sorted_groups[:10]:
                top_skill = TopSkill(
                    skill_name=canonical_name,
                    demand_percentage=group.aggregated_frequency * 100,
                    job_count=group.total_job_mentions,
                    growth_trend='stable'
                )
                top_skills.append(top_skill)
        else:
            # Fallback to market frequencies (old behavior)
            sorted_skills = sorted(
                classification_result.market_frequencies.items(),
                key=lambda x: x[1].normalized_frequency,
                reverse=True
            )
            
            for skill_name, freq_data in sorted_skills[:10]:
                top_skill = TopSkill(
                    skill_name=skill_name,
                    demand_percentage=freq_data.normalized_frequency * 100,
                    job_count=freq_data.raw_frequency,
                    growth_trend='stable'
                )
                top_skills.append(top_skill)
        
        return top_skills
    
    def generate_narrative_report(
        self,
        resume_text: str,
        analysis_result,
        classification_result
    ) -> str:
        """
        Generate a comprehensive narrative report using LLM
        
        Args:
            resume_text: Full resume text
            analysis_result: MarketIntelligenceResult from analysis
            classification_result: ClassificationResult with job data
            
        Returns:
            Markdown-formatted narrative report
        """
        logger.info("Generating comprehensive narrative report")
        
        # Build context for LLM
        strong_matches = [m for m in analysis_result.skill_matches if m.match_status == "Strong Match"]
        partial_matches = [m for m in analysis_result.skill_matches if m.match_status == "Partial Match"]
        missing_skills = [m for m in analysis_result.skill_matches if m.match_status == "Missing"]
        
        must_have_missing = [m for m in missing_skills if m.importance == "Must-have"]
        
        prompt = f"""You are a career consultant analyzing a candidate's profile against {len(classification_result.classified_jobs)} job postings.

**Candidate Profile Summary:**
{resume_text[:1500]}

**Analysis Results:**
- Overall Match Score: {analysis_result.overall_match_score:.1f}%
- Strong Skill Matches: {len(strong_matches)}
- Partial Matches: {len(partial_matches)}
- Missing Skills: {len(missing_skills)}
- Critical Missing Skills (Must-have): {len(must_have_missing)}
- Jobs Analyzed: {len(classification_result.classified_jobs)}
- Market Competition: {analysis_result.market_insights.competition_level}

**Top Matched Skills:**
{', '.join([m.skill_name for m in strong_matches[:10]])}

**Critical Missing Skills:**
{', '.join([m.skill_name for m in must_have_missing[:5]])}

Generate a comprehensive career analysis report with these sections:

## Executive Summary
2-3 sentences summarizing the candidate's overall position and readiness for these roles.

## Strengths Analysis
What skills, experience, and qualifications make this candidate competitive? Be specific and reference actual skills from the analysis.

## Gap Analysis
What are the critical missing skills? Why do they matter for these roles? Prioritize by importance.

## Market Position
How does this candidate compare to typical applicants? What's their competitive advantage? What are the challenges?

## Strategic Recommendations
Provide 3-5 prioritized, actionable recommendations with specific next steps. Focus on high-impact actions.

## Career Trajectory
What are realistic next steps? What roles should they target now vs. in 6-12 months?

Write in a professional but encouraging tone. Be honest about gaps but focus on actionable paths forward. Use markdown formatting.
"""
        
        try:
            # Generate report using LLM (text mode, not JSON)
            report = self.llm_client.generate_text(prompt)
            logger.info("Narrative report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate narrative report: {e}")
            # Return a basic template if LLM fails
            return f"""# Career Analysis Report

## Executive Summary
Based on analysis of {len(classification_result.classified_jobs)} job postings, you have a {analysis_result.overall_match_score:.1f}% match score with {len(strong_matches)} strong skill matches and {len(missing_skills)} skill gaps to address.

## Analysis Details
Please review the detailed tabs for specific skill gaps, matches, and recommendations.

*Note: Detailed narrative report generation failed. Please contact support if this persists.*
"""
    
    def _prioritize_skill_gaps(
        self,
        skill_matches: List[SkillMatch],
        market_frequencies: Dict
    ) -> List[SkillGap]:
        """Prioritize skill gaps by importance and market demand"""
        skill_gaps = []
        
        # Find missing skills
        missing_skills = [m for m in skill_matches if m.match_status == "Missing"]
        
        for match in missing_skills:
            # Calculate priority score
            importance_weight = {
                "Must-have": 3.0,
                "Nice-to-have": 2.0,
                "Preferred": 1.0
            }.get(match.importance, 1.0)
            
            freq_data = market_frequencies.get(match.skill_name)
            market_freq = freq_data.normalized_frequency if freq_data else 0.0
            
            priority_score = importance_weight * (1 + market_freq)
            
            skill_gap = SkillGap(
                skill_name=match.skill_name,
                importance=match.importance,
                market_frequency=market_freq,
                priority_score=priority_score,
                reasoning=f"{match.importance} skill appearing in {market_freq*100:.0f}% of jobs"
            )
            skill_gaps.append(skill_gap)
        
        # Sort by priority score
        skill_gaps.sort(key=lambda x: x.priority_score, reverse=True)
        
        return skill_gaps
