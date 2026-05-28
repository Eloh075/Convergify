"""Load scraped jobs from V2 scraper into database."""

import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from database import SessionLocal
from models import Job, JobGroup

def load_jobs():
    """Load jobs from V2 scraper JSON file."""
    
    # Read the scraped data
    json_file = "../V2 Scraper w debugC/scraped_data/developer_20260204_211656.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    jobs_data = data['jobs']
    print(f"📊 Loading {len(jobs_data)} real jobs from V2 scraper...")
    
    db = SessionLocal()
    try:
        saved_jobs = []
        
        for job_data in jobs_data:
            # Extract description text
            description = ""
            if 'job_description' in job_data and 'full_text' in job_data['job_description']:
                description = ' '.join(job_data['job_description']['full_text'][:3])  # First 3 paragraphs
            
            job = Job(
                title=job_data['title'],
                company=job_data['company_name'],
                description=description[:1000] if description else "No description available",
                location=job_data['location'],
                employment_type=job_data['employment_type'],
                salary_min=job_data['salary_min'],
                salary_max=job_data['salary_max'],
                source="mycareersfuture_v2_real",
                scraped_date=datetime.now()
            )
            
            # Set list fields
            job.requirements_list = job_data.get('requirements', ["Requirements not specified"])
            job.skills_list = job_data.get('required_skills', ["Skills not specified"])
            
            db.add(job)
            saved_jobs.append(job)
            print(f"  ✅ Added: {job.title} at {job.company}")
        
        db.commit()
        
        # Refresh to get IDs
        for job in saved_jobs:
            db.refresh(job)
        
        # Create scraped group
        scraped_group = db.query(JobGroup).filter(JobGroup.name == "Scraped").first()
        if not scraped_group:
            scraped_group = JobGroup(
                name="Scraped",
                description="Jobs discovered through automated scraping",
                group_type="scraped",
                job_ids_list=[]
            )
            db.add(scraped_group)
            db.commit()
            db.refresh(scraped_group)
            print("📁 Created 'Scraped' group")
        
        # Add jobs to group
        current_job_ids = scraped_group.job_ids_list or []
        new_job_ids = [job.id for job in saved_jobs]
        scraped_group.job_ids_list = current_job_ids + new_job_ids
        
        # Update jobs with group ID
        for job in saved_jobs:
            job.group_id = scraped_group.id
        
        db.commit()
        
        print(f"✅ Successfully loaded {len(saved_jobs)} REAL jobs into database!")
        print("🎉 Jobs are now available in the frontend!")
        
    finally:
        db.close()

if __name__ == "__main__":
    load_jobs()