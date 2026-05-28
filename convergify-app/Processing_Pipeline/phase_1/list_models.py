"""
Quick script to list all available Gemini models
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Scraper_Automated", ".env")
load_dotenv(env_path)

import google.generativeai as genai

# Configure with API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ No GEMINI_API_KEY found in .env")
    sys.exit(1)

genai.configure(api_key=api_key)

print("=" * 80)
print("Available Gemini Models")
print("=" * 80)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\n✓ {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")
        print(f"  Input Token Limit: {model.input_token_limit}")
        print(f"  Output Token Limit: {model.output_token_limit}")

print("\n" + "=" * 80)
