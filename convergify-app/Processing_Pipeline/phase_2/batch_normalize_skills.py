"""
Batch Normalize Skills

Main orchestrator for Phase 2 skill normalization and classification.
"""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Scraper_Automated", ".env")
load_dotenv(env_path)

from supabase import create_client
from config import Phase2Config
from gemini_client import GeminiClient
from skill_normalizer import SkillNormalizer
from skill_classifier import SkillClassifier
import time


def create_tables(supabase):
    """Create Phase 2 tables if they don't exist"""
    print("\n" + "=" * 80)
    print("CREATING PHASE 2 TABLES")
    print("=" * 80)
    
    # Read SQL file
    sql_file = os.path.join(os.path.dirname(__file__), "create_phase2_tables.sql")
    with open(sql_file, 'r') as f:
        sql = f.read()
    
    # Execute SQL (note: Supabase Python client doesn't support raw SQL execution)
    # You'll need to run this manually in Supabase SQL editor or use psycopg2
    print("\n⚠️  Please run create_phase2_tables.sql in Supabase SQL editor")
    print("   File location: Processing_Pipeline/phase_2/create_phase2_tables.sql")
    
    input("\nPress Enter after running the SQL script...")


def get_job_roles(supabase):
    """Get all job roles"""
    result = supabase.table("job_classifications").select("job_role").execute()
    roles = sorted(set([r['job_role'] for r in result.data]))
    return roles


def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print("PHASE 2: SKILL NORMALIZATION & CLASSIFICATION")
    print("=" * 80)
    
    # Validate config
    Phase2Config.validate()
    
    # Connect to database
    supabase = create_client(
        Phase2Config.SUPABASE_URL,
        Phase2Config.SUPABASE_KEY
    )
    
    # Initialize clients
    gemini = GeminiClient()
    normalizer = SkillNormalizer(supabase, gemini)
    classifier = SkillClassifier(supabase, gemini)
    
    # Create tables (if needed)
    # create_tables(supabase)
    
    # Get job roles
    job_roles = get_job_roles(supabase)
    print(f"\nJob roles to process: {len(job_roles)}")
    for role in job_roles:
        print(f"  - {role}")
    
    # Check for command-line argument
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "all":
            print("\nBatch mode: Processing all roles")
        elif mode == "test":
            job_roles = [job_roles[0]]
            print(f"\nTest mode: Processing only {job_roles[0]}")
        else:
            # Specific role
            if mode in job_roles:
                job_roles = [mode]
                print(f"\nProcessing specific role: {mode}")
            else:
                print(f"\n✗ Error: Role '{mode}' not found")
                return
    else:
        # Interactive mode
        print("\nOptions:")
        print("  1. Process all roles")
        print("  2. Process specific role")
        print("  3. Test on one role first")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "2":
            print("\nAvailable roles:")
            for i, role in enumerate(job_roles, 1):
                print(f"  {i}. {role}")
            role_idx = int(input("\nEnter role number: ").strip()) - 1
            job_roles = [job_roles[role_idx]]
        elif choice == "3":
            job_roles = [job_roles[0]]  # First role only
            print(f"\nTest mode: Processing only {job_roles[0]}")
    
    # Track results
    results = {
        "normalization": [],
        "classification": []
    }
    
    start_time = time.time()
    
    # Process each role
    for i, job_role in enumerate(job_roles, 1):
        print(f"\n{'='*80}")
        print(f"PROCESSING ROLE {i}/{len(job_roles)}: {job_role}")
        print(f"{'='*80}")
        
        try:
            # Step 1: Normalization
            norm_result = normalizer.normalize_all(job_role)
            results["normalization"].append({
                "job_role": job_role,
                **norm_result
            })
            
            # Step 2: Classification
            class_result = classifier.classify_for_role(job_role)
            results["classification"].append(class_result)
            
        except Exception as e:
            print(f"\n✗ Error processing {job_role}: {e}")
            import traceback
            traceback.print_exc()
            print(f"\nContinuing with next role...")
            continue
    
    # Print final summary
    elapsed_time = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"PHASE 2 COMPLETE")
    print(f"{'='*80}")
    print(f"Time elapsed: {elapsed_time/60:.1f} minutes")
    
    print(f"\nNormalization Summary:")
    total_skills = sum(r['total_skills'] for r in results['normalization'])
    total_chunks = sum(r['chunks_processed'] for r in results['normalization'])
    total_canonical = sum(r['new_canonical'] for r in results['normalization'])
    total_aliases = sum(r['new_aliases'] for r in results['normalization'])
    
    print(f"  Total skills processed: {total_skills}")
    print(f"  Total chunks: {total_chunks}")
    print(f"  New canonical skills: {total_canonical}")
    print(f"  New aliases: {total_aliases}")
    
    print(f"\nClassification Summary:")
    total_classified = sum(r['skills_classified'] for r in results['classification'])
    print(f"  Total skills classified: {total_classified}")
    
    print(f"\nRoles processed: {len(job_roles)}")
    for role in job_roles:
        print(f"  ✓ {role}")
    
    print(f"\n{'='*80}")
    print("Next steps:")
    print("  1. Run frequency calculation (Step 3)")
    print("  2. Run importance assignment (Step 4)")
    print("  3. Validate results")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
