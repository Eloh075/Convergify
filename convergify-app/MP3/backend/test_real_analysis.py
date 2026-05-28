#!/usr/bin/env python3
"""
End-to-end test that simulates actual analysis flow
This will help us see where the uniform 10% / 40% values are coming from
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engines.skill_extraction.extractor import SkillExtractor
from engines.skill_classification.classifier import SkillClassifier
from engines.strategic_analysis.analyzer import StrategicAnalyzer
from engines.skill_classification.models import JobSkills
from engines.skill_extraction.models import ExtractedSkill

# Sample resume
SAMPLE_RESUME = """
John Doe
Senior Software Engineer

EXPERIENCE:
- 5 years of Python development
- Built REST APIs using FastAPI and Flask
- Worked with SQL databases (PostgreSQL, MySQL)
- Deployed applications using Docker

SKILLS:
- Python, SQL, Docker, FastAPI, REST APIs
"""

# Sample job postings
SAMPLE_JOBS = [
    {
        "id": "job1",
        "title": "Senior Backend Engineer",
        "description": """
        We're looking for a Senior Backend Engineer with:
        - Strong Python experience (5+ years)
        - SQL database expertise
        - Docker containerization
        - Blockchain Data experience
        - Graph Databases knowledge
        """
    },
    {
        "id": "job2",
        "title": "Full Stack Developer",
        "description": """
        Requirements:
        - Python programming
        - SQL databases
        - LangGraph framework
        - Transformer Models experience
        """
    },
    {
        "id": "job3",
        "title": "AI Engineer",
        "description": """
        Looking for:
        - Python
        - Machine Learning
        - Transformer Models
        - AI Agents development
        """
    }
]


def test_full_analysis():
    """Run full analysis pipeline and check for uniform values"""
    print("=" * 80)
    print("END-TO-END ANALYSIS TEST")
    print("=" * 80)
    
    # Step 1: Extract skills from resume
    print("\n[STEP 1] Extracting skills from resume...")
    extractor = SkillExtractor()
    
    try:
        resume_skills = extractor.extract_skills(SAMPLE_RESUME, "Senior Software Engineer")
        print(f"✅ Extracted {len(resume_skills)} skills from resume")
        for skill in resume_skills[:5]:
            print(f"   - {skill.skill_name} (confidence: {skill.confidence:.2f})")
    except Exception as e:
        print(f"❌ Resume extraction failed: {e}")
        resume_skills = None
    
    # Step 2: Extract skills from jobs
    print("\n[STEP 2] Extracting skills from jobs...")
    all_jobs_skills = []
    
    for job in SAMPLE_JOBS:
        try:
            job_skills_result = extractor.extract_skills(job["description"], job["title"])
            job_skills = JobSkills(
                job_id=job["id"],
                job_title=job["title"],
                skills=job_skills_result
            )
            all_jobs_skills.append(job_skills)
            print(f"✅ Job {job['id']}: Extracted {len(job_skills.skills)} skills")
            for skill in job_skills.skills[:3]:
                print(f"   - {skill.skill_name}")
        except Exception as e:
            print(f"❌ Job {job['id']} extraction failed: {e}")
    
    if not all_jobs_skills:
        print("\n❌ No job skills extracted, cannot continue")
        return
    
    # Step 3: Classify skills
    print("\n[STEP 3] Classifying skills...")
    classifier = SkillClassifier()
    
    try:
        classification_result = classifier.classify_skills_batch(all_jobs_skills)
        print(f"✅ Classified {len(classification_result.market_frequencies)} unique skills")
        
        # Check for uniform values (THE BUG)
        print("\n" + "=" * 80)
        print("CHECKING FOR UNIFORM VALUES BUG")
        print("=" * 80)
        
        frequencies = [freq.normalized_frequency for freq in classification_result.market_frequencies.values()]
        importances = []
        
        for job in classification_result.classified_jobs:
            for skill in job.classified_skills:
                if skill.canonical_name in classification_result.market_frequencies:
                    importances.append(skill.importance)
        
        # Check if all frequencies are the same
        unique_frequencies = set(f"{f:.2f}" for f in frequencies)
        unique_importances = set(importances)
        
        print(f"\nUnique frequency values: {unique_frequencies}")
        print(f"Unique importance values: {unique_importances}")
        
        if len(unique_frequencies) == 1:
            print("\n❌ BUG DETECTED: All frequencies are the same!")
            print(f"   All skills have frequency: {frequencies[0]:.2f}")
        else:
            print("\n✅ Frequencies are varied (bug is fixed)")
        
        if len(unique_importances) == 1:
            print("\n❌ BUG DETECTED: All importances are the same!")
            print(f"   All skills have importance: {list(unique_importances)[0]}")
        else:
            print("\n✅ Importances are varied (bug is fixed)")
        
        # Print detailed breakdown
        print("\n" + "=" * 80)
        print("DETAILED SKILL BREAKDOWN")
        print("=" * 80)
        
        for skill_name, freq_data in sorted(
            classification_result.market_frequencies.items(),
            key=lambda x: x[1].normalized_frequency,
            reverse=True
        )[:10]:
            # Find importance for this skill
            importance = None
            for job in classification_result.classified_jobs:
                for skill in job.classified_skills:
                    if skill.canonical_name == skill_name:
                        importance = skill.importance
                        break
                if importance:
                    break
            
            print(f"\n{skill_name}:")
            print(f"  Raw Frequency: {freq_data.raw_frequency} jobs")
            print(f"  Normalized: {freq_data.normalized_frequency:.2f} ({freq_data.normalized_frequency*100:.0f}%)")
            print(f"  Importance: {importance}")
            
            # Calculate expected values
            total_jobs = len(all_jobs_skills)
            expected_norm = freq_data.raw_frequency / total_jobs
            print(f"  Expected Normalized: {expected_norm:.2f}")
            
            if abs(freq_data.normalized_frequency - expected_norm) > 0.01:
                print(f"  ⚠️  MISMATCH! Should be {expected_norm:.2f}")
        
    except Exception as e:
        print(f"❌ Classification failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Strategic analysis
    print("\n[STEP 4] Running strategic analysis...")
    analyzer = StrategicAnalyzer()
    
    try:
        # Use first job for single-job analysis
        analysis_result = analyzer.analyze_single_job(
            resume_text=SAMPLE_RESUME,
            job_description=SAMPLE_JOBS[0]["description"],
            classification_result=classification_result
        )
        
        print(f"✅ Analysis complete")
        print(f"   Match Score: {analysis_result.match_score:.1%}")
        print(f"   Skill Matches: {len(analysis_result.skill_matches)}")
        print(f"   Skill Gaps: {len(analysis_result.skill_gaps)}")
        
        # Check skill gaps for uniform values
        print("\n" + "=" * 80)
        print("SKILL GAPS ANALYSIS")
        print("=" * 80)
        
        gap_importances = [gap.importance for gap in analysis_result.skill_gaps]
        gap_market_freqs = [gap.market_frequency for gap in analysis_result.skill_gaps]
        
        unique_gap_importances = set(f"{imp:.2f}" if isinstance(imp, float) else imp for imp in gap_importances)
        unique_gap_freqs = set(f"{freq:.2f}" for freq in gap_market_freqs)
        
        print(f"\nUnique gap importance values: {unique_gap_importances}")
        print(f"Unique gap market frequency values: {unique_gap_freqs}")
        
        if len(unique_gap_importances) == 1:
            print("\n❌ BUG: All skill gaps have same importance!")
        else:
            print("\n✅ Skill gap importances are varied")
        
        if len(unique_gap_freqs) == 1:
            print("\n❌ BUG: All skill gaps have same market frequency!")
        else:
            print("\n✅ Skill gap market frequencies are varied")
        
        # Print first 5 gaps
        print("\nFirst 5 Skill Gaps:")
        for gap in analysis_result.skill_gaps[:5]:
            print(f"\n{gap.skill_name}:")
            print(f"  Importance: {gap.importance}")
            print(f"  Market Frequency: {gap.market_frequency:.2f} ({gap.market_frequency*100:.0f}%)")
            print(f"  Match Status: {gap.match_status}")
        
        # Check skill matches
        print("\n" + "=" * 80)
        print("SKILL MATCHES ANALYSIS")
        print("=" * 80)
        
        print("\nFirst 5 Skill Matches:")
        for match in analysis_result.skill_matches[:5]:
            print(f"\n{match.skill_name}:")
            print(f"  Match Status: {match.match_status}")
            print(f"  Confidence: {match.confidence_score:.2f}")
            print(f"  Evidence Found: {match.evidence.found if match.evidence else 'N/A'}")
            print(f"  Market Frequency: {match.market_frequency:.2f} ({match.market_frequency*100:.0f}%)")
        
    except Exception as e:
        print(f"❌ Strategic analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_full_analysis()
