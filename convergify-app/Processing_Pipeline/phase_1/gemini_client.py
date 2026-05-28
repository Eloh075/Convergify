"""
Gemini API Client Wrapper

Provides a unified interface for interacting with Google's Gemini API
with automatic API key rotation, retry logic, and error handling.
"""
import time
import logging
from typing import Optional, Dict, Any, List
import google.generativeai as genai

from .config import PipelineConfig

logger = logging.getLogger(__name__)


class GeminiClient:
    """Wrapper for Gemini API with automatic key rotation and retry logic"""
    
    # Class-level tracking of failed keys
    _failed_keys: set = set()
    _current_key_index: int = 0
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client with automatic key rotation
        
        Args:
            api_key: Specific API key to use (optional, will use rotation if not provided)
        """
        # Get all available keys
        self.available_keys = PipelineConfig.GEMINI_API_KEYS.copy()
        
        if not self.available_keys:
            raise ValueError("No Gemini API keys available")
        
        # If specific key provided, use it
        if api_key:
            self.api_key = api_key
            self.use_rotation = False
        else:
            # Use rotation - start with first available key
            self.api_key = self._get_next_working_key()
            self.use_rotation = True
        
        self._configure_client()
        logger.info(f"Initialized Gemini client with model: {PipelineConfig.GEMINI_MODEL}")
        if self.use_rotation:
            logger.info(f"API key rotation enabled with {len(self.available_keys)} key(s)")
    
    def _configure_client(self):
        """Configure the Gemini client with current API key"""
        genai.configure(api_key=self.api_key)
        
        # Initialize model with safety settings for better compatibility
        self.model = genai.GenerativeModel(
            PipelineConfig.GEMINI_MODEL,
            safety_settings={
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            }
        )
    
    def _get_next_working_key(self) -> str:
        """Get the next working API key from rotation"""
        # Filter out failed keys
        working_keys = [k for k in self.available_keys if k not in self._failed_keys]
        
        if not working_keys:
            # All keys failed, reset and try again
            logger.warning("All API keys failed, resetting failure tracking")
            self._failed_keys.clear()
            working_keys = self.available_keys.copy()
        
        # Get next key in rotation
        key = working_keys[self._current_key_index % len(working_keys)]
        self._current_key_index = (self._current_key_index + 1) % len(working_keys)
        
        return key
    
    def _rotate_key(self) -> bool:
        """
        Rotate to next API key
        
        Returns:
            True if rotation successful, False if no more keys available
        """
        if not self.use_rotation:
            return False
        
        # Mark current key as failed
        self._failed_keys.add(self.api_key)
        logger.warning(f"Marking API key as failed (quota exceeded or error)")
        
        # Try to get next working key
        try:
            old_key = self.api_key
            self.api_key = self._get_next_working_key()
            
            if self.api_key == old_key:
                # No other keys available
                logger.error("No more API keys available for rotation")
                return False
            
            # Reconfigure with new key
            self._configure_client()
            logger.info(f"Rotated to next API key ({len(self._failed_keys)} failed so far)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate API key: {e}")
            return False
        
    def generate_text(
        self, 
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        retry_count: int = 0
    ) -> str:
        """
        Generate text using Gemini API with automatic key rotation and retry logic
        
        Args:
            prompt: The prompt to send to the model
            temperature: Sampling temperature (defaults to config)
            max_tokens: Maximum tokens to generate (defaults to config)
            retry_count: Current retry attempt (internal use)
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If all retries and key rotations fail
        """
        temperature = temperature or PipelineConfig.GEMINI_TEMPERATURE
        max_tokens = max_tokens or PipelineConfig.GEMINI_MAX_TOKENS
        
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini API error (attempt {retry_count + 1}): {error_msg}")
            
            # Check if it's a quota error (429 or quota exceeded message)
            is_quota_error = (
                "429" in error_msg or 
                "quota" in error_msg.lower() or
                "rate limit" in error_msg.lower()
            )
            
            # If quota error and rotation enabled, try rotating key
            if is_quota_error and self.use_rotation and retry_count == 0:
                logger.info("Quota exceeded, attempting to rotate API key...")
                if self._rotate_key():
                    logger.info("Successfully rotated to new API key, retrying...")
                    # Retry immediately with new key (don't count as retry)
                    return self.generate_text(
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        retry_count=0  # Reset retry count for new key
                    )
            
            # Retry with exponential backoff
            if retry_count < PipelineConfig.MAX_RETRIES:
                delay = PipelineConfig.RETRY_INITIAL_DELAY * (
                    PipelineConfig.RETRY_BACKOFF_FACTOR ** retry_count
                )
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                
                return self.generate_text(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    retry_count=retry_count + 1
                )
            else:
                logger.error(f"All {PipelineConfig.MAX_RETRIES} retries failed")
                raise
    
    def generate_json(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_schema: Optional[Any] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Generate JSON response using Gemini/Gemma API with structured output
        
        For Gemma models: Uses response_schema only (no JSON mode)
        For Gemini models: Uses both JSON mode and response_schema
        
        Args:
            prompt: The prompt to send to the model
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_schema: Pydantic model for structured output
            retry_count: Current retry attempt (internal use)
            
        Returns:
            Parsed JSON response
            
        Raises:
            ValueError: If response is not valid JSON
        """
        import json
        
        # Prevent infinite recursion
        MAX_RETRIES = len(self.available_keys) if self.use_rotation else 3
        if retry_count >= MAX_RETRIES:
            raise Exception(f"Max retries ({MAX_RETRIES}) exceeded for generate_json")
        
        temperature = temperature or PipelineConfig.GEMINI_TEMPERATURE
        max_tokens = max_tokens or PipelineConfig.GEMINI_MAX_TOKENS
        
        # Check if model is Gemma (doesn't support JSON mode)
        is_gemma = "gemma" in PipelineConfig.GEMINI_MODEL.lower()
        
        try:
            # Build generation config
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            # Only add JSON mode for Gemini models (not Gemma)
            if not is_gemma:
                generation_config.response_mime_type = "application/json"
            
            # Add response_schema if provided (works with both Gemini and Gemma)
            if response_schema:
                generation_config.response_schema = response_schema
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            response_text = response.text.strip()
            
            # For Gemma models, remove markdown code blocks if present
            if is_gemma:
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse the JSON response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                # If JSON is truncated, try to salvage what we can
                logger.error(f"JSON parse error at position {e.pos}: {str(e)}")
                logger.error(f"Response text length: {len(response_text)}")
                logger.error(f"Response preview: {response_text[:500]}...")
                logger.error(f"Response end: ...{response_text[-500:]}")
                
                # Check if response was truncated
                if len(response_text) > 20000:
                    raise ValueError(
                        f"Response too large ({len(response_text)} chars) and truncated. "
                        f"Consider reducing prompt size or processing in smaller chunks."
                    )
                else:
                    raise ValueError(f"Invalid JSON response from model: {str(e)}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response.text[:200]}")
            raise ValueError(f"Invalid JSON response from model: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini API error: {error_msg}")
            
            # Check if it's a quota error and try rotation
            is_quota_error = (
                "429" in error_msg or 
                "quota" in error_msg.lower() or
                "rate limit" in error_msg.lower()
            )
            
            if is_quota_error and self.use_rotation:
                logger.info("Quota exceeded, attempting to rotate API key...")
                if self._rotate_key():
                    logger.info("Successfully rotated to new API key, retrying...")
                    return self.generate_json(
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        response_schema=response_schema,
                        retry_count=retry_count + 1
                    )
            
            raise
