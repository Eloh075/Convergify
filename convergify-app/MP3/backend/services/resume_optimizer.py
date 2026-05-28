"""
Resume Optimization Service
Generates improved resume based on analysis feedback without hallucination
"""
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ResumeOptimizer:
    """Service for optimizing resumes based on analysis results"""
    
    def __init__(self):
        self.version = "1.0"
    
    async def optimize_resume(
        self, 
        original_resume_text: str,
        analysis_results: Dict[str, Any],
        resume_skills: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Optimize resume based on analysis results
        
        Args:
            original_resume_text: Original resume content
            analysis_results: Analysis results with gaps and recommendations
            resume_skills: Extracted skills from resume
            
        Returns:
            Dictionary with optimized resume and changes
        """
        try:
            logger.info("Starting resume optimization")
            
            # Extract key information from analysis
            skill_gaps = analysis_results.get('skill_gaps', [])
            skill_overlaps = analysis_results.get('skill_overlaps', [])
            recommendations = analysis_results.get('recommendations', [])
            match_score = analysis_results.get('match_score', 0)
            
            # Generate optimization suggestions
            suggestions = self._generate_suggestions(
                skill_gaps=skill_gaps,
                skill_overlaps=skill_overlaps,
                recommendations=recommendations,
                resume_skills=resume_skills
            )
            
            # Create optimized resume sections
            optimized_sections = self._optimize_sections(
                original_resume_text=original_resume_text,
                suggestions=suggestions,
                skill_overlaps=skill_overlaps
            )
            
            # Track changes
            changes = self._track_changes(
                original_text=original_resume_text,
                optimized_sections=optimized_sections,
                suggestions=suggestions
            )
            
            # Build final result
            result = {
                'success': True,
                'optimized_resume': {
                    'text': self._build_resume_text(optimized_sections),
                    'sections': optimized_sections,
                    'format': 'text'
                },
                'changes': changes,
                'suggestions': suggestions,
                'optimization_metadata': {
                    'original_match_score': match_score,
                    'optimization_version': self.version,
                    'timestamp': datetime.now().isoformat(),
                    'total_changes': len(changes),
                    'skill_gaps_addressed': len([s for s in suggestions if s['type'] == 'skill_gap'])
                }
            }
            
            logger.info(f"Resume optimization complete with {len(changes)} changes")
            return result
            
        except Exception as e:
            logger.error(f"Resume optimization failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'optimized_resume': None,
                'changes': [],
                'suggestions': []
            }
    
    def _generate_suggestions(
        self,
        skill_gaps: List[Dict],
        skill_overlaps: List[Dict],
        recommendations: List[Dict],
        resume_skills: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """Generate specific optimization suggestions"""
        suggestions = []
        
        # Suggestions for highlighting existing skills
        for overlap in skill_overlaps[:10]:  # Top 10 matching skills
            skill = overlap.get('skill', '')
            if skill:
                suggestions.append({
                    'type': 'highlight_skill',
                    'skill': skill,
                    'action': 'emphasize',
                    'reason': f'This skill matches job requirements - ensure it\'s prominently featured',
                    'priority': 'high',
                    'section': 'skills'
                })
        
        # Suggestions for addressing skill gaps (only if related to existing experience)
        for gap in skill_gaps[:5]:  # Top 5 gaps
            skill = gap.get('skill', '')
            if skill and self._is_related_to_existing_skills(skill, resume_skills):
                suggestions.append({
                    'type': 'skill_gap',
                    'skill': skill,
                    'action': 'add_context',
                    'reason': f'Add context about {skill} if you have relevant experience',
                    'priority': 'medium',
                    'section': 'experience'
                })
        
        # Suggestions from recommendations
        for rec in recommendations[:5]:
            if rec.get('category') == 'immediate':
                suggestions.append({
                    'type': 'recommendation',
                    'action': 'improve_description',
                    'reason': rec.get('description', ''),
                    'priority': rec.get('priority', 'medium'),
                    'section': 'general'
                })
        
        return suggestions
    
    def _is_related_to_existing_skills(self, skill: str, resume_skills: Dict[str, List[str]]) -> bool:
        """Check if a skill is related to existing resume skills"""
        skill_lower = skill.lower()
        
        # Check if skill is similar to existing skills
        for skill_category, skills in resume_skills.items():
            for existing_skill in skills:
                if skill_lower in existing_skill.lower() or existing_skill.lower() in skill_lower:
                    return True
        
        return False
    
    def _optimize_sections(
        self,
        original_resume_text: str,
        suggestions: List[Dict],
        skill_overlaps: List[Dict]
    ) -> Dict[str, str]:
        """Optimize resume sections based on suggestions"""
        
        # For now, return enhanced versions of common sections
        # In a full implementation, this would use LLM with strict instructions
        
        sections = {
            'summary': self._enhance_summary(original_resume_text, skill_overlaps),
            'skills': self._enhance_skills(original_resume_text, skill_overlaps, suggestions),
            'experience': self._enhance_experience(original_resume_text, suggestions),
            'education': self._extract_section(original_resume_text, 'education'),
            'projects': self._extract_section(original_resume_text, 'projects')
        }
        
        return sections
    
    def _enhance_summary(self, resume_text: str, skill_overlaps: List[Dict]) -> str:
        """Enhance professional summary with matching skills"""
        # Extract existing summary
        summary = self._extract_section(resume_text, 'summary')
        
        if not summary:
            # Create basic summary highlighting top skills
            top_skills = [s.get('skill', '') for s in skill_overlaps[:5]]
            summary = f"Professional with expertise in {', '.join(top_skills[:3])} and related technologies."
        
        return summary
    
    def _enhance_skills(
        self,
        resume_text: str,
        skill_overlaps: List[Dict],
        suggestions: List[Dict]
    ) -> str:
        """Enhance skills section"""
        skills_section = self._extract_section(resume_text, 'skills')
        
        # Get matching skills to highlight
        matching_skills = [s.get('skill', '') for s in skill_overlaps]
        
        # Organize by category
        skill_categories = {
            'Technical Skills': [],
            'Tools & Technologies': [],
            'Soft Skills': []
        }
        
        for skill in matching_skills[:15]:
            skill_categories['Technical Skills'].append(skill)
        
        # Build enhanced skills section
        enhanced = "SKILLS\n\n"
        for category, skills in skill_categories.items():
            if skills:
                enhanced += f"{category}: {', '.join(skills)}\n"
        
        return enhanced
    
    def _enhance_experience(self, resume_text: str, suggestions: List[Dict]) -> str:
        """Enhance experience section"""
        experience = self._extract_section(resume_text, 'experience')
        
        # Add suggestions as comments (in a real implementation, would integrate into descriptions)
        return experience
    
    def _extract_section(self, resume_text: str, section_name: str) -> str:
        """Extract a section from resume text"""
        section_keywords = {
            'summary': ['summary', 'objective', 'profile'],
            'skills': ['skills', 'technical skills', 'competencies'],
            'experience': ['experience', 'work history', 'employment'],
            'education': ['education', 'academic', 'qualifications'],
            'projects': ['projects', 'portfolio']
        }
        
        keywords = section_keywords.get(section_name.lower(), [section_name])
        lines = resume_text.split('\n')
        
        section_content = []
        in_section = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if we're entering this section
            if any(keyword in line_lower for keyword in keywords):
                in_section = True
                section_content.append(line)
                continue
            
            # Check if we're entering a different section
            if in_section and any(
                keyword in line_lower 
                for other_keywords in section_keywords.values() 
                for keyword in other_keywords
                if keyword not in keywords
            ):
                break
            
            if in_section:
                section_content.append(line)
        
        return '\n'.join(section_content) if section_content else ''
    
    def _build_resume_text(self, sections: Dict[str, str]) -> str:
        """Build complete resume text from sections"""
        resume_parts = []
        
        section_order = ['summary', 'skills', 'experience', 'projects', 'education']
        
        for section_name in section_order:
            section_content = sections.get(section_name, '')
            if section_content:
                resume_parts.append(section_content)
                resume_parts.append('')  # Add spacing
        
        return '\n'.join(resume_parts)
    
    def _track_changes(
        self,
        original_text: str,
        optimized_sections: Dict[str, str],
        suggestions: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Track changes made to the resume"""
        changes = []
        
        # Track section-level changes
        for section_name, optimized_content in optimized_sections.items():
            original_section = self._extract_section(original_text, section_name)
            
            if optimized_content != original_section:
                changes.append({
                    'section': section_name,
                    'type': 'section_enhanced',
                    'description': f'Enhanced {section_name} section to highlight relevant skills',
                    'original_length': len(original_section),
                    'new_length': len(optimized_content),
                    'reason': f'Optimized based on analysis feedback'
                })
        
        # Track suggestion-based changes
        for suggestion in suggestions[:10]:
            if suggestion['type'] == 'highlight_skill':
                changes.append({
                    'section': suggestion['section'],
                    'type': 'skill_highlighted',
                    'description': f'Highlighted {suggestion["skill"]}',
                    'reason': suggestion['reason'],
                    'priority': suggestion['priority']
                })
        
        return changes
