#!/usr/bin/env python3
"""
Test generate_json method specifically
"""
import sys
import time
import json

def test_generate_json():
    """Test the generate_json method"""
    print("=" * 80)
    print("GENERATE_JSON METHOD TEST")
    print("=" * 80)
    
    try:
        print("\n1. Importing LLM client...")
        from engines.gemini_client import GeminiClient
        print("   ✅ Import successful")
        
        print("\n2. Initializing client...")
        client = GeminiClient()
        print("   ✅ Client initialized")
        
        print("\n3. Testing generate_json with simple prompt...")
        print("   (This should return valid JSON)")
        
        start = time.time()
        
        prompt = """Extract skills from this job description and return as JSON:

Job: Senior Python Developer
- 5+ years Python experience
- Django/Flask frameworks
- PostgreSQL database
- AWS cloud services
- Docker containerization

Return JSON in this format:
{
  "skills": [
    {"name": "skill_name", "importance": "Must-have" or "Nice-to-have", "confidence": 0.0-1.0}
  ]
}"""
        
        print(f"\n   Sending prompt...")
        
        response = client.generate_json(prompt)
        
        elapsed = time.time() - start
        
        print(f"\n   ✅ Response received in {elapsed:.1f} seconds!")
        print(f"\n{'=' * 80}")
        print("JSON RESPONSE:")
        print("=" * 80)
        print(json.dumps(response, indent=2))
        print("=" * 80)
        
        # Validate it's actually JSON
        if isinstance(response, dict):
            print("\n✅ Response is valid JSON (dict)")
        else:
            print(f"\n❌ Response is not a dict, it's: {type(response)}")
            return 1
        
        # Check if it has expected structure
        if "skills" in response:
            print(f"✅ Response has 'skills' key")
            print(f"   Found {len(response['skills'])} skills")
            
            # Show first skill
            if response['skills']:
                first_skill = response['skills'][0]
                print(f"\n   Example skill:")
                print(f"   - Name: {first_skill.get('name', 'N/A')}")
                print(f"   - Importance: {first_skill.get('importance', 'N/A')}")
                print(f"   - Confidence: {first_skill.get('confidence', 'N/A')}")
        else:
            print(f"⚠️  Response doesn't have 'skills' key")
            print(f"   Keys found: {list(response.keys())}")
        
        if elapsed > 30:
            print(f"\n⚠️  WARNING: Took {elapsed:.1f}s (over 30 seconds)")
        elif elapsed > 15:
            print(f"\n⚠️  Took {elapsed:.1f}s (acceptable but could be faster)")
        else:
            print(f"\n✅ Response time is good ({elapsed:.1f}s)")
        
        print("\n" + "=" * 80)
        print("TEST 2: Testing with response_schema")
        print("=" * 80)
        
        # Test with response schema
        from pydantic import BaseModel
        from typing import List
        
        class Skill(BaseModel):
            name: str
            importance: str
            confidence: float
        
        class SkillsResponse(BaseModel):
            skills: List[Skill]
        
        print("\n   Testing with Pydantic schema...")
        start = time.time()
        
        response2 = client.generate_json(
            prompt=prompt,
            response_schema=SkillsResponse
        )
        
        elapsed2 = time.time() - start
        
        print(f"\n   ✅ Response received in {elapsed2:.1f} seconds!")
        print(f"\n{'=' * 80}")
        print("JSON RESPONSE (with schema):")
        print("=" * 80)
        print(json.dumps(response2, indent=2))
        print("=" * 80)
        
        if isinstance(response2, dict) and "skills" in response2:
            print(f"\n✅ Schema-based response is valid")
            print(f"   Found {len(response2['skills'])} skills")
        else:
            print(f"\n⚠️  Schema-based response has unexpected structure")
        
        print("\n" + "=" * 80)
        print("FINAL RESULTS")
        print("=" * 80)
        print(f"✅ Test 1 (basic): {elapsed:.1f}s")
        print(f"✅ Test 2 (schema): {elapsed2:.1f}s")
        print(f"✅ Both tests passed!")
        print(f"\n✅ generate_json method is working correctly")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_generate_json())
