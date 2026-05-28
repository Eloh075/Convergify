"""Search for a specific LinkedIn job ID in the database."""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def search_job_id(job_id: str):
    """Search for a job ID in the database."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return
    
    print(f"Connecting to Supabase...")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    print(f"Searching for job ID: {job_id}")
    
    # Get all LinkedIn URLs
    result = supabase.table("job_listings").select("*").eq("website", "LinkedIn").execute()
    
    print(f"Total LinkedIn jobs in database: {len(result.data)}")
    
    # Search for the job ID in URLs
    found = False
    for job in result.data:
        url = job.get('url', '')
        if job_id in url:
            found = True
            print(f"\n{'='*80}")
            print(f"FOUND JOB!")
            print(f"{'='*80}")
            print(f"URL: {url}")
            print(f"Job Role: {job.get('job_role', 'N/A')}")
            print(f"Location: {job.get('location', 'N/A')}")
            print(f"Experience Level: {job.get('experience_level', 'N/A')}")
            print(f"Date Posted: {job.get('date_posted', 'N/A')}")
            print(f"Scraped At: {job.get('scraped_at', 'N/A')}")
            print(f"Extracted: {job.get('extracted', False)}")
            print(f"Job Sector: {job.get('job_sector', 'N/A')}")
            print(f"{'='*80}\n")
            break
    
    if not found:
        print(f"\nJob ID {job_id} NOT FOUND in database.")
        print(f"This job was not scraped during your bulk scraping runs.")


if __name__ == "__main__":
    job_id = "4373232625"
    if len(sys.argv) > 1:
        job_id = sys.argv[1]
    
    search_job_id(job_id)
