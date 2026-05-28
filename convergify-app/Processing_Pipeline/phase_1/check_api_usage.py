"""
Check API usage for all Gemini API keys
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Scraper_Automated", ".env")
load_dotenv(env_path)

import google.generativeai as genai

# Load all API keys
keys = []
primary_key = os.getenv("GEMINI_API_KEY")
if primary_key:
    keys.append(("GEMINI_API_KEY", primary_key.strip()))

for i in range(1, 20):
    key = os.getenv(f"GEMINI_API_KEY{i}")
    if key and key.strip():
        keys.append((f"GEMINI_API_KEY{i}", key.strip()))

print("=" * 80)
print(f"Checking API Usage for {len(keys)} Keys")
print("=" * 80)

for key_name, api_key in keys:
    print(f"\n{key_name}:")
    try:
        genai.configure(api_key=api_key)
        
        # Try to make a simple call to check if key works
        model = genai.GenerativeModel("models/gemma-3-12b-it")
        response = model.generate_content("Say 'OK'")
        
        print(f"  ✓ Key is ACTIVE and working")
        print(f"  Response: {response.text[:50]}")
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            print(f"  ⚠️  QUOTA EXCEEDED - Key exhausted")
        elif "403" in error_msg or "API key not valid" in error_msg:
            print(f"  ❌ INVALID KEY")
        else:
            print(f"  ❌ ERROR: {error_msg[:100]}")

print("\n" + "=" * 80)
