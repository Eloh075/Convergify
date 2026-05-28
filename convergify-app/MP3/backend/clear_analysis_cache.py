#!/usr/bin/env python3
"""
Clear analysis cache to force fresh analysis

This script clears:
1. Analysis results from database
2. Classified skills cache on jobs
3. Any other cached analysis data

Run this after fixing bugs to ensure you're seeing fresh results.
"""
import sys
from database import SessionLocal
from models.analysis import Analysis
from models.job import Job
from sqlalchemy import update

def clear_analysis_cache():
    """Clear all analysis cache"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("CLEARING ANALYSIS CACHE")
        print("=" * 80)
        
        # Count existing data
        analysis_count = db.query(Analysis).count()
        jobs_with_cache = db.query(Job).filter(Job.classified_skills.isnot(None)).count()
        
        print(f"\nCurrent State:")
        print(f"  Analysis records: {analysis_count}")
        print(f"  Jobs with cached skills: {jobs_with_cache}")
        
        # Clear analysis results
        print(f"\nClearing analysis results...")
        deleted_analyses = db.query(Analysis).delete()
        print(f"  Deleted {deleted_analyses} analysis records")
        
        # Clear classified skills cache on jobs
        print(f"\nClearing classified skills cache on jobs...")
        db.execute(
            update(Job).values(
                classified_skills=None,
                classification_date=None,
                classification_version=None
            )
        )
        print(f"  Cleared classified skills cache")
        
        # Commit changes
        db.commit()
        
        print(f"\n" + "=" * 80)
        print("CACHE CLEARED SUCCESSFULLY")
        print("=" * 80)
        print(f"\nYou can now run a fresh analysis and see correct results!")
        print(f"\nNext steps:")
        print(f"  1. Go to Analysis Lab in the UI")
        print(f"  2. Select resume and jobs")
        print(f"  3. Click 'Generate Analysis'")
        print(f"  4. Check that market demand values are varied (not all 10%)")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error clearing cache: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(clear_analysis_cache())
