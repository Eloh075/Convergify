"""
Gemini API Client for Phase 2

Simplified client for JSON generation with retry logic.
"""
import time
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
import json

from config import Phase2Config

logger = logging.getLogger(__name__)


class GeminiClient:
    """Simplified Gemini client for Phase 2"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client"""
        self.api_key = api_key or Phase2Config.GEMINI_API_KEYS[0]
        genai.configure(api_key=self.api_key)
        
        self.model = genai.GenerativeModel(
            Phase2Config.GEMINI_MODEL,
            safety_settings={
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            }
        )
        logger.info(f"Initialized Gemini client with model: {Phase2Config.GEMINI_MODEL}")
    
    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Generate JSON response using Gemini API
        
        Args:
            prompt: The prompt to send to the model
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            retry_count: Current retry attempt
            
        Returns:
            Parsed JSON response
        """
        if retry_count >= Phase2Config.MAX_RETRIES:
            raise Exception(f"Max retries ({Phase2Config.MAX_RETRIES}) exceeded")
        
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            # Check if model is Gemma (doesn't support JSON mode)
            is_gemma = "gemma" in Phase2Config.GEMINI_MODEL.lower()
            
            # Only add JSON mode for Gemini models (not Gemma)
            if not is_gemma:
                generation_config.response_mime_type = "application/json"
            
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
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            logger.error(f"Response preview: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON response from model: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini API error (attempt {retry_count + 1}): {error_msg}")
            
            # Retry with exponential backoff
            if retry_count < Phase2Config.MAX_RETRIES:
                delay = Phase2Config.RETRY_INITIAL_DELAY * (
                    Phase2Config.RETRY_BACKOFF_FACTOR ** retry_count
                )
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                
                return self.generate_json(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    retry_count=retry_count + 1
                )
            else:
                raise
