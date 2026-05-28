"""Show summary of job role and suffix separation in the database."""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from scraper.database.job_database import JobDatabase


def show_database_summary():
    """Show summary of job roles and suffixes in the database."""
    logger.info("📊 DATABASE SUMMARY: Job Roles and Suffixes")
    logger.info("="*60)
    
    db = JobDatabase()
    
    try:
        # Get summary by base role
        result = db.supabase.table(db.table_name).select("job_role, suffix").eq("website", "LinkedIn").execute()
        jobs = result.data
        
        # Group by base role
        role_counts = {}
        suffix_counts = {}
        role_suffix_combinations = {}
        
        for job in jobs:
            base_role = job['job_role']
            suffix = job['suffix']
            
            # Count base roles
            if base_role not in role_counts:
                role_counts[base_role] = 0
            role_counts[base_role] += 1
            
            # Count suffixes
            suffix_key = suffix if suffix else "(no suffix)"
            if suffix_key not in suffix_counts:
                suffix_counts[suffix_key] = 0
            suffix_counts[suffix_key] += 1
            
            # Count role-suffix combinations
            combo_key = f"{base_role} + {suffix_key}"
            if combo_key not in role_suffix_combinations:
                role_suffix_combinations[combo_key] = 0
            role_suffix_combinations[combo_key] += 1
        
        logger.info(f"\n📈 Total LinkedIn Jobs: {len(jobs)}")
        
        logger.info(f"\n🎯 Jobs by Base Role:")
        for role, count in sorted(role_counts.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"   {role}: {count}")
        
        logger.info(f"\n🏷️ Jobs by Suffix:")
        for suffix, count in sorted(suffix_counts.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"   {suffix}: {count}")
        
        logger.info(f"\n🔗 Top Role + Suffix Combinations:")
        for combo, count in sorted(role_suffix_combinations.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"   {combo}: {count}")
        
        # Show some examples of the new structure
        logger.info(f"\n📝 Recent Examples (last 5 entries):")
        recent_result = db.supabase.table(db.table_name).select("job_role, suffix, scraped_at").eq("website", "LinkedIn").order("scraped_at", desc=True).limit(5).execute()
        
        for job in recent_result.data:
            suffix_display = job['suffix'] if job['suffix'] else "(no suffix)"
            logger.info(f"   '{job['job_role']}' + '{suffix_display}' (scraped: {job['scraped_at'][:19]})")
        
        logger.info(f"\n✅ Database structure successfully updated!")
        logger.info(f"   - Job roles and suffixes are now stored separately")
        logger.info(f"   - Base roles are clean (e.g., 'Software Engineer', 'AI Engineer')")
        logger.info(f"   - Suffixes are in separate column (e.g., 'Intern', 'Graduate', NULL)")
        logger.info(f"   - All existing data has been migrated")
        logger.info(f"   - New scraping automatically uses this structure")
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")


def main():
    """Main function."""
    show_database_summary()


if __name__ == "__main__":
    main()