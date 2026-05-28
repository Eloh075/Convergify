"""
Configuration for Strategic Career Analysis Engines
"""
import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class EngineConfig:
    """Configuration for all analysis engines"""
    
    # Gemini API Configuration - Multiple keys for rotation
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_API_KEYS: List[str] = []  # Will be populated from env
    GEMINI_MODEL: str = "models/gemma-3-27b-it"  # Gemma 3 27B instruction-tuned model
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 8192  # Increased for longer responses
    
    @classmethod
    def load_api_keys(cls) -> List[str]:
        """Load all available Gemini API keys from environment"""
        keys = []
        
        # Add primary key
        if cls.GEMINI_API_KEY:
            keys.append(cls.GEMINI_API_KEY.strip())
        
        # Add numbered keys (GEMINI_API_KEY1, GEMINI_API_KEY2, etc.)
        for i in range(1, 20):  # Check up to 20 keys
            key = os.getenv(f"GEMINI_API_KEY{i}")
            if key and key.strip():  # Check if key exists and is not empty after stripping
                keys.append(key.strip())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keys = []
        for key in keys:
            if key not in seen:
                seen.add(key)
                unique_keys.append(key)
        
        return unique_keys
    
    # Cache Configuration
    CACHE_VERSION: str = "1.0"
    MAX_CACHE_AGE_DAYS: int = 30
    
    # Skill Extraction Configuration
    SKILL_CONFIDENCE_THRESHOLD: float = 0.7
    MAX_SKILLS_PER_JOB: int = 50
    
    # Classification Configuration
    MUST_HAVE_THRESHOLD: float = 0.6  # Appears in >60% of jobs
    NICE_TO_HAVE_THRESHOLD: float = 0.3  # Appears in 30-60% of jobs
    
    # Analysis Configuration
    SEMANTIC_MATCH_THRESHOLD: float = 0.75
    EVIDENCE_MIN_LENGTH: int = 10
    MAX_EVIDENCE_SNIPPETS: int = 5
    
    # Resume Optimization Configuration
    MAX_OPTIMIZATION_ATTEMPTS: int = 3
    FABRICATION_CHECK_ENABLED: bool = True
    
    # Retry Configuration
    MAX_LLM_RETRIES: int = 3
    RETRY_BACKOFF_FACTOR: float = 2.0
    RETRY_INITIAL_DELAY: float = 1.0
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        # Load all available keys
        cls.GEMINI_API_KEYS = cls.load_api_keys()
        
        if not cls.GEMINI_API_KEYS:
            raise ValueError(
                "At least one GEMINI_API_KEY is required. "
                "Please set GEMINI_API_KEY or GEMINI_API_KEY1, GEMINI_API_KEY2, etc. in your .env file. "
                "Get your API keys from: https://makersuite.google.com/app/apikey"
            )
        
        import sys
        print(f"Loaded {len(cls.GEMINI_API_KEYS)} Gemini API key(s) for rotation", file=sys.stderr)
        return True


# Validate configuration on import
try:
    EngineConfig.validate()
except ValueError as e:
    import sys
    print(f"Warning: {e}", file=sys.stderr)
