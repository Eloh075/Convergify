"""
Test Setup for Phase 2

Validates configuration, database connection, and basic functionality
before running full batch processing.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Scraper_Automated", ".env")
load_dotenv(env_path)

from supabase import create_client
from config import Phase2Config
from taxonomy import SkillTaxonomy
from gemini_client import GeminiClient
import json


def test_config():
    """Test configuration"""
    print("\n" + "=" * 80)
    print("TEST 1: Configuration")
    print("=" * 80)
    
    try:
        Phase2Config.validate()
        print("✅ Configuration valid")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_database_connection():
    """Test database connection"""
    print("\n" + "=" * 80)
    print("TEST 2: Database Connection")
    print("=" * 80)
    
    try:
        supabase = create_client(
            Phase2Config.SUPABASE_URL,
            Phase2Config.SUPABASE_KEY
        )
        
        # Test query
        result = supabase.table("job_skills").select("skill_name").limit(5).execute()
        print(f"✅ Database connected")
        print(f"   Sample skills: {[r['skill_name'] for r in result.data]}")
        return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


def test_taxonomy():
    """Test taxonomy"""
    print("\n" + "=" * 80)
    print("TEST 3: Taxonomy")
    print("=" * 80)
    
    try:
        taxonomy = SkillTaxonomy()
        
        # Test that taxonomy provides category structure
        print("  Taxonomy provides 24 tier2 categories for LLM classification")
        print(f"  Tier1 categories: {len(taxonomy.get_all_tier1_categories())}")
        
        tier2_count = 0
        for tier1 in taxonomy.get_all_tier1_categories():
            tier2_count += len(taxonomy.get_tier2_categories(tier1))
        print(f"  Tier2 categories: {tier2_count}")
        
        # Test keyword-based fallback classification
        print("\n  Testing keyword-based fallback classification:")
        test_skills = ["Python", "React", "Leadership", "AWS", "Unknown Skill"]
        for skill in test_skills:
            tier1, tier2 = taxonomy.classify_skill(skill)
            print(f"    {skill:20} → {tier1:15} / {tier2}")
        
        print("\n✅ Taxonomy working")
        print("   Note: LLM will use these categories to classify skills in Step 4")
        return True
    except Exception as e:
        print(f"❌ Taxonomy error: {e}")
        return False


def test_gemini_client():
    """Test Gemini client"""
    print("\n" + "=" * 80)
    print("TEST 4: Gemini Client")
    print("=" * 80)
    
    try:
        client = GeminiClient()
        
        # Test simple JSON generation
        prompt = """Return a JSON object with exactly 3 skill mappings:
{
  "python programming": "Python",
  "reactjs": "React",
  "leadership skills": "Leadership"
}

Return ONLY the JSON, no other text."""
        
        response = client.generate_json(prompt)
        print(f"✅ Gemini client working")
        print(f"   Response: {json.dumps(response, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Gemini client error: {e}")
        return False


def test_database_schema():
    """Test if required tables exist"""
    print("\n" + "=" * 80)
    print("TEST 5: Database Schema")
    print("=" * 80)
    
    try:
        supabase = create_client(
            Phase2Config.SUPABASE_URL,
            Phase2Config.SUPABASE_KEY
        )
        
        # Check required tables
        required_tables = [
            "job_skills",
            "job_classifications"
        ]
        
        for table in required_tables:
            result = supabase.table(table).select("*").limit(1).execute()
            print(f"  ✓ Table '{table}' exists")
        
        print("✅ Database schema valid")
        print("\n⚠️  Note: Phase 2 tables (canonical_skills, skill_aliases, etc.) will be created during first run")
        return True
    except Exception as e:
        print(f"❌ Database schema error: {e}")
        return False


def test_sample_data():
    """Test sample data availability"""
    print("\n" + "=" * 80)
    print("TEST 6: Sample Data")
    print("=" * 80)
    
    try:
        supabase = create_client(
            Phase2Config.SUPABASE_URL,
            Phase2Config.SUPABASE_KEY
        )
        
        # Count total skills
        result = supabase.table("job_skills").select("skill_name", count="exact").execute()
        total_skills = result.count
        print(f"  Total skills in database: {total_skills:,}")
        
        # Count unique skills
        result = supabase.table("job_skills").select("skill_name").execute()
        unique_skills = len(set([r['skill_name'] for r in result.data]))
        print(f"  Unique skill names: {unique_skills:,}")
        
        # Count job roles
        result = supabase.table("job_classifications").select("job_role").execute()
        unique_roles = len(set([r['job_role'] for r in result.data]))
        print(f"  Unique job roles: {unique_roles}")
        
        print("✅ Sample data available")
        return True
    except Exception as e:
        print(f"❌ Sample data error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("PHASE 2 SETUP VALIDATION")
    print("=" * 80)
    
    tests = [
        ("Configuration", test_config),
        ("Database Connection", test_database_connection),
        ("Taxonomy", test_taxonomy),
        ("Gemini Client", test_gemini_client),
        ("Database Schema", test_database_schema),
        ("Sample Data", test_sample_data)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Ready to run Phase 2 batch processing.")
    else:
        print("\n❌ Some tests failed. Please fix issues before running batch processing.")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
