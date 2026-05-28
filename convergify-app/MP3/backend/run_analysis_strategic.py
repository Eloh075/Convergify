"""
Strategic Career Analysis Script

This script orchestrates the complete strategic analysis workflow:
1. Load resume and jobs from database
2. Extract/load skills with caching
3. Classify all skills together (batch)
4. Perform strategic analysis with evidence extraction
5. Generate optimized resume
6. Save results to database

INTERFACE: Matches run_analysis_simple.py for API compatibility
- Accepts: resume_id, job_ids_json, analysis_mode as command-line arguments
- Outputs: JSON to stdout with {'success': True/False, ...} format
- Logs: Debug info to stderr
"""

import sys
import json
from datetime import datetime
from typing import List, Dict, Any
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def run_strategic_analysis(resume_id: str, job_ids_json: str, analysis_mode: str) -> int:
    """
    Run strategic career analysis
    
    Args:
        resume_id: Resume ID
        job_ids_json: JSON string of job IDs
        analysis_mode: "single_job" or "market_intelligence"
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Import database here to avoid issues
        from database import SessionLocal
        from models.resume import Resume, OptimizedResume
        from models.job import Job
        from models.analysis import Analysis
        
        # Import engines
        from engines.skill_extraction.extractor import SkillExtractor
        from engines.skill_classification.classifier import SkillClassifier, JobSkills
        from engines.strategic_analysis.analyzer import StrategicAnalyzer
        from engines.resume_optimizer.optimizer import ResumeOptimizer
        from services.cache_service import CacheService
        
        # Log to stderr for debugging
        print(f"Starting strategic analysis...", file=sys.stderr)
        print(f"Resume ID: {resume_id}", file=sys.stderr)
        print(f"Job IDs JSON (raw): {repr(job_ids_json)}", file=sys.stderr)
        
        # Parse job IDs
        try:
            job_ids = json.loads(job_ids_json)
            print(f"Job IDs (parsed): {job_ids}", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"ERROR parsing job_ids_json: {e}", file=sys.stderr)
            print(f"  Input was: {repr(job_ids_json)}", file=sys.stderr)
            print(f"  Length: {len(job_ids_json)}", file=sys.stderr)
            print(f"  First 100 chars: {job_ids_json[:100]}", file=sys.stderr)
            raise
        
        # Get database session
        db = SessionLocal()
        
        try:
            # Step 1: Load data from database
            print(f"Step 1: Loading data from database...", file=sys.stderr)
            
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                raise Exception(f"Resume not found: {resume_id}")
            
            resume_text = resume.original_text
            print(f"Resume text length: {len(resume_text)}", file=sys.stderr)
            
            jobs = db.query(Job).filter(Job.id.in_(job_ids)).all()
            if not jobs:
                raise Exception("No jobs found")
            
            print(f"Loaded {len(jobs)} jobs from database", file=sys.stderr)
            
            # Step 2: Initialize services
            print(f"Step 2: Initializing services...", file=sys.stderr)
            cache_service = CacheService()
            skill_extractor = SkillExtractor()
            skill_classifier = SkillClassifier()
            strategic_analyzer = StrategicAnalyzer(db_session=db)
            resume_optimizer = ResumeOptimizer()
            print(f"Services initialized", file=sys.stderr)
            
            # Step 3: Extract/load skills from jobs (with caching)
            print(f"Step 3: Extracting skills from jobs (with caching)...", file=sys.stderr)
            all_jobs_skills = []
            
            for job in jobs:
                print(f"  Processing: {job.title}", file=sys.stderr)
                skills = cache_service.get_or_extract_job_skills(job, skill_extractor, db)
                all_jobs_skills.append(JobSkills(
                    job_id=job.id,
                    job_title=job.title,
                    skills=skills
                ))
                print(f"    Extracted {len(skills)} skills", file=sys.stderr)
            
            cache_stats = cache_service.get_cache_stats(len(jobs))
            print(f"Cache hits: {cache_stats.cached_jobs}/{cache_stats.total_jobs}", file=sys.stderr)
            print(f"Tokens saved: {cache_stats.tokens_saved}", file=sys.stderr)
            
            # Step 4: Classify all skills together (batch)
            print(f"Step 4: Classifying skills in batch...", file=sys.stderr)
            classification_result = skill_classifier.classify_skills_batch(all_jobs_skills)
            
            print(f"Total skills: {classification_result.processing_stats.total_skills_extracted}", file=sys.stderr)
            print(f"Unique skills: {classification_result.processing_stats.unique_skills_after_normalization}", file=sys.stderr)
            
            # Step 5: Perform strategic analysis
            print(f"Step 5: Performing strategic analysis...", file=sys.stderr)
            
            if analysis_mode == "single_job":
                analysis_result = strategic_analyzer.analyze_single_job(
                    resume_text,
                    classification_result
                )
            else:
                analysis_result = strategic_analyzer.analyze_market_intelligence(
                    resume_text,
                    classification_result
                )
            
            print(f"Overall match: {analysis_result.overall_match_score:.1f}%", file=sys.stderr)
            print(f"Strong matches: {analysis_result.summary.strong_matches}", file=sys.stderr)
            print(f"Partial matches: {analysis_result.summary.partial_matches}", file=sys.stderr)
            print(f"Missing skills: {analysis_result.summary.missing_skills}", file=sys.stderr)
            
            # Step 6: Generate optimized resume
            print(f"Step 6: Generating optimized resume...", file=sys.stderr)
            optimized_resume_result = resume_optimizer.optimize_resume(
                resume_text,
                analysis_result
            )
            
            print(f"Changes made: {len(optimized_resume_result.changes)}", file=sys.stderr)
            print(f"Validation: {'PASSED' if optimized_resume_result.validation_passed else 'FAILED'}", file=sys.stderr)
            
            # Step 7: Save optimized resume to database
            print(f"Step 7: Saving optimized resume to database...", file=sys.stderr)
            
            optimized_resume_db = OptimizedResume(
                original_resume_id=resume_id,
                optimized_text=optimized_resume_result.optimized_text,
                changes=json.dumps([c.dict() for c in optimized_resume_result.changes]),
                improvement_score=None,  # Can be calculated later
                target_job_ids=job_ids_json,
                generated_date=datetime.utcnow()
            )
            db.add(optimized_resume_db)
            db.flush()
            
            print(f"Optimized resume saved: {optimized_resume_db.id}", file=sys.stderr)
            
            # Step 8: Build final result matching simple script format
            print(f"Step 8: Building result...", file=sys.stderr)
            
            # Build skill gaps with proper importance and market demand scoring
            skill_gaps = []
            for skill_match in analysis_result.skill_matches:
                if skill_match.match_status == "Missing":
                    # Calculate importance score (0-1) based on category
                    importance_score = {
                        "Must-have": 1.0,
                        "Nice-to-have": 0.7,
                        "Preferred": 0.4
                    }.get(skill_match.importance, 0.5)
                    
                    # Get market demand from frequency (must be > 0, no fallback!)
                    market_demand = skill_match.market_frequency
                    if market_demand == 0:
                        raise ValueError(f"Skill '{skill_match.skill_name}' has 0 market frequency - classification failed!")
                    
                    # Get jobs requiring this skill
                    jobs_requiring = []
                    if classification_result.market_frequencies and skill_match.skill_name in classification_result.market_frequencies:
                        freq_data = classification_result.market_frequencies[skill_match.skill_name]
                        # Get job titles from the jobs that have this skill
                        for job in jobs:
                            if job.id in freq_data.job_ids if hasattr(freq_data, 'job_ids') else []:
                                jobs_requiring.append(job.title)
                    
                    # If we can't get specific jobs, use a generic list based on frequency
                    if not jobs_requiring:
                        job_count = int(market_demand * len(jobs))
                        jobs_requiring = [job.title for job in jobs[:job_count]]
                    
                    # Generate why_matters explanation
                    demand_pct = int(market_demand * 100)
                    importance_text = skill_match.importance.lower().replace('-', ' ')
                    why_matters = f"This {importance_text} skill is required by {demand_pct}% of analyzed positions and is critical for competitive applications."
                    
                    skill_gaps.append({
                        'skill': skill_match.skill_name,
                        'importance': importance_score,
                        'market_demand': market_demand,
                        'category': skill_match.importance,  # Must-have, Nice-to-have, Preferred
                        'learning_resources': [],
                        # New required fields
                        'importance_level': skill_match.importance,
                        'why_matters': why_matters,
                        'jobs_requiring': jobs_requiring
                    })
            
            # Sort by combined importance and market demand
            skill_gaps.sort(key=lambda x: (x['importance'] * 0.6 + x['market_demand'] * 0.4), reverse=True)
            
            # Build skill matches
            skill_matches = []
            for skill_match in analysis_result.skill_matches:
                if skill_match.match_status in ["Strong Match", "Partial Match"]:
                    # Count evidence snippets as resume mentions
                    resume_mentions = len(skill_match.evidence.text_snippets) if skill_match.evidence and skill_match.evidence.found else 0
                    
                    # Get actual job_mentions from classification result
                    job_mentions = 1
                    if classification_result.market_frequencies and skill_match.skill_name in classification_result.market_frequencies:
                        freq_data = classification_result.market_frequencies[skill_match.skill_name]
                        job_mentions = freq_data.raw_frequency
                    
                    # Get canonical group from classification result
                    canonical_group = 'General'
                    if hasattr(skill_match, 'canonical_group') and skill_match.canonical_group:
                        canonical_group = skill_match.canonical_group
                    
                    skill_matches.append({
                        'skill': skill_match.skill_name,
                        'relevance_score': skill_match.confidence_score,
                        'resume_mentions': resume_mentions,
                        'job_mentions': job_mentions,
                        'match_type': skill_match.match_type,
                        'evidence': skill_match.evidence.dict() if skill_match.evidence else None,
                        # New required fields
                        'canonical_group': canonical_group,
                        'match_percentage': round(skill_match.confidence_score * 100, 1),
                        'confidence_score': skill_match.confidence_score,
                        'importance_level': skill_match.importance,
                        'market_demand': skill_match.market_frequency,
                        'category': canonical_group
                    })
            
            # Sort by relevance score
            skill_matches.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Build recommendations
            recommendations = []
            for rec in analysis_result.recommendations:
                recommendations.append({
                    'priority': rec.priority,
                    'category': rec.category,
                    'title': rec.title,
                    'description': rec.description,
                    'action_items': rec.action_items,
                    'evidence_references': rec.evidence_references
                })
            
            # Build market insights
            top_skills_data = []
            for skill_match in analysis_result.skill_matches:
                # Get actual job_count from classification result
                job_count = 1
                if classification_result.market_frequencies and skill_match.skill_name in classification_result.market_frequencies:
                    freq_data = classification_result.market_frequencies[skill_match.skill_name]
                    job_count = freq_data.raw_frequency
                
                top_skills_data.append({
                    'skill': skill_match.skill_name,
                    'demand_score': skill_match.market_frequency,
                    'job_count': job_count,
                    'growth_trend': None,  # Not available - requires historical data
                    'importance': skill_match.importance
                })
            
            market_insights = {
                'total_jobs_analyzed': len(jobs),
                'top_skills': top_skills_data,  # Frontend can sort by demand_score
                'competition_level': 'high' if analysis_result.overall_match_score < 50 else 'medium' if analysis_result.overall_match_score < 75 else 'low',
                'average_salary': {
                    'min': 60000,
                    'max': 120000,
                    'currency': 'USD'
                },
                'must_have_skills': [s['skill'] for s in top_skills_data if s['importance'] == 'Must-have'][:5],
                'nice_to_have_skills': [s['skill'] for s in top_skills_data if s['importance'] == 'Nice-to-have'][:5]
            }
            
            # Build career paths
            career_paths = []
            match_score = analysis_result.overall_match_score
            
            if match_score >= 70:
                career_paths.append({
                    'role': 'Senior ' + (jobs[0].title if jobs else 'Position'),
                    'probability': min((match_score + 10) / 100, 1.0),
                    'company_type': 'Tech Companies',
                    'timeline': '1-2 years',
                    'required_skills': [sg['skill'] for sg in skill_gaps[:3]]
                })
            else:
                career_paths.append({
                    'role': jobs[0].title if jobs else 'Target Position',
                    'probability': match_score / 100,
                    'company_type': 'Tech Companies',
                    'timeline': '6-12 months',
                    'required_skills': [sg['skill'] for sg in skill_gaps[:5]]
                })
            
            # Add alternative path
            if len(jobs) > 1:
                career_paths.append({
                    'role': jobs[1].title if len(jobs) > 1 else 'Alternative Position',
                    'probability': max((match_score - 10) / 100, 0.3),
                    'company_type': 'Startups',
                    'timeline': '6-12 months',
                    'required_skills': [sg['skill'] for sg in skill_gaps[:4]]
                })
            
            # Build job details with match scores
            job_details = []
            for job in jobs:
                # Calculate individual job match score
                job_match_score = 0.0
                job_skill_count = 0
                
                # Count how many of this job's skills are matched
                if classification_result.market_frequencies:
                    for skill_name, freq_data in classification_result.market_frequencies.items():
                        if hasattr(freq_data, 'job_ids') and job.id in freq_data.job_ids:
                            job_skill_count += 1
                            # Check if this skill is matched in resume
                            for match in skill_matches:
                                if match['skill'] == skill_name:
                                    job_match_score += match['relevance_score']
                                    break
                
                # Calculate percentage
                if job_skill_count > 0:
                    job_match_score = (job_match_score / job_skill_count) * 100
                else:
                    job_match_score = 0.0
                
                job_details.append({
                    'job_id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location or 'Not specified',
                    'required_skills': job.skills_list or [],
                    'match_score': round(job_match_score, 1)
                })
            
            # Calculate match breakdown by importance level
            match_breakdown = {
                'must_have': {'matched': 0, 'total': 0},
                'nice_to_have': {'matched': 0, 'total': 0},
                'preferred': {'matched': 0, 'total': 0}
            }
            
            for skill_match in analysis_result.skill_matches:
                importance_key = skill_match.importance.lower().replace('-', '_')
                if importance_key in match_breakdown:
                    match_breakdown[importance_key]['total'] += 1
                    if skill_match.match_status in ["Strong Match", "Partial Match"]:
                        match_breakdown[importance_key]['matched'] += 1
            
            # Extract top strengths and top gaps
            top_strengths = [m['skill'] for m in sorted(skill_matches, key=lambda x: x['relevance_score'], reverse=True)[:5]]
            top_gaps = [g['skill'] for g in sorted(skill_gaps, key=lambda x: x['importance'], reverse=True)[:5]]
            
            # Step 9: Generate comprehensive narrative report (SKIPPED for performance)
            print(f"Step 9: Generating narrative report (skipped for performance)...", file=sys.stderr)
            # Skip LLM-based narrative report to improve performance
            # Provide a simple summary instead
            narrative_report = f"""# Analysis Summary

## Overview
Your resume has been analyzed against **{len(jobs)} job postings** in the market.

## Key Findings

### Match Score: {int(analysis_result.overall_match_score)}%

**Skills Matched:** {len([m for m in analysis_result.skill_matches if m.match_status in ["Strong Match", "Partial Match"]])} skills from your resume align with market requirements

**Skills to Develop:** {len([m for m in analysis_result.skill_matches if m.match_status == "Missing"])} skills identified as gaps

### What This Means
- Review the **Skill Gaps** tab to see which skills to prioritize learning
- Check **Skill Matches** to understand your current strengths
- Explore **Market Insights** to see what's in demand
- Read **Recommendations** for actionable next steps

### Next Steps
1. Focus on high-priority skill gaps (Must-have skills)
2. Strengthen partial matches with more experience
3. Leverage your strong matches in applications
4. Consider the career paths suggested in the Career Paths tab

*For detailed analysis, please review each tab above.*
"""
            
            # Build final result
            result = {
                'success': True,
                'analysis_id': resume_id,
                'timestamp': datetime.now().isoformat(),
                'overall_match_score': round(analysis_result.overall_match_score, 1),
                'skill_gaps': skill_gaps,
                'skill_matches': skill_matches,
                'recommendations': recommendations,
                'market_insights': market_insights,
                'career_paths': career_paths,
                'job_details': job_details,
                'narrative_report': narrative_report,  # Add narrative report
                'summary': {
                    'total_skills_identified': analysis_result.summary.total_skills_required,
                    'matching_skills': analysis_result.summary.strong_matches + analysis_result.summary.partial_matches,
                    'missing_skills': analysis_result.summary.missing_skills,
                    'jobs_analyzed': len(jobs)
                },
                'optimized_resume': {
                    'id': optimized_resume_db.id,
                    'changes_count': len(optimized_resume_result.changes),
                    'validation_passed': optimized_resume_result.validation_passed
                },
                'cache_stats': {
                    'cached_jobs': cache_stats.cached_jobs,
                    'total_jobs': cache_stats.total_jobs,
                    'tokens_saved': cache_stats.tokens_saved,
                    'cache_hit_rate': cache_stats.cache_hit_rate
                },
                # New required fields for dashboard redesign
                'match_breakdown': match_breakdown,
                'top_strengths': top_strengths,
                'top_gaps': top_gaps,
                'analyzed_jobs': job_details  # Alias for consistency
            }
            
            # Commit database changes
            db.commit()
            
            # Output as JSON to stdout
            print(f"Analysis complete, outputting result", file=sys.stderr)
            print(json.dumps(result))
            sys.stdout.flush()
            return 0
            
        finally:
            db.close()
        
    except Exception as e:
        print(f"ERROR in analysis: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        
        error_result = {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        print(json.dumps(error_result))
        sys.stdout.flush()
        return 1


if __name__ == '__main__':
    # Read arguments: resume_id, job_ids_json, analysis_mode
    if len(sys.argv) != 4:
        print(json.dumps({'success': False, 'error': 'Usage: script.py <resume_id> <job_ids_json> <analysis_mode>'}))
        sys.exit(1)
    
    resume_id = sys.argv[1]
    job_ids_json = sys.argv[2]
    analysis_mode = sys.argv[3]
    
    sys.exit(run_strategic_analysis(resume_id, job_ids_json, analysis_mode))
