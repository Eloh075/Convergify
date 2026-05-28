"""
Skill Classification Adapter - Integration with skills_classification_engine
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
    from skills_classification_engine.engine import SkillsClassificationEngine
    from skills_classification_engine.models import JobEntry, ClassifiedSkill, ProcessingResult
    from skills_classification_engine.classifier import SkillClassifier
    from skills_classification_engine.taxonomy import TaxonomyValidator
    from skills_classification_engine.skill_normalizer import SkillNormalizer
    from skills_classification_engine.gemini_client import GeminiClient
    SKILL_CLASSIFICATION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Skills classification engine not available: {e}")
    SKILL_CLASSIFICATION_AVAILABLE = False

logger = logging.getLogger(__name__)

class SkillClassificationAdapter:
    """Adapter for integrating with the skills classification engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the skill classification adapter
        
        Args:
            config: Configuration dictionary for the classification engine
        """
        self.available = SKILL_CLASSIFICATION_AVAILABLE
        self.engine = None
        self.classifier = None
        self.taxonomy_validator = None
        self.normalizer = None
        
        if self.available:
            try:
                # Extract configuration
                gemini_api_key = config.get('gemini_api_key') if config else None
                gemini_model = config.get('gemini_model') if config else None
                
                # Initialize the classification engine
                self.engine = SkillsClassificationEngine(
                    gemini_api_key=gemini_api_key,
                    gemini_model=gemini_model
                )
                
                # Initialize individual components for direct access
                self.taxonomy_validator = TaxonomyValidator()
                
                if gemini_api_key:
                    gemini_client = GeminiClient(gemini_api_key, gemini_model)
                    self.normalizer = SkillNormalizer(gemini_client)
                
                logger.info("SkillClassificationAdapter initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize skill classification engine: {e}")
                self.available = False
                self.engine = None
        else:
            logger.warning("Skill classification engine not available - adapter will use fallback methods")
    
    async def classify_skills(self, skills: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Classify skills into categories
        
        Args:
            skills: List of skill names to classify
            context: Optional context information (job title, company, etc.)
            
        Returns:
            Dictionary containing classified skills and metadata
        """
        if not self.available or not self.engine:
            return self._fallback_skill_classification(skills)
        
        try:
            # Create a mock job entry for classification
            job_entry = self._create_job_entry_from_skills(skills, context)
            
            # Use the engine's classifier to classify skills
            classified_skills = self.engine.classifier.classify_skills_for_job(job_entry)
            
            # Process the results
            return self._process_classification_result(classified_skills, skills)
            
        except Exception as e:
            logger.error(f"Skill classification failed: {e}")
            return self._fallback_skill_classification(skills)
    
    async def normalize_skills(self, skills: List[str]) -> List[str]:
        """
        Normalize skill names to canonical forms
        
        Args:
            skills: List of skill names to normalize
            
        Returns:
            List of normalized skill names
        """
        if not self.available or not self.normalizer:
            return self._fallback_skill_normalization(skills)
        
        try:
            # Create classified skills for normalization
            classified_skills = []
            for skill in skills:
                # Create a basic classified skill object
                classified_skill = ClassifiedSkill(
                    raw_skill=skill,
                    tier1_category="Unknown",
                    tier2_category="Unknown",
                    tier3_category="Unknown",
                    confidence_score=0.5,
                    raw_frequency=1,
                    context_frequency=1
                )
                classified_skills.append(classified_skill)
            
            # Normalize using the engine's normalizer
            normalized_groups = self.normalizer.normalize_skills(classified_skills)
            
            # Extract canonical names
            normalized_skills = [group.canonical_name for group in normalized_groups]
            
            return normalized_skills
            
        except Exception as e:
            logger.error(f"Skill normalization failed: {e}")
            return self._fallback_skill_normalization(skills)
    
    async def get_skill_taxonomy(self) -> Dict[str, Any]:
        """
        Get the complete skill taxonomy
        
        Returns:
            Dictionary containing the skill taxonomy structure
        """
        if not self.available or not self.taxonomy_validator:
            return self._fallback_taxonomy()
        
        try:
            # Get valid categories from taxonomy validator
            categories = self.taxonomy_validator.get_valid_categories()
            
            return {
                "success": True,
                "taxonomy": categories,
                "total_categories": len(categories),
                "source": "skills_classification_engine",
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get skill taxonomy: {e}")
            return self._fallback_taxonomy()
    
    async def validate_skill_category(self, skill: str, category: str) -> bool:
        """
        Validate if a skill belongs to a specific category
        
        Args:
            skill: Skill name
            category: Category to validate against
            
        Returns:
            True if the skill-category combination is valid
        """
        if not self.available or not self.taxonomy_validator:
            return True  # Fallback: assume valid
        
        try:
            return self.taxonomy_validator.is_valid_category(category)
        except Exception as e:
            logger.error(f"Skill category validation failed: {e}")
            return True  # Fallback: assume valid
    
    def _create_job_entry_from_skills(self, skills: List[str], context: Optional[Dict[str, Any]] = None) -> 'JobEntry':
        """Create a JobEntry object from skills list"""
        if not SKILL_CLASSIFICATION_AVAILABLE:
            raise ImportError("JobEntry not available")
        
        # Extract context information
        job_title = context.get('job_title', 'Unknown Position') if context else 'Unknown Position'
        company = context.get('company', 'Unknown Company') if context else 'Unknown Company'
        
        # Create job description from skills
        job_description = f"Position requiring skills: {', '.join(skills)}"
        
        # Create job entry
        job_entry = JobEntry(
            title=job_title,
            company=company,
            description=job_description,
            required_skills=skills,
            location=context.get('location', 'Unknown') if context else 'Unknown',
            employment_type=context.get('employment_type', 'Full-time') if context else 'Full-time'
        )
        
        return job_entry
    
    def _process_classification_result(self, classified_skills: List['ClassifiedSkill'], 
                                     original_skills: List[str]) -> Dict[str, Any]:
        """Process classification results into standardized format"""
        
        processed_skills = []
        
        for classified_skill in classified_skills:
            skill_data = {
                "original_name": classified_skill.raw_skill,
                "tier1_category": classified_skill.tier1_category,
                "tier2_category": classified_skill.tier2_category,
                "tier3_category": classified_skill.tier3_category,
                "confidence": classified_skill.confidence_score,
                "frequency": {
                    "raw": classified_skill.raw_frequency,
                    "context": classified_skill.context_frequency
                }
            }
            processed_skills.append(skill_data)
        
        return {
            "success": True,
            "classified_skills": processed_skills,
            "total_skills": len(processed_skills),
            "original_count": len(original_skills),
            "classification_method": "skills_classification_engine",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "engine_version": "1.0.0"
            }
        }
    
    def _fallback_skill_classification(self, skills: List[str]) -> Dict[str, Any]:
        """Fallback skill classification using predefined categories"""
        
        # Basic skill categories mapping
        category_mapping = {
            # Programming languages
            'python': ('Technical Skills', 'Programming Languages', 'Python'),
            'javascript': ('Technical Skills', 'Programming Languages', 'JavaScript'),
            'java': ('Technical Skills', 'Programming Languages', 'Java'),
            'c++': ('Technical Skills', 'Programming Languages', 'C++'),
            'c#': ('Technical Skills', 'Programming Languages', 'C#'),
            'php': ('Technical Skills', 'Programming Languages', 'PHP'),
            'ruby': ('Technical Skills', 'Programming Languages', 'Ruby'),
            'go': ('Technical Skills', 'Programming Languages', 'Go'),
            'rust': ('Technical Skills', 'Programming Languages', 'Rust'),
            'swift': ('Technical Skills', 'Programming Languages', 'Swift'),
            
            # Web technologies
            'html': ('Technical Skills', 'Web Technologies', 'HTML'),
            'css': ('Technical Skills', 'Web Technologies', 'CSS'),
            'react': ('Technical Skills', 'Web Technologies', 'React'),
            'vue': ('Technical Skills', 'Web Technologies', 'Vue.js'),
            'angular': ('Technical Skills', 'Web Technologies', 'Angular'),
            'node.js': ('Technical Skills', 'Web Technologies', 'Node.js'),
            'express': ('Technical Skills', 'Web Technologies', 'Express.js'),
            'django': ('Technical Skills', 'Web Technologies', 'Django'),
            'flask': ('Technical Skills', 'Web Technologies', 'Flask'),
            
            # Databases
            'sql': ('Technical Skills', 'Databases', 'SQL'),
            'mysql': ('Technical Skills', 'Databases', 'MySQL'),
            'postgresql': ('Technical Skills', 'Databases', 'PostgreSQL'),
            'mongodb': ('Technical Skills', 'Databases', 'MongoDB'),
            'redis': ('Technical Skills', 'Databases', 'Redis'),
            'elasticsearch': ('Technical Skills', 'Databases', 'Elasticsearch'),
            
            # Cloud & DevOps
            'aws': ('Technical Skills', 'Cloud Platforms', 'AWS'),
            'azure': ('Technical Skills', 'Cloud Platforms', 'Azure'),
            'gcp': ('Technical Skills', 'Cloud Platforms', 'Google Cloud'),
            'docker': ('Technical Skills', 'DevOps', 'Docker'),
            'kubernetes': ('Technical Skills', 'DevOps', 'Kubernetes'),
            'terraform': ('Technical Skills', 'DevOps', 'Terraform'),
            
            # Tools
            'git': ('Technical Skills', 'Development Tools', 'Git'),
            'jenkins': ('Technical Skills', 'Development Tools', 'Jenkins'),
            'jira': ('Technical Skills', 'Development Tools', 'Jira'),
            'confluence': ('Technical Skills', 'Development Tools', 'Confluence'),
            
            # Soft skills
            'communication': ('Soft Skills', 'Communication', 'Communication'),
            'leadership': ('Soft Skills', 'Leadership', 'Leadership'),
            'teamwork': ('Soft Skills', 'Collaboration', 'Teamwork'),
            'problem solving': ('Soft Skills', 'Problem Solving', 'Problem Solving'),
            'analytical': ('Soft Skills', 'Analytical', 'Analytical Thinking')
        }
        
        classified_skills = []
        
        for skill in skills:
            skill_lower = skill.lower()
            
            if skill_lower in category_mapping:
                tier1, tier2, tier3 = category_mapping[skill_lower]
                confidence = 0.7  # Medium confidence for predefined mappings
            else:
                # Default categorization
                tier1, tier2, tier3 = 'Technical Skills', 'Other', 'Unclassified'
                confidence = 0.3  # Low confidence for unknown skills
            
            classified_skills.append({
                "original_name": skill,
                "tier1_category": tier1,
                "tier2_category": tier2,
                "tier3_category": tier3,
                "confidence": confidence,
                "frequency": {
                    "raw": 1,
                    "context": 1
                }
            })
        
        return {
            "success": True,
            "classified_skills": classified_skills,
            "total_skills": len(classified_skills),
            "original_count": len(skills),
            "classification_method": "fallback_mapping",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "fallback_reason": "Classification engine not available"
            }
        }
    
    def _fallback_skill_normalization(self, skills: List[str]) -> List[str]:
        """Fallback skill normalization using simple rules"""
        
        # Basic normalization rules
        normalization_map = {
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'py': 'Python',
            'node': 'Node.js',
            'react.js': 'React',
            'vue.js': 'Vue',
            'angular.js': 'Angular',
            'postgresql': 'PostgreSQL',
            'mysql': 'MySQL',
            'mongodb': 'MongoDB',
            'aws': 'Amazon Web Services',
            'gcp': 'Google Cloud Platform',
            'k8s': 'Kubernetes'
        }
        
        normalized_skills = []
        
        for skill in skills:
            skill_lower = skill.lower()
            
            if skill_lower in normalization_map:
                normalized_skills.append(normalization_map[skill_lower])
            else:
                # Basic capitalization
                normalized_skills.append(skill.title())
        
        return normalized_skills
    
    def _fallback_taxonomy(self) -> Dict[str, Any]:
        """Fallback taxonomy structure"""
        
        taxonomy = {
            "Technical Skills": {
                "Programming Languages": ["Python", "JavaScript", "Java", "C++", "C#", "PHP", "Ruby", "Go", "Rust", "Swift"],
                "Web Technologies": ["HTML", "CSS", "React", "Vue.js", "Angular", "Node.js", "Express.js", "Django", "Flask"],
                "Databases": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch"],
                "Cloud Platforms": ["AWS", "Azure", "Google Cloud"],
                "DevOps": ["Docker", "Kubernetes", "Terraform", "Jenkins", "CI/CD"],
                "Development Tools": ["Git", "Jira", "Confluence", "VS Code", "IntelliJ"]
            },
            "Soft Skills": {
                "Communication": ["Communication", "Presentation", "Writing"],
                "Leadership": ["Leadership", "Management", "Mentoring"],
                "Collaboration": ["Teamwork", "Cross-functional", "Agile"],
                "Problem Solving": ["Problem Solving", "Critical Thinking", "Debugging"],
                "Analytical": ["Analytical Thinking", "Data Analysis", "Research"]
            }
        }
        
        return {
            "success": True,
            "taxonomy": taxonomy,
            "total_categories": sum(len(subcats) for cats in taxonomy.values() for subcats in cats.values()),
            "source": "fallback_taxonomy",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "fallback_reason": "Classification engine not available"
            }
        }
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get the status of the skill classification engine"""
        if not self.available:
            return {
                "available": False,
                "healthy": False,
                "reason": "Skills classification engine not available"
            }
        
        if not self.engine:
            return {
                "available": False,
                "healthy": False,
                "reason": "Engine failed to initialize"
            }
        
        try:
            # Test connection to external services
            connection_ok = self.engine.test_connection()
            
            # Get system info
            system_info = self.engine.get_system_info()
            
            # Get processing statistics
            stats = self.engine.get_processing_statistics()
            
            return {
                "available": True,
                "healthy": connection_ok,
                "system_info": system_info,
                "processing_stats": stats,
                "connection_status": connection_ok
            }
            
        except Exception as e:
            return {
                "available": True,
                "healthy": False,
                "error": str(e)
            }
    
    def is_available(self) -> bool:
        """Check if the skill classification engine is available"""
        return self.available and self.engine is not None
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return [
            "classify_skills",
            "normalize_skills", 
            "get_skill_taxonomy",
            "validate_skill_category"
        ]