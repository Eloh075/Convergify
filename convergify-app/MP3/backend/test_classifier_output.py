#!/usr/bin/env python3
"""
Simple test to check if classifier is returning correct frequencies
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engines.skill_classification.classifier import SkillClassifier, JobSkills
from engines.skill_extraction.models import ExtractedSkill

# Create simple test data
job1_skills = [
    ExtractedSkill(skill_name="Python", confidence=0.9, evidence=["Python"], category_hint="Language"),
    ExtractedSkill(skill_name="SQL", confidence=0.8, evidence=["SQL"], category_hint="Database"),
]

job2_skills = [
    ExtractedSkill(skill_name="Python", confidence=0.9, evidence=["Python"], category_hint="Language"),
    ExtractedSkill(skill_name="Java", confidence=0.8, evidence=["Java"], category_hint="Language"),
]

job3_skills = [
    ExtractedSkill(skill_name="Python", confidence=0.9, evidence=["Python"], category_hint="Language"),
    ExtractedSkill(skill_name="React", confidence=0.8, evidence=["React"], category_hint="Framework"),
]

jobs = [
    JobSkills(job_id="job1", job_title="Backend Dev", skills=job1_skills),
    JobSkills(job_id="job2", job_title="Full Stack Dev", skills=job2_skills),
    JobSkills(job_id="job3", job_title="Frontend Dev", skills=job3_skills),
]

print("=" * 80)
print("CLASSIFIER OUTPUT TEST")
print("=" * 80)
print(f"\nTest Data:")
print(f"  Total Jobs: 3")
print(f"  Job 1: Python, SQL")
print(f"  Job 2: Python, Java")
print(f"  Job 3: Python, React")
print(f"\nExpected:")
print(f"  Python: 3/3 = 1.0 (100%)")
print(f"  SQL: 1/3 = 0.33 (33%)")
print(f"  Java: 1/3 = 0.33 (33%)")
print(f"  React: 1/3 = 0.33 (33%)")

try:
    classifier = SkillClassifier()
    result = classifier.classify_skills_batch(jobs)
    
    print(f"\n" + "=" * 80)
    print("ACTUAL OUTPUT:")
    print("=" * 80)
    
    for skill_name in ["Python", "SQL", "Java", "React"]:
        if skill_name in result.market_frequencies:
            freq_data = result.market_frequencies[skill_name]
            print(f"\n{skill_name}:")
            print(f"  Raw Frequency: {freq_data.raw_frequency}")
            print(f"  Normalized: {freq_data.normalized_frequency:.2f} ({freq_data.normalized_frequency*100:.0f}%)")
            
            # Find importance
            importance = None
            for job in result.classified_jobs:
                for skill in job.classified_skills:
                    if skill.canonical_name == skill_name:
                        importance = skill.importance
                        break
                if importance:
                    break
            print(f"  Importance: {importance}")
        else:
            print(f"\n{skill_name}: NOT FOUND")
    
    # Check for uniform values
    print(f"\n" + "=" * 80)
    print("CHECKING FOR BUGS:")
    print("=" * 80)
    
    frequencies = [f.normalized_frequency for f in result.market_frequencies.values()]
    unique_freqs = set(f"{f:.2f}" for f in frequencies)
    
    print(f"\nUnique frequency values: {sorted(unique_freqs)}")
    
    if len(unique_freqs) == 1:
        print("\n❌ BUG: All frequencies are the same!")
    else:
        print("\n✅ Frequencies are varied (bug is fixed)")
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
