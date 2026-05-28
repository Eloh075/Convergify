"""List all available Gemini models"""
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Available Gemini models:")
print()

try:
    models = genai.list_models()
    for model in models:
        # Check if it supports generateContent
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            print(f"   Display name: {model.display_name}")
            print(f"   Description: {model.description[:100] if model.description else 'N/A'}")
            print()
except Exception as e:
    print(f"Error listing models: {e}")
