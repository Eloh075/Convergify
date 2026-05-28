"""Experience level normalizer for consistent experience level mapping."""

from typing import Optional


class ExperienceLevelNormalizer:
    """Normalizes experience levels across different job sites."""
    
    # LinkedIn's standard experience levels
    LINKEDIN_LEVELS = {
        "internship": "internship",
        "entry": "entry",
        "associate": "associate", 
        "mid": "mid",
        "senior": "senior",
        "executive": "executive"
    }
    
    # Skills Career employment types to LinkedIn levels mapping
    SKILLS_CAREER_MAPPING = {
        "internship": "internship",
        "attachment": "internship",
        "permanent": "entry",
        "fulltime": "entry",
        "parttime": "entry",
        "contract": "associate",
        "temporary": "associate",
        "freelance": "associate"
    }
    
    def normalize_linkedin_level(self, level: str) -> str:
        """Normalize LinkedIn experience level."""
        if not level:
            return ""
        
        level_lower = level.lower().strip()
        return self.LINKEDIN_LEVELS.get(level_lower, level_lower)
    
    def normalize_skills_career_level(self, employment_type: str) -> str:
        """Map Skills Career employment type to LinkedIn experience level."""
        if not employment_type:
            return ""
        
        employment_lower = employment_type.lower().strip()
        return self.SKILLS_CAREER_MAPPING.get(employment_lower, "entry")
    
    def normalize_indeed_level(self, level: str) -> str:
        """Normalize Indeed experience level to LinkedIn standard."""
        if not level:
            return ""
        
        level_lower = level.lower().strip()
        
        # Map Indeed-specific terms to LinkedIn levels
        indeed_mapping = {
            "entry level": "entry",
            "entry-level": "entry",
            "junior": "entry",
            "mid level": "mid",
            "mid-level": "mid",
            "senior level": "senior",
            "senior-level": "senior",
            "lead": "senior",
            "principal": "executive",
            "director": "executive",
            "manager": "senior"
        }
        
        return indeed_mapping.get(level_lower, self.LINKEDIN_LEVELS.get(level_lower, level_lower))
    
    def get_all_linkedin_levels(self) -> list:
        """Get all valid LinkedIn experience levels."""
        return list(self.LINKEDIN_LEVELS.values())