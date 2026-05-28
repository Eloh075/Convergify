"""Clear cache for jobs that have 0 classified skills"""
from database import SessionLocal
from models.job import Job

db = SessionLocal()

# Find jobs with empty classified skills
jobs_with_empty_cache = db.query(Job).filter(
    Job.classified_skills != None
).all()

empty_jobs = [j for j in jobs_with_empty_cache if len(j.classified_skills_list) == 0]

print(f"Found {len(empty_jobs)} jobs with empty classified skills cache")
print()

if empty_jobs:
    print("Jobs to clear:")
    for job in empty_jobs:
        print(f"  - {job.title} ({job.company})")
    print()
    
    response = input("Clear cache for these jobs? (yes/no): ")
    
    if response.lower() == 'yes':
        for job in empty_jobs:
            job.classified_skills = None
            job.classification_date = None
            job.skills_processed = False
        
        db.commit()
        print(f"✅ Cleared cache for {len(empty_jobs)} jobs")
        print("These jobs will be re-extracted on next analysis (when API quota is available)")
    else:
        print("Cancelled")
else:
    print("No jobs with empty cache found")

db.close()
