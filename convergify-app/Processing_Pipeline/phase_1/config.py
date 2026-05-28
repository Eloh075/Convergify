"""
Configuration for Skills Processing Pipeline
Adapted from MP3/backend/engines/config.py
"""
import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class PipelineConfig:
    """Configuration for skills processing pipeline"""
    
    # Gemini API Configuration - Multiple keys for rotation
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_API_KEYS: List[str] = []  # Will be populated from env
    GEMINI_MODEL: str = "models/gemma-3-12b-it"  # Gemma 3 12B - good balance for high velocity
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 8192
    
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
            if key and key.strip():
                keys.append(key.strip())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keys = []
        for key in keys:
            if key not in seen:
                seen.add(key)
                unique_keys.append(key)
        
        return unique_keys
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Processing Configuration
    BATCH_SIZE: int = 50  # Jobs to process per batch
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_FACTOR: float = 2.0
    RETRY_INITIAL_DELAY: float = 1.0
    
    # Skill Extraction Configuration
    SKILL_CONFIDENCE_THRESHOLD: float = 0.7
    MAX_SKILLS_PER_JOB: int = 50
    
    # Classification Configuration
    MUST_HAVE_THRESHOLD: float = 0.6  # Appears in >60% of jobs
    NICE_TO_HAVE_THRESHOLD: float = 0.3  # Appears in 30-60% of jobs
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        # Load all available keys
        cls.GEMINI_API_KEYS = cls.load_api_keys()
        
        if not cls.GEMINI_API_KEYS:
            raise ValueError(
                "At least one GEMINI_API_KEY is required. "
                "Please set GEMINI_API_KEY or GEMINI_API_KEY1, GEMINI_API_KEY2, etc. in your .env file."
            )
        
        if not cls.SUPABASE_URL or not cls.SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY are required in .env file"
            )
        
        print(f"✓ Loaded {len(cls.GEMINI_API_KEYS)} Gemini API key(s) for rotation")
        print(f"✓ Supabase connection configured")
        return True


# Validate configuration on import
try:
    PipelineConfig.validate()
except ValueError as e:
    import sys
    print(f"Warning: {e}", file=sys.stderr)
