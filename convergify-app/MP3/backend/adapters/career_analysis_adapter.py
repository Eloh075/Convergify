"""
Career Analysis Adapter - Integration with strategic_career_analysis engine
"""
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# Add the project root to Python path to import existing engines
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from strategic_career_analysis.engine import StrategicCareerAnalysisEngine
    from strategic_career_analysis.adaptive_engine import AdaptiveStrategicEngine, create_adaptive_engine
    from strategic_career_analysis.single_pass_engine import SinglePassStrategicEngine
    from strategic_career_analysis.config import StrategicCareerConfig
    from strategic_career_analysis.models import (
        ResumeJSON, SkillEvidenceReport, SectorReadinessSummary, 
        CareerGuidanceReport, AnalysisResult, AnalysisType
    )
    CAREER_ANALYSIS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Strategic career analysis not available: {e}")
    CAREER_ANALYSIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class CareerAnalysisAdapter:
    """Adapter for integrating with the strategic career analysis engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the career analysis adapter
        
        Args:
            config: Configuration dictionary for the career analysis engine
        """
        self.available = CAREER_ANALYSIS_AVAILABLE
        self.engine = None
        self.adaptive_engine = None
        self.single_pass_engine = None
        self.config = None
        
        if self.available:
            try:
                # Create strategic career config if provided
                if config:
                    self.config = self._create_strategic_config(config)
                
                # Initialize the main strategic career analysis engine
                self.engine = StrategicCareerAnalysisEngine(self.config)
                
                # Initialize adaptive engine for advanced analysis
                self.adaptive_engine = create_adaptive_engine(self.config)
                
                # Initialize single pass engine for quick analysis
                self.single_pass_engine = SinglePassStrategicEngine(self.config)
                
                logger.info("CareerAnalysisAdapter initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize career analysis engine: {e}")
                self.available = False
                self.engine = None
        else:
            logger.warning("Career analysis engine not available - adapter will use fallback methods")
    
    def _create_strategic_config(self, config_dict: Dict[str, Any]) -> Optional['StrategicCareerConfig']:
        """Create StrategicCareerConfig from dictionary"""
        try:
            # For now, use default config
            # In a full implementation, you'd map config_dict to StrategicCareerConfig
            return StrategicCareerConfig()
        except Exception as e:
            logger.error(f"Failed to create strategic config: {e}")
            return None
    
    async def analyze_career_path(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze career path and opportunities
        
        Args:
            profile: Dictionary containing resume text and optional job/sector data
            
        Returns:
            Dictionary containing career path analysis results
        """
        if not self.available or not self.engine:
            return self._fallback_career_analysis(profile)
        
        try:
            resume_text = profile.get('resume_text', '')
            analysis_type = profile.get('analysis_type', 'career_guidance')
            
            if analysis_type == 'single_job' and 'job_data' in profile:
                # Single job analysis
                job_data = profile['job_data']
                job_id = profile.get('job_id')
                
                result = self.engine.analyze_single_job(resume_text, job_data, job_id)
                return self._process_single_job_result(result)
                
            elif analysis_type == 'sector_analysis' and 'sector' in profile:
                # Sector analysis
                sector = profile['sector']
                include_transferability = profile.get('include_transferability', True)
                
                result = self.engine.analyze_sector(resume_text, sector, include_transferability)
                return self._process_sector_analysis_result(result)
                
            else:
                # General career guidance
                analysis_results = profile.get('previous_analyses', [])
                focus_areas = profile.get('focus_areas', [])
                
                result = self.engine.generate_career_guidance(resume_text, analysis_results, focus_areas)
                return self._process_career_guidance_result(result)
                
        except Exception as e:
            logger.error(f"Career path analysis failed: {e}")
            return self._fallback_career_analysis(profile)
    
    async def generate_recommendations(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate career recommendations based on analysis data
        
        Args:
            analysis_data: Dictionary containing analysis results and context
            
        Returns:
            Dictionary containing recommendations and action items
        """
        if not self.available or not self.adaptive_engine:
            return self._fallback_recommendations(analysis_data)
        
        try:
            # Use adaptive engine for intelligent recommendations
            resume_text = analysis_data.get('resume_text', '')
            context = analysis_data.get('context', {})
            
            # Generate adaptive recommendations
            recommendations = await self.adaptive_engine.generate_adaptive_recommendations(
                resume_text, context
            )
            
            return self._process_recommendations_result(recommendations)
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return self._fallback_recommendations(analysis_data)
    
    async def calculate_market_demand(self, skills: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate market demand for skills
        
        Args:
            skills: List of skills to analyze
            context: Optional context (sector, location, etc.)
            
        Returns:
            Dictionary containing market demand analysis
        """
        if not self.available:
            return self._fallback_market_demand(skills)
        
        try:
            # Use market intelligence component if available
            if hasattr(self.engine, '_market_roadmap_analyzer'):
                analyzer = self.engine._market_roadmap_analyzer
                
                # Get sector data for context
                sector = context.get('sector', 'Technology') if context else 'Technology'
                sector_data = analyzer.get_sector_data(sector)
                
                # Analyze skill demand within sector
                demand_analysis = self._analyze_skill_demand_in_sector(skills, sector_data)
                
                return {
                    "success": True,
                    "skills_demand": demand_analysis,
                    "sector": sector,
                    "analysis_method": "strategic_career_analysis",
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "total_skills_analyzed": len(skills)
                    }
                }
            else:
                return self._fallback_market_demand(skills)
                
        except Exception as e:
            logger.error(f"Market demand calculation failed: {e}")
            return self._fallback_market_demand(skills)
    
    async def assess_skill_gaps(self, resume_text: str, target_role: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess skill gaps for a target role
        
        Args:
            resume_text: Resume text to analyze
            target_role: Target role information (title, requirements, etc.)
            
        Returns:
            Dictionary containing skill gap analysis
        """
        if not self.available or not self.engine:
            return self._fallback_skill_gaps(resume_text, target_role)
        
        try:
            # Create job data from target role
            job_data = {
                'job_title': target_role.get('title', 'Unknown Position'),
                'job_description': target_role.get('description', ''),
                'skills': [{'skill_name': skill, 'must_have_indicator': True} 
                          for skill in target_role.get('required_skills', [])],
                'company': target_role.get('company', 'Unknown Company')
            }
            
            # Perform single job analysis
            result = self.engine.analyze_single_job(
                resume_text, 
                job_data, 
                target_role.get('id', 'target_role')
            )
            
            # Extract skill gaps
            skill_gaps = []
            skill_matches = []
            
            for skill_analysis in result.skill_analysis:
                if skill_analysis['status'] == 'Missing':
                    skill_gaps.append({
                        'skill': skill_analysis['skill_name'],
                        'importance': 'high' if skill_analysis.get('must_have_indicator', False) else 'medium',
                        'substitution_available': bool(skill_analysis.get('substitution_reasoning')),
                        'substitution_confidence': skill_analysis.get('substitution_confidence', 'None')
                    })
                else:
                    skill_matches.append({
                        'skill': skill_analysis['skill_name'],
                        'status': skill_analysis['status'],
                        'confidence': skill_analysis['confidence_score']
                    })
            
            return {
                "success": True,
                "overall_match_score": result.overall_match_score,
                "skill_gaps": skill_gaps,
                "skill_matches": skill_matches,
                "critical_gaps": result.critical_gaps,
                "recommendations": result.recommendations,
                "analysis_method": "strategic_career_analysis",
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "target_role": target_role.get('title', 'Unknown'),
                    "total_gaps": len(skill_gaps),
                    "total_matches": len(skill_matches)
                }
            }
            
        except Exception as e:
            logger.error(f"Skill gap assessment failed: {e}")
            return self._fallback_skill_gaps(resume_text, target_role)
    
    def _process_single_job_result(self, result: 'SkillEvidenceReport') -> Dict[str, Any]:
        """Process single job analysis result"""
        return {
            "success": True,
            "analysis_type": "single_job",
            "job_id": result.job_id,
            "job_title": result.job_title,
            "overall_match_score": result.overall_match_score,
            "category_scores": result.category_scores,
            "critical_gaps": result.critical_gaps,
            "skill_analysis": result.skill_analysis,
            "recommendations": result.recommendations,
            "processing_time": getattr(result, 'processing_time_seconds', None),
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "analysis_method": "strategic_career_analysis"
            }
        }
    
    def _process_sector_analysis_result(self, result: 'SectorReadinessSummary') -> Dict[str, Any]:
        """Process sector analysis result"""
        return {
            "success": True,
            "analysis_type": "sector_analysis",
            "sector": result.sector,
            "market_alignment": {
                "overall_percentage": result.market_alignment.overall_percentage,
                "technical_alignment": result.market_alignment.technical_alignment,
                "business_alignment": result.market_alignment.business_alignment,
                "soft_skills_alignment": result.market_alignment.soft_skills_alignment
            },
            "top_sector_skills": [
                {
                    "skill": skill.skill,
                    "market_frequency": skill.market_frequency,
                    "candidate_status": skill.candidate_status,
                    "transferability_score": skill.transferability_score
                }
                for skill in result.top_sector_skills
            ],
            "transferability_analysis": {
                "high_transfer_skills": result.transferability_analysis.high_transfer_skills,
                "moderate_transfer_skills": result.transferability_analysis.moderate_transfer_skills,
                "development_needed": result.transferability_analysis.development_needed
            },
            "strategic_recommendations": {
                "priority_skills": result.strategic_recommendations.priority_skills,
                "learning_timeline": result.strategic_recommendations.learning_timeline,
                "career_pathway": result.strategic_recommendations.career_pathway
            },
            "processing_time": getattr(result, 'processing_time_seconds', None),
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "analysis_method": "strategic_career_analysis"
            }
        }
    
    def _process_career_guidance_result(self, result: 'CareerGuidanceReport') -> Dict[str, Any]:
        """Process career guidance result"""
        return {
            "success": True,
            "analysis_type": "career_guidance",
            "fit_assessment": {
                "individual_fit": result.fit_assessment.individual_fit,
                "sector_fit": result.fit_assessment.sector_fit,
                "skill_depth": result.fit_assessment.skill_depth,
                "overall_fit": result.fit_assessment.overall_fit
            },
            "career_pathway": {
                "current_level": result.career_pathway.current_level,
                "target_level": result.career_pathway.target_level,
                "progression_steps": result.career_pathway.progression_steps,
                "timeline_estimate": result.career_pathway.timeline_estimate,
                "key_milestones": result.career_pathway.key_milestones
            },
            "priority_recommendations": result.priority_recommendations,
            "industry_trends": result.industry_trends,
            "skill_gap_priorities": result.skill_gap_priorities,
            "processing_time": getattr(result, 'processing_time_seconds', None),
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "analysis_method": "strategic_career_analysis"
            }
        }
    
    def _process_recommendations_result(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Process recommendations result"""
        return {
            "success": True,
            "recommendations": recommendations,
            "analysis_method": "adaptive_strategic_analysis",
            "metadata": {
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _analyze_skill_demand_in_sector(self, skills: List[str], sector_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze skill demand within a specific sector"""
        sector_skills = sector_data.get('top_skills', [])
        skill_demand_map = {skill.get('skill', '').lower(): skill.get('frequency', 0.0) 
                           for skill in sector_skills}
        
        demand_analysis = []
        
        for skill in skills:
            skill_lower = skill.lower()
            demand_score = skill_demand_map.get(skill_lower, 0.0)
            
            # Categorize demand level
            if demand_score >= 0.7:
                demand_level = "high"
            elif demand_score >= 0.4:
                demand_level = "medium"
            elif demand_score >= 0.1:
                demand_level = "low"
            else:
                demand_level = "minimal"
            
            demand_analysis.append({
                "skill": skill,
                "demand_score": demand_score,
                "demand_level": demand_level,
                "market_frequency": demand_score
            })
        
        return demand_analysis
    
    def _fallback_career_analysis(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback career analysis using basic heuristics"""
        return {
            "success": True,
            "analysis_type": "fallback",
            "overall_assessment": "moderate_fit",
            "key_strengths": ["Experience", "Education", "Skills"],
            "improvement_areas": ["Skill gaps", "Experience depth", "Industry knowledge"],
            "recommendations": [
                "Continue developing technical skills",
                "Gain more industry-specific experience",
                "Build professional network",
                "Consider additional certifications"
            ],
            "analysis_method": "fallback_heuristics",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "fallback_reason": "Career analysis engine not available"
            }
        }
    
    def _fallback_recommendations(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback recommendations using basic rules"""
        return {
            "success": True,
            "immediate_actions": [
                "Update resume with recent achievements",
                "Identify target companies and roles",
                "Network with industry professionals"
            ],
            "skill_development": [
                "Focus on in-demand technical skills",
                "Develop leadership capabilities",
                "Improve communication skills"
            ],
            "long_term_strategy": [
                "Build expertise in emerging technologies",
                "Consider advanced education or certifications",
                "Develop thought leadership through content creation"
            ],
            "analysis_method": "fallback_recommendations",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "fallback_reason": "Adaptive engine not available"
            }
        }
    
    def _fallback_market_demand(self, skills: List[str]) -> Dict[str, Any]:
        """Fallback market demand analysis"""
        # Basic demand scoring based on common industry trends
        high_demand_skills = ['python', 'javascript', 'react', 'aws', 'kubernetes', 'machine learning', 'data science']
        medium_demand_skills = ['java', 'c++', 'sql', 'project management', 'agile', 'leadership']
        
        skills_demand = []
        
        for skill in skills:
            skill_lower = skill.lower()
            
            if any(hd_skill in skill_lower for hd_skill in high_demand_skills):
                demand_level = "high"
                demand_score = 0.8
            elif any(md_skill in skill_lower for md_skill in medium_demand_skills):
                demand_level = "medium"
                demand_score = 0.6
            else:
                demand_level = "low"
                demand_score = 0.3
            
            skills_demand.append({
                "skill": skill,
                "demand_score": demand_score,
                "demand_level": demand_level,
                "market_frequency": demand_score
            })
        
        return {
            "success": True,
            "skills_demand": skills_demand,
            "sector": "general",
            "analysis_method": "fallback_demand_analysis",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "fallback_reason": "Market analysis engine not available"
            }
        }
    
    def _fallback_skill_gaps(self, resume_text: str, target_role: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback skill gap analysis"""
        required_skills = target_role.get('required_skills', [])
        resume_lower = resume_text.lower()
        
        skill_gaps = []
        skill_matches = []
        
        for skill in required_skills:
            if skill.lower() in resume_lower:
                skill_matches.append({
                    'skill': skill,
                    'status': 'Found',
                    'confidence': 0.6
                })
            else:
                skill_gaps.append({
                    'skill': skill,
                    'importance': 'medium',
                    'substitution_available': False,
                    'substitution_confidence': 'None'
                })
        
        match_percentage = len(skill_matches) / len(required_skills) * 100 if required_skills else 0
        
        return {
            "success": True,
            "overall_match_score": match_percentage,
            "skill_gaps": skill_gaps,
            "skill_matches": skill_matches,
            "critical_gaps": [gap['skill'] for gap in skill_gaps[:3]],
            "recommendations": [
                f"Develop skills in {', '.join([gap['skill'] for gap in skill_gaps[:3]])}",
                "Highlight relevant experience more prominently",
                "Consider additional training or certifications"
            ],
            "analysis_method": "fallback_skill_gaps",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "fallback_reason": "Strategic analysis engine not available"
            }
        }
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get the status of the career analysis engine"""
        if not self.available:
            return {
                "available": False,
                "healthy": False,
                "reason": "Strategic career analysis engine not available"
            }
        
        if not self.engine:
            return {
                "available": False,
                "healthy": False,
                "reason": "Engine failed to initialize"
            }
        
        try:
            # Get processing status
            status = self.engine.get_processing_status()
            
            return {
                "available": True,
                "healthy": True,
                "processing_status": {
                    "stage": status.stage,
                    "progress": status.progress_percentage,
                    "current_task": status.current_task,
                    "errors": [{"type": err.error_type, "message": err.error_message, "component": err.component} 
                              for err in status.errors]
                },
                "engines": {
                    "main_engine": self.engine is not None,
                    "adaptive_engine": self.adaptive_engine is not None,
                    "single_pass_engine": self.single_pass_engine is not None
                }
            }
            
        except Exception as e:
            return {
                "available": True,
                "healthy": False,
                "error": str(e)
            }
    
    def is_available(self) -> bool:
        """Check if the career analysis engine is available"""
        return self.available and self.engine is not None
    
    def get_supported_analysis_types(self) -> List[str]:
        """Get list of supported analysis types"""
        return [
            "single_job",
            "sector_analysis", 
            "career_guidance",
            "skill_gap_assessment",
            "market_demand_analysis"
        ]