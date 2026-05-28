"""
Configuration for Phase 2 - Skills Normalization
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Phase2Config:
    """Configuration for Phase 2 processing"""
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Gemini API Configuration
    GEMINI_API_KEYS = []
    GEMINI_MODEL = "models/gemma-3-12b-it"  # Same as Phase 1
    
    @classmethod
    def load_api_keys(cls):
        """Load all available Gemini API keys from environment"""
        keys = []
        
        # Add primary key
        primary_key = os.getenv("GEMINI_API_KEY")
        if primary_key:
            keys.append(primary_key.strip())
        
        # Add numbered keys (GEMINI_API_KEY1, GEMINI_API_KEY2, etc.)
        for i in range(1, 20):
            key = os.getenv(f"GEMINI_API_KEY{i}")
            if key and key.strip():
                keys.append(key.strip())
        
        # Remove duplicates
        return list(set(keys))
    
    # Chunking Configuration
    CHUNK_SIZE = 75  # Optimal for complete LLM responses (50-100 range)
    
    # Retry Configuration
    MAX_RETRIES = 3
    RETRY_INITIAL_DELAY = 2  # seconds
    RETRY_BACKOFF_FACTOR = 2  # exponential backoff
    
    # Context Configuration
    MIN_JOBS_PER_CONTEXT = 3  # Only process contexts with 3+ jobs
    
    # Importance Thresholds
    MUST_HAVE_THRESHOLD = 0.6  # >60% of jobs
    NICE_TO_HAVE_THRESHOLD = 0.3  # 30-60% of jobs
    # <30% = Preferred
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        cls.GEMINI_API_KEYS = cls.load_api_keys()
        
        if not cls.SUPABASE_URL:
            raise ValueError("SUPABASE_URL not set in environment")
        if not cls.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY not set in environment")
        if not cls.GEMINI_API_KEYS:
            raise ValueError("GEMINI_API_KEYS not set in environment")
        
        print("✓ Configuration validated")
        print(f"  Supabase URL: {cls.SUPABASE_URL[:30]}...")
        print(f"  API Keys: {len(cls.GEMINI_API_KEYS)} keys")
        print(f"  Model: {cls.GEMINI_MODEL}")
        print(f"  Chunk Size: {cls.CHUNK_SIZE}")
