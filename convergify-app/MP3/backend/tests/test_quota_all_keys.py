#!/usr/bin/env python3
"""
Test quota for all API keys with Gemini 2.5 models
"""
import sys
import google.generativeai as genai
from engines.config import EngineConfig

def test_key_quota(api_key, model_name):
    """Test if a key has quota for a specific model"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        # Try a minimal generation to test quota
        response = model.generate_content(
            "Say OK",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=5
            )
        )
        
        result = response.text.strip()
        return True, "OK"
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return False, "QUOTA_EXCEEDED"
        elif "404" in error_msg or "not found" in error_msg.lower():
            return False, "MODEL_NOT_FOUND"
        else:
            return False, f"ERROR: {error_msg[:100]}"

def main():
    print("=" * 80)
    print("CHECKING QUOTA FOR ALL KEYS - GEMINI 2.5 MODELS")
    print("=" * 80)
    
    # Load API keys
    EngineConfig.validate()
    api_keys = EngineConfig.GEMINI_API_KEYS
    
    print(f"\nFound {len(api_keys)} API key(s)")
    
    # Models to test (Gemini 2.5 variants)
    models_to_test = [
        ("models/gemini-2.5-flash", "Gemini 2.5 Flash (65K output)"),
        ("models/gemini-2.5-pro", "Gemini 2.5 Pro (65K output)"),
        ("models/gemini-2.5-flash-lite", "Gemini 2.5 Flash Lite (65K output)"),
    ]
    
    results = {}
    
    for model_name, description in models_to_test:
        print(f"\n{'='*80}")
        print(f"{description}")
        print(f"Model: {model_name}")
        print("=" * 80)
        
        results[model_name] = []
        
        for i, api_key in enumerate(api_keys, 1):
            key_preview = f"{api_key[:10]}...{api_key[-4:]}"
            
            success, result = test_key_quota(api_key, model_name)
            
            if success:
                print(f"  ✅ Key {i} ({key_preview}): HAS QUOTA")
                results[model_name].append((i, key_preview, "AVAILABLE"))
            else:
                status = result
                if status == "QUOTA_EXCEEDED":
                    print(f"  ❌ Key {i} ({key_preview}): QUOTA EXCEEDED")
                    results[model_name].append((i, key_preview, "QUOTA_EXCEEDED"))
                elif status == "MODEL_NOT_FOUND":
                    print(f"  ⚠️  Key {i} ({key_preview}): MODEL NOT FOUND")
                    results[model_name].append((i, key_preview, "NOT_FOUND"))
                    break  # No point checking other keys if model doesn't exist
                else:
                    print(f"  ❌ Key {i} ({key_preview}): {status}")
                    results[model_name].append((i, key_preview, "ERROR"))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY - KEYS WITH AVAILABLE QUOTA")
    print("=" * 80)
    
    available_found = False
    
    for model_name, description in models_to_test:
        available_keys = [r for r in results.get(model_name, []) if r[2] == "AVAILABLE"]
        
        if available_keys:
            available_found = True
            print(f"\n✅ {description}")
            print(f"   Model: {model_name}")
            print(f"   Available keys: {len(available_keys)}")
            for key_num, key_preview, _ in available_keys:
                print(f"     - Key #{key_num} ({key_preview})")
    
    if not available_found:
        print("\n❌ NO KEYS WITH AVAILABLE QUOTA FOUND!")
        print("\nAll Gemini 2.5 models have exhausted quota.")
        print("\nOptions:")
        print("  1. Wait for quota to reset (usually 24 hours)")
        print("  2. Use Gemini 2.0 models (8K output)")
        print("  3. Use Gemma 3 models (8K output)")
        print("  4. Upgrade to paid tier for higher quota")
        
        # Check Gemini 2.0 as fallback
        print("\n" + "=" * 80)
        print("CHECKING GEMINI 2.0 MODELS AS FALLBACK")
        print("=" * 80)
        
        fallback_models = [
            ("models/gemini-2.0-flash", "Gemini 2.0 Flash (8K output)"),
        ]
        
        for model_name, description in fallback_models:
            print(f"\n{description}")
            print(f"Model: {model_name}")
            print("-" * 80)
            
            for i, api_key in enumerate(api_keys, 1):
                key_preview = f"{api_key[:10]}...{api_key[-4:]}"
                success, result = test_key_quota(api_key, model_name)
                
                if success:
                    print(f"  ✅ Key {i} ({key_preview}): HAS QUOTA")
                    break
                else:
                    print(f"  ❌ Key {i} ({key_preview}): {result}")
    
    return 0 if available_found else 1

if __name__ == "__main__":
    sys.exit(main())
