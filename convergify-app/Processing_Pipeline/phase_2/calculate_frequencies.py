"""
Calculate Skill Frequencies

Pure math calculations for skill frequencies and importance per 4D context.
No LLM needed.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Scraper_Automated", ".env")
load_dotenv(env_path)

from supabase import create_client
from config import Phase2Config


def calculate_frequencies_for_context(supabase, context):
    """Calculate frequencies for a specific 4D context"""
    
    job_role = context['job_role']
    role_sub_cluster = context['role_sub_cluster']
    experience_level = context['experience_level']
    cluster_type = context['cluster_type']
    total_jobs = context['total_jobs']
    
    # Get all job URLs for this context
    query = supabase.table("job_classifications").select("url").eq(
        "job_role", job_role
    ).eq("experience_level", experience_level).eq("cluster_type", cluster_type)
    
    if role_sub_cluster:
        query = query.eq("role_sub_cluster", role_sub_cluster)
    else:
        query = query.is_("role_sub_cluster", "null")
    
    job_urls = [r['url'] for r in query.execute().data]
    
    # Get skills for these jobs
    skills_result = supabase.table("job_skills").select(
        "canonical_skill_id, canonical_name, url"
    ).in_("url", job_urls).not_.is_("canonical_name", "null").execute()
    
    # Count unique jobs per skill
    skill_jobs = {}
    for row in skills_result.data:
        skill_id = row['canonical_skill_id']
        skill_name = row['canonical_name']
        url = row['url']
        
        if skill_id not in skill_jobs:
            skill_jobs[skill_id] = {
                'canonical_name': skill_name,
                'urls': set()
            }
        skill_jobs[skill_id]['urls'].add(url)
    
    # Calculate normalized frequency and importance
    frequencies = []
    for skill_id, data in skill_jobs.items():
        unique_jobs = len(data['urls'])
        normalized_freq = unique_jobs / total_jobs
        
        # Check if insufficient data
        if context.get('insufficient_data', False):
            importance = "Insufficient Data"
        else:
            # Assign importance based on frequency
            if normalized_freq > 0.6:
                importance = "Must-have"
            elif normalized_freq >= 0.3:
                importance = "Nice-to-have"
            else:
                importance = "Preferred"
        
        frequencies.append({
            'canonical_skill_id': skill_id,
            'job_role': job_role,
            'role_sub_cluster': role_sub_cluster,
            'experience_level': experience_level,
            'cluster_type': cluster_type,
            'raw_frequency': unique_jobs,
            'normalized_frequency': normalized_freq,
            'unique_jobs': unique_jobs,
            'total_jobs_in_context': total_jobs,
            'importance': importance
        })
    
    return frequencies


def save_frequencies(supabase, frequencies):
    """Save frequencies to skill_market_frequencies table"""
    
    if not frequencies:
        return
    
    # Batch upsert
    supabase.table("skill_market_frequencies").upsert(
        frequencies,
        on_conflict="canonical_skill_id,job_role,role_sub_cluster,experience_level,cluster_type"
    ).execute()


def main():
    print("\n" + "=" * 80)
    print("CALCULATING SKILL FREQUENCIES")
    print("=" * 80)
    
    # Connect
    supabase = create_client(Phase2Config.SUPABASE_URL, Phase2Config.SUPABASE_KEY)
    
    # Get all 4D contexts with at least 3 jobs
    print("\nGetting 4D contexts...")
    
    # Query for contexts
    result = supabase.table("job_classifications").select(
        "job_role, role_sub_cluster, experience_level, cluster_type"
    ).execute()
    
    # Group by 4D context and count
    context_counts = {}
    for row in result.data:
        key = (
            row['job_role'],
            row['role_sub_cluster'],
            row['experience_level'],
            row['cluster_type']
        )
        context_counts[key] = context_counts.get(key, 0) + 1
    
    # Filter contexts with at least 3 jobs
    contexts = []
    for (job_role, role_sub_cluster, exp_level, cluster_type), count in context_counts.items():
        if count >= 3:
            contexts.append({
                'job_role': job_role,
                'role_sub_cluster': role_sub_cluster,
                'experience_level': exp_level,
                'cluster_type': cluster_type,
                'total_jobs': count,
                'insufficient_data': count < 10  # Flag for insufficient data
            })
    
    # Sort contexts
    contexts.sort(key=lambda x: (x['job_role'], x['role_sub_cluster'] or '', x['experience_level'], x['cluster_type']))
    
    print(f"Found {len(contexts)} 4D contexts")
    
    # Process each context
    total_frequencies = 0
    insufficient_data_count = 0
    
    for i, context in enumerate(contexts, 1):
        insufficient_flag = " [INSUFFICIENT DATA]" if context.get('insufficient_data') else ""
        print(f"\nProcessing context {i}/{len(contexts)}: {context['job_role']} / {context['role_sub_cluster']} / {context['experience_level']} / {context['cluster_type']} ({context['total_jobs']} jobs){insufficient_flag}")
        
        if context.get('insufficient_data'):
            insufficient_data_count += 1
        
        # Calculate frequencies
        frequencies = calculate_frequencies_for_context(supabase, context)
        
        # Save to database
        save_frequencies(supabase, frequencies)
        
        total_frequencies += len(frequencies)
        print(f"  ✓ Calculated {len(frequencies)} skill frequencies")
    
    print(f"\n{'='*80}")
    print(f"FREQUENCY CALCULATION COMPLETE")
    print(f"{'='*80}")
    print(f"Contexts processed: {len(contexts)}")
    print(f"Contexts with insufficient data (<10 jobs): {insufficient_data_count}")
    print(f"Total frequencies calculated: {total_frequencies}")
    print(f"\n⚠️  Note: Contexts with <10 jobs are marked as 'Insufficient Data'")
    print(f"   Users should refer to parent group or combined groups for these contexts")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
