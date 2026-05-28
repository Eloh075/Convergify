"""
Add sample jobs to the database for testing
"""
from database import SessionLocal
from models.job import Job, JobGroup
from datetime import datetime
import uuid

def add_sample_jobs():
    db = SessionLocal()
    
    try:
        # Sample jobs data
        sample_jobs = [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "description": "We are looking for an experienced software engineer to join our team. You will work on building scalable web applications using modern technologies.",
                "location": "Singapore",
                "employment_type": "full-time",
                "salary_min": 80000,
                "salary_max": 120000,
                "requirements": ["5+ years of experience", "Strong Python skills", "Experience with React", "Knowledge of cloud platforms"],
                "skills": ["Python", "React", "AWS", "Docker", "PostgreSQL", "REST APIs"]
            },
            {
                "title": "Frontend Developer",
                "company": "Digital Solutions",
                "description": "Join our frontend team to build beautiful and responsive user interfaces. You'll work with React, TypeScript, and modern CSS frameworks.",
                "location": "Singapore",
                "employment_type": "full-time",
                "salary_min": 60000,
                "salary_max": 90000,
                "requirements": ["3+ years frontend experience", "Expert in React", "TypeScript proficiency", "UI/UX understanding"],
                "skills": ["React", "TypeScript", "CSS", "HTML", "JavaScript", "Tailwind CSS", "Git"]
            },
            {
                "title": "Data Scientist",
                "company": "Analytics Inc",
                "description": "We're seeking a data scientist to analyze large datasets and build machine learning models. You'll work on predictive analytics and data visualization.",
                "location": "Singapore",
                "employment_type": "full-time",
                "salary_min": 90000,
                "salary_max": 130000,
                "requirements": ["Master's degree in related field", "Strong Python and R skills", "ML experience", "Statistical analysis"],
                "skills": ["Python", "R", "Machine Learning", "TensorFlow", "Pandas", "SQL", "Data Visualization"]
            },
            {
                "title": "DevOps Engineer",
                "company": "Cloud Systems",
                "description": "Looking for a DevOps engineer to manage our cloud infrastructure and CI/CD pipelines. Experience with Kubernetes and AWS required.",
                "location": "Singapore",
                "employment_type": "full-time",
                "salary_min": 75000,
                "salary_max": 110000,
                "requirements": ["4+ years DevOps experience", "Kubernetes expertise", "AWS certification preferred", "CI/CD pipeline management"],
                "skills": ["Kubernetes", "AWS", "Docker", "Jenkins", "Terraform", "Linux", "Python", "Bash"]
            },
            {
                "title": "Product Manager",
                "company": "Innovation Labs",
                "description": "We need a product manager to lead our product development initiatives. You'll work with cross-functional teams to deliver great products.",
                "location": "Singapore",
                "employment_type": "full-time",
                "salary_min": 85000,
                "salary_max": 125000,
                "requirements": ["5+ years product management", "Technical background", "Agile methodology", "Stakeholder management"],
                "skills": ["Product Management", "Agile", "Jira", "User Research", "Data Analysis", "Communication", "Leadership"]
            }
        ]
        
        created_jobs = []
        
        for job_data in sample_jobs:
            job = Job(
                title=job_data["title"],
                company=job_data["company"],
                description=job_data["description"],
                location=job_data["location"],
                employment_type=job_data["employment_type"],
                salary_min=job_data["salary_min"],
                salary_max=job_data["salary_max"],
                source="sample_data",
                scraped_date=datetime.now()
            )
            
            # Set requirements and skills using property setters
            job.requirements_list = job_data["requirements"]
            job.skills_list = job_data["skills"]
            
            db.add(job)
            created_jobs.append(job)
            print(f"✅ Added: {job.title} at {job.company}")
        
        db.commit()
        
        # Refresh to get IDs
        for job in created_jobs:
            db.refresh(job)
        
        # Create a sample job group
        job_group = JobGroup(
            name="Sample Tech Jobs",
            description="A collection of sample technology jobs for testing the analysis system",
            group_type="custom",
            job_ids_list=[job.id for job in created_jobs]
        )
        
        db.add(job_group)
        db.commit()
        db.refresh(job_group)
        
        # Update jobs to reference the group
        for job in created_jobs:
            job.group_id = job_group.id
        
        db.commit()
        
        print(f"\n📁 Created job group: {job_group.name}")
        print(f"✅ Successfully added {len(created_jobs)} sample jobs!")
        print(f"\nYou can now:")
        print(f"  1. Upload a resume in the Resume Vault")
        print(f"  2. Go to Analysis Lab")
        print(f"  3. Select your resume and the 'Sample Tech Jobs' group")
        print(f"  4. Click 'Generate Analysis' to see the system in action!")
        
    except Exception as e:
        print(f"❌ Error adding sample jobs: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_jobs()
