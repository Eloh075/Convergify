"""
Simplified analysis script that works with the current codebase
Reads data from database using IDs passed as arguments
"""
import sys
import json
from datetime import datetime

def run_simple_analysis(resume_id, job_ids_json, analysis_mode):
    """
    Run a simplified analysis without external dependencies
    Fetches data from database using IDs
    """
    try:
        # Import database here to avoid issues
        from database import SessionLocal
        from models.resume import Resume
        from models.job import Job
        
        # Log to stderr for debugging
        print(f"Starting analysis...", file=sys.stderr)
        print(f"Resume ID: {resume_id}", file=sys.stderr)
        
        # Get database session
        db = SessionLocal()
        
        try:
            # Fetch resume
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                raise Exception(f"Resume not found: {resume_id}")
            
            resume_text = resume.original_text
            print(f"Resume text length: {len(resume_text)}", file=sys.stderr)
            
            # Fetch jobs
            job_ids = json.loads(job_ids_json)
            print(f"Fetching {len(job_ids)} jobs", file=sys.stderr)
            
            jobs = db.query(Job).filter(Job.id.in_(job_ids)).all()
            if not jobs:
                raise Exception("No jobs found")
            
            print(f"Loaded {len(jobs)} jobs from database", file=sys.stderr)
            
            # Convert to dict format
            jobs_data = []
            for job in jobs:
                jobs_data.append({
                    'job_id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location or 'Not specified',
                    'description': job.description,
                    'required_skills': job.skills_list or []
                })
            
        finally:
            db.close()
        
        # Simple skill extraction from resume
        resume_skills = extract_skills_simple(resume_text)
        print(f"Extracted {len(resume_skills)} skills from resume", file=sys.stderr)
        
        # Extract skills from jobs
        all_job_skills = set()
        job_details = []
        
        for job in jobs_data:
            job_skills = job.get('required_skills', [])
            all_job_skills.update(job_skills)
            
            job_details.append({
                'job_id': job['job_id'],
                'title': job['title'],
                'company': job['company'],
                'location': job.get('location', 'Not specified'),
                'required_skills': job_skills
            })
        
        # Calculate matches and gaps
        resume_skills_set = set(resume_skills)
        all_job_skills_set = set(all_job_skills)
        
        matching_skills = list(resume_skills_set.intersection(all_job_skills_set))
        missing_skills = list(all_job_skills_set - resume_skills_set)
        
        # Calculate match score
        if all_job_skills_set:
            match_score = (len(matching_skills) / len(all_job_skills_set)) * 100
        else:
            match_score = 0
        
        # Build skill gaps with importance
        skill_gaps = []
        for skill in missing_skills[:20]:  # Top 20 gaps
            # Count how many jobs require this skill
            job_count = sum(1 for job in jobs_data if skill in job.get('required_skills', []))
            
            # Calculate importance as a number (0-1)
            importance_score = min(job_count / max(len(jobs_data), 1), 1.0)
            
            # Calculate market demand (0-1)
            market_demand = min(job_count / 5.0, 1.0)  # Normalize to max of 5 jobs
            
            skill_gaps.append({
                'skill': skill,
                'importance': importance_score,
                'market_demand': market_demand,
                'category': categorize_skill(skill),
                'learning_resources': []
            })
        
        # Sort by importance
        skill_gaps.sort(key=lambda x: x['importance'], reverse=True)
        
        # Build skill matches
        skill_matches = []
        for skill in matching_skills[:30]:  # Top 30 matches
            job_count = sum(1 for job in jobs_data if skill in job.get('required_skills', []))
            
            # Count resume mentions (simple count of occurrences)
            resume_mentions = resume_text.lower().count(skill.lower())
            
            # Calculate relevance score (0-1)
            relevance_score = min(job_count / max(len(jobs_data), 1), 1.0)
            
            skill_matches.append({
                'skill': skill,
                'relevance_score': relevance_score,
                'resume_mentions': resume_mentions,
                'job_mentions': job_count
            })
        
        # Sort by relevance score
        skill_matches.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Generate recommendations
        recommendations = []
        
        if match_score < 50:
            recommendations.append({
                'priority': 'High',
                'category': 'Skill Development',
                'title': 'Focus on Core Skills',
                'description': f'Your current match score is {match_score:.1f}%. Focus on acquiring the most frequently required skills to improve your competitiveness.',
                'action_items': [f'Learn {skill}' for skill in missing_skills[:5]]
            })
        
        if len(missing_skills) > 10:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Career Strategy',
                'title': 'Prioritize High-Impact Skills',
                'description': 'Focus on skills that appear in multiple job postings to maximize your market value.',
                'action_items': ['Take online courses', 'Build portfolio projects', 'Seek mentorship']
            })
        
        recommendations.append({
            'priority': 'Medium',
            'category': 'Resume Optimization',
            'title': 'Highlight Matching Skills',
            'description': f'You have {len(matching_skills)} skills that match job requirements. Make sure these are prominently featured in your resume.',
            'action_items': ['Update resume summary', 'Add specific examples', 'Quantify achievements']
        })
        
        # Market insights
        # Build top skills with proper structure
        top_skills_data = []
        for skill in list(all_job_skills_set)[:10]:
            job_count = sum(1 for job in jobs_data if skill in job.get('required_skills', []))
            demand_score = min(job_count / max(len(jobs_data), 1), 1.0)
            
            top_skills_data.append({
                'skill': skill,
                'demand_score': demand_score,
                'job_count': job_count,
                'growth_trend': None  # Not available - requires historical data
            })
        
        # Sort by demand score
        top_skills_data.sort(key=lambda x: x['demand_score'], reverse=True)
        
        market_insights = {
            'total_jobs_analyzed': len(jobs_data),
            'top_skills': top_skills_data,
            'competition_level': 'high' if match_score < 50 else 'medium' if match_score < 75 else 'low',
            'average_salary': {
                'min': 60000,
                'max': 120000,
                'currency': 'USD'
            }
        }
        
        # Career paths
        career_paths = []
        if match_score >= 70:
            career_paths.append({
                'role': 'Senior ' + (jobs_data[0]['title'] if jobs_data else 'Position'),
                'probability': min((match_score + 10) / 100, 1.0),
                'company_type': 'Tech Companies',
                'timeline': '1-2 years',
                'required_skills': missing_skills[:3]
            })
        else:
            career_paths.append({
                'role': jobs_data[0]['title'] if jobs_data else 'Target Position',
                'probability': match_score / 100,
                'company_type': 'Tech Companies',
                'timeline': '6-12 months',
                'required_skills': missing_skills[:5]
            })
        
        # Add alternative path
        if len(jobs_data) > 1:
            career_paths.append({
                'role': jobs_data[1]['title'] if len(jobs_data) > 1 else 'Alternative Position',
                'probability': max((match_score - 10) / 100, 0.3),
                'company_type': 'Startups',
                'timeline': '6-12 months',
                'required_skills': missing_skills[:4]
            })
        
        # Build final result
        result = {
            'success': True,
            'analysis_id': resume_id,
            'timestamp': datetime.now().isoformat(),
            'overall_match_score': round(match_score, 1),
            'skill_gaps': skill_gaps,
            'skill_matches': skill_matches,
            'recommendations': recommendations,
            'market_insights': market_insights,
            'career_paths': career_paths,
            'job_details': job_details,
            'summary': {
                'total_skills_identified': len(resume_skills),
                'matching_skills': len(matching_skills),
                'missing_skills': len(missing_skills),
                'jobs_analyzed': len(jobs_data)
            }
        }
        
        # Output as JSON
        print(f"Analysis complete, outputting result", file=sys.stderr)
        print(json.dumps(result))
        sys.stdout.flush()
        return 0
        
    except Exception as e:
        print(f"ERROR in analysis: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        
        error_result = {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        print(json.dumps(error_result))
        sys.stdout.flush()
        return 1

def extract_skills_simple(text):
    """Simple skill extraction using keyword matching"""
    # Common tech skills to look for
    common_skills = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust', 'PHP',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Express',
        'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'CI/CD',
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn',
        'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum',
        'HTML', 'CSS', 'Tailwind', 'Bootstrap', 'Sass',
        'Linux', 'Bash', 'PowerShell', 'Terraform', 'Ansible',
        'Data Analysis', 'Data Visualization', 'Pandas', 'NumPy',
        'Project Management', 'Leadership', 'Communication', 'Problem Solving'
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in common_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills

def categorize_skill(skill):
    """Categorize a skill"""
    programming_langs = ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust', 'PHP']
    frameworks = ['React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Express']
    databases = ['SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch']
    cloud = ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes']
    
    if skill in programming_langs:
        return 'Programming Language'
    elif skill in frameworks:
        return 'Framework'
    elif skill in databases:
        return 'Database'
    elif skill in cloud:
        return 'Cloud/DevOps'
    else:
        return 'Other'

if __name__ == '__main__':
    # Read arguments: resume_id, job_ids_json, analysis_mode
    if len(sys.argv) != 4:
        print(json.dumps({'success': False, 'error': 'Usage: script.py <resume_id> <job_ids_json> <analysis_mode>'}))
        sys.exit(1)
    
    resume_id = sys.argv[1]
    job_ids_json = sys.argv[2]
    analysis_mode = sys.argv[3]
    
    sys.exit(run_simple_analysis(resume_id, job_ids_json, analysis_mode))
