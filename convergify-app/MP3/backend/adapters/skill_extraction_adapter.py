"""
Skill Extraction Adapter - Integration with enhanced_skill_extraction engine
"""
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging
from datetime import datetime

# Add the project root to Python path to import existing engines
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from enhanced_skill_extraction.skills_engine import EnhancedSkillsEngine, extract_skills_from_job
    from enhanced_skill_extraction.models import JobEntry, JobContext, SkillExtractionResult
    from enhanced_skill_extraction.config import EnhancedConfig
    from enhanced_skill_extraction.llm_skill_analyzer import ErrorResponse
    SKILL_EXTRACTION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Enhanced skill extraction not available: {e}")
    SKILL_EXTRACTION_AVAILABLE = False

logger = logging.getLogger(__name__)

class SkillExtractionAdapter:
    """Adapter for integrating with the enhanced skill extraction engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the skill extraction adapter
        
        Args:
            config: Configuration dictionary for the skill extraction engine
        """
        self.available = SKILL_EXTRACTION_AVAILABLE
        self.engine = None
        self.config = None
        
        if self.available:
            try:
                # Create enhanced config if provided
                if config:
                    self.config = self._create_enhanced_config(config)
                
                # Initialize the skills engine
                self.engine = EnhancedSkillsEngine(self.config)
                logger.info("SkillExtractionAdapter initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize skill extraction engine: {e}")
                self.available = False
                self.engine = None
        else:
            logger.warning("Skill extraction engine not available - adapter will use fallback methods")
    
    def _create_enhanced_config(self, config_dict: Dict[str, Any]) -> Optional['EnhancedConfig']:
        """Create EnhancedConfig from dictionary"""
        try:
            # For now, use default config
            # In a full implementation, you'd map config_dict to EnhancedConfig
            return EnhancedConfig()
        except Exception as e:
            logger.error(f"Failed to create enhanced config: {e}")
            return None
    
    async def extract_from_resume(self, resume_text: str, resume_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract skills from resume text
        
        Args:
            resume_text: The resume text content
            resume_id: Optional resume identifier
            
        Returns:
            Dictionary containing extracted skills and metadata
        """
        if not self.available or not self.engine:
            return self._fallback_skill_extraction(resume_text, "resume")
        
        try:
            # Create a job entry from resume text (treating resume as job description)
            job_entry = self._create_job_entry_from_text(
                text=resume_text,
                entry_id=resume_id or f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                entry_type="resume"
            )
            
            # Extract skills using the engine
            result = self.engine.process(job_entry)
            
            # Process the result
            return self._process_extraction_result(result, "resume")
            
        except Exception as e:
            logger.error(f"Resume skill extraction failed: {e}")
            return self._fallback_skill_extraction(resume_text, "resume")
    
    async def extract_from_job(self, job_description: str, job_id: Optional[str] = None, 
                              job_title: Optional[str] = None, company: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract required skills from job description
        
        Args:
            job_description: The job description text
            job_id: Optional job identifier
            job_title: Optional job title for context
            company: Optional company name for context
            
        Returns:
            Dictionary containing extracted skills and metadata
        """
        if not self.available or not self.engine:
            return self._fallback_skill_extraction(job_description, "job")
        
        try:
            # Create job entry
            job_entry = self._create_job_entry_from_text(
                text=job_description,
                entry_id=job_id or f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                entry_type="job",
                title=job_title,
                company=company
            )
            
            # Create job context if we have additional information
            job_context = None
            if job_title or company:
                job_context = self._create_job_context(job_title, company)
            
            # Extract skills using the engine
            result = self.engine.process(job_entry, job_context)
            
            # Process the result
            return self._process_extraction_result(result, "job")
            
        except Exception as e:
            logger.error(f"Job skill extraction failed: {e}")
            return self._fallback_skill_extraction(job_description, "job")
    
    async def batch_extract(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract skills from multiple documents
        
        Args:
            documents: List of documents, each containing 'text', 'id', and 'type' keys
            
        Returns:
            List of extraction results
        """
        results = []
        
        for doc in documents:
            text = doc.get('text', '')
            doc_id = doc.get('id')
            doc_type = doc.get('type', 'unknown')
            
            if doc_type == 'resume':
                result = await self.extract_from_resume(text, doc_id)
            elif doc_type == 'job':
                result = await self.extract_from_job(
                    text, 
                    doc_id, 
                    doc.get('title'), 
                    doc.get('company')
                )
            else:
                # Generic extraction
                if self.available and self.engine:
                    job_entry = self._create_job_entry_from_text(text, doc_id or f"doc_{len(results)}", doc_type)
                    engine_result = self.engine.process(job_entry)
                    result = self._process_extraction_result(engine_result, doc_type)
                else:
                    result = self._fallback_skill_extraction(text, doc_type)
            
            results.append(result)
        
        return results
    
    def _create_job_entry_from_text(self, text: str, entry_id: str, entry_type: str, 
                                   title: Optional[str] = None, company: Optional[str] = None) -> 'JobEntry':
        """Create a JobEntry object from text"""
        if not SKILL_EXTRACTION_AVAILABLE:
            raise ImportError("JobEntry not available")
        
        # Create a basic job entry
        # The exact structure depends on your JobEntry model
        job_entry = JobEntry(
            id=entry_id,
            description=text,
            job_description=text,  # Some models might expect this field
            title=title or f"{entry_type.title()} Entry",
            company=company or "Unknown"
        )
        
        return job_entry
    
    def _create_job_context(self, job_title: Optional[str], company: Optional[str]) -> Optional['JobContext']:
        """Create a JobContext object"""
        if not SKILL_EXTRACTION_AVAILABLE or not (job_title or company):
            return None
        
        try:
            return JobContext(
                job_title=job_title or "Unknown Position",
                company_name=company or "Unknown Company",
                industry=None,  # Could be inferred or provided
                seniority_level=None  # Could be inferred from job title
            )
        except Exception as e:
            logger.error(f"Failed to create job context: {e}")
            return None
    
    def _process_extraction_result(self, result: Union['SkillExtractionResult', 'ErrorResponse'], 
                                  source_type: str) -> Dict[str, Any]:
        """Process the extraction result from the engine"""
        
        if isinstance(result, ErrorResponse):
            # Handle error response
            return {
                "success": False,
                "skills": result.partial_results if result.partial_results else [],
                "error": result.error_message,
                "error_type": result.error_type,
                "source_type": source_type,
                "extraction_method": "enhanced_engine_error",
                "metadata": {
                    "timestamp": result.timestamp.isoformat() if result.timestamp else None,
                    "fallback_used": result.fallback_used,
                    "context": result.context
                }
            }
        
        elif hasattr(result, 'extracted_skills'):
            # Handle successful SkillExtractionResult
            skills = []
            
            for skill in result.extracted_skills:
                skill_data = {
                    "name": skill.name,
                    "category": getattr(skill, 'category', 'unknown'),
                    "confidence": getattr(skill, 'confidence', 0.5),
                    "importance": getattr(skill, 'importance', 0.5),
                    "evidence": getattr(skill, 'evidence', []),
                    "explanation": getattr(skill, 'explanation', ''),
                    "priority": getattr(skill, 'priority', 'medium')
                }
                skills.append(skill_data)
            
            return {
                "success": True,
                "skills": skills,
                "total_skills": len(skills),
                "source_type": source_type,
                "extraction_method": "enhanced_engine",
                "metadata": {
                    "job_id": result.job_id,
                    "processing_time": getattr(result.processing_metadata, 'processing_time', None) if hasattr(result, 'processing_metadata') else None,
                    "llm_calls": getattr(result.processing_metadata, 'llm_calls_made', None) if hasattr(result, 'processing_metadata') else None,
                    "model_used": getattr(result.processing_metadata, 'model_used', None) if hasattr(result, 'processing_metadata') else None,
                    "timestamp": datetime.now().isoformat()
                }
            }
        
        else:
            # Unexpected result type
            return {
                "success": False,
                "skills": [],
                "error": f"Unexpected result type: {type(result)}",
                "source_type": source_type,
                "extraction_method": "enhanced_engine_error"
            }
    
    def _fallback_skill_extraction(self, text: str, source_type: str) -> Dict[str, Any]:
        """Fallback skill extraction using simple keyword matching"""
        
        # Basic skill keywords (this would be much more comprehensive in a real implementation)
        skill_keywords = {
            'programming': ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift'],
            'web': ['html', 'css', 'react', 'vue', 'angular', 'node.js', 'express', 'django', 'flask'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'tools': ['git', 'jenkins', 'jira', 'confluence', 'slack', 'figma'],
            'soft_skills': ['communication', 'leadership', 'teamwork', 'problem solving', 'analytical']
        }
        
        text_lower = text.lower()
        found_skills = []
        
        for category, keywords in skill_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_skills.append({
                        "name": keyword.title(),
                        "category": category,
                        "confidence": 0.3,  # Low confidence for keyword matching
                        "importance": 0.4,
                        "evidence": [f"Found keyword '{keyword}' in text"],
                        "explanation": f"Detected through keyword matching",
                        "priority": "low"
                    })
        
        return {
            "success": True,
            "skills": found_skills,
            "total_skills": len(found_skills),
            "source_type": source_type,
            "extraction_method": "fallback_keywords",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "fallback_reason": "Enhanced engine not available"
            }
        }
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get the status of the skill extraction engine"""
        if not self.available:
            return {
                "available": False,
                "healthy": False,
                "reason": "Enhanced skill extraction engine not available"
            }
        
        if not self.engine:
            return {
                "available": False,
                "healthy": False,
                "reason": "Engine failed to initialize"
            }
        
        try:
            health_status = self.engine.get_health_status()
            return {
                "available": True,
                "healthy": health_status.get("healthy", False),
                "engine_metrics": self.engine.get_pipeline_metrics(),
                "component_health": health_status.get("component_health", {}),
                "configuration": health_status.get("configuration", {})
            }
        except Exception as e:
            return {
                "available": True,
                "healthy": False,
                "error": str(e)
            }
    
    def reset_engine_stats(self):
        """Reset engine statistics"""
        if self.available and self.engine:
            try:
                self.engine.reset_metrics()
                logger.info("Engine statistics reset successfully")
            except Exception as e:
                logger.error(f"Failed to reset engine statistics: {e}")
    
    def is_available(self) -> bool:
        """Check if the skill extraction engine is available"""
        return self.available and self.engine is not None
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported input formats"""
        return ["text", "resume", "job_description"]