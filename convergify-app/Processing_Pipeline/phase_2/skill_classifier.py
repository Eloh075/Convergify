"""
Skill Classifier

Classifies canonical skills into tier1/tier2 categories using LLM.
"""
import json
from typing import List, Dict
from supabase import Client
from gemini_client import GeminiClient
from taxonomy import SkillTaxonomy


class SkillClassifier:
    """Classifies skills into taxonomy categories"""
    
    def __init__(self, supabase: Client, gemini_client: GeminiClient):
        self.supabase = supabase
        self.gemini = gemini_client
        self.taxonomy = SkillTaxonomy()
    
    def get_canonical_skills_for_role(self, job_role: str) -> List[Dict]:
        """Get all canonical skills for a job role from job_skills"""
        result = self.supabase.table("job_skills").select(
            "canonical_skill_id, canonical_name, tier1, tier2"
        ).eq("job_role", job_role).not_.is_("canonical_name", "null").execute()
        
        # Get unique canonical skills and separate classified vs unclassified
        seen = set()
        classified_skills = []
        unclassified_skills = []
        
        for r in result.data:
            if r['canonical_skill_id'] and r['canonical_skill_id'] not in seen:
                seen.add(r['canonical_skill_id'])
                
                if r['tier1'] and r['tier2']:
                    # Already classified
                    classified_skills.append({
                        'id': r['canonical_skill_id'],
                        'canonical_name': r['canonical_name'],
                        'tier1': r['tier1'],
                        'tier2': r['tier2']
                    })
                else:
                    # Needs classification
                    unclassified_skills.append({
                        'id': r['canonical_skill_id'],
                        'canonical_name': r['canonical_name']
                    })
        
        return classified_skills, unclassified_skills
    
    def classify_skills(self, skills: List[Dict], job_role: str) -> List[Dict]:
        """Classify skills using LLM"""
        
        # Get tier2 categories
        tier2_categories = {}
        for tier1 in self.taxonomy.get_all_tier1_categories():
            tier2_categories[tier1] = self.taxonomy.get_tier2_categories(tier1)
        
        prompt = f"""You are classifying skills for {job_role} roles.

IMPORTANT: Classification is about WHAT the skill IS, not how important it is.
- "Python" is always a "Programming Language" regardless of experience level
- "Leadership" is always a "Soft Skill" regardless of sub-cluster

Available Tier2 Categories (MUST use exact tier1/tier2 combinations):

{json.dumps(tier2_categories, indent=2)}

CRITICAL: Each tier2 category ONLY exists under its specific tier1. For example:
- "Specialized Domains" ONLY exists under "Technical", NOT under "Business/Ops"
- "Data Analysis" exists under BOTH "Technical" AND "Business/Ops" - choose based on context
- "Project Management" ONLY exists under "Business/Ops"

Skills to classify for {job_role}:
{json.dumps([{"id": s['id'], "name": s['canonical_name']} for s in skills], indent=2)}

For each skill, provide:
1. **tier1** and **tier2** from the categories above (MUST be valid combination from the list)
2. **skill_type**: Tool, Concept, Certification, or Other
3. **experience_context**: Extract any experience level if mentioned (e.g., "5+ years", "Expert"), or null

Return as JSON array with format:
[
  {{
    "skill_id": 123,
    "skill_name": "LangChain",
    "tier1": "Technical",
    "tier2": "LLM & Generative AI",
    "skill_type": "Tool",
    "experience_context": null
  }},
  ...
]

CRITICAL: 
- You must classify ALL {len(skills)} skills
- Choose the most appropriate tier2 category for each skill
- VERIFY tier1/tier2 combination exists in the categories list above
- Return ONLY the JSON array, no other text
"""
        
        # Call LLM
        classifications = self.gemini.generate_json(prompt)
        
        # Validate response
        if not isinstance(classifications, list):
            raise Exception(f"Expected list, got {type(classifications)}")
        
        if len(classifications) != len(skills):
            raise Exception(
                f"LLM returned {len(classifications)} classifications, expected {len(skills)}"
            )
        
        # Validate tier1/tier2 combinations
        invalid_classifications = []
        for classification in classifications:
            tier1 = classification.get('tier1')
            tier2 = classification.get('tier2')
            skill_name = classification.get('skill_name')
            
            if not self.taxonomy.is_valid_classification(tier1, tier2):
                invalid_classifications.append(f"{skill_name}: {tier1} / {tier2}")
        
        if invalid_classifications:
            print(f"\n⚠️  Warning: {len(invalid_classifications)} invalid classifications detected:")
            for invalid in invalid_classifications[:5]:  # Show first 5
                print(f"    - {invalid}")
            
            # Try to fix invalid classifications by using keyword fallback
            print(f"\n  Attempting to fix invalid classifications using keyword fallback...")
            for classification in classifications:
                tier1 = classification.get('tier1')
                tier2 = classification.get('tier2')
                
                if not self.taxonomy.is_valid_classification(tier1, tier2):
                    # Use keyword-based classification as fallback
                    skill_name = classification.get('skill_name')
                    fixed_tier1, fixed_tier2 = self.taxonomy.classify_skill(skill_name)
                    classification['tier1'] = fixed_tier1
                    classification['tier2'] = fixed_tier2
                    print(f"    Fixed: {skill_name} → {fixed_tier1} / {fixed_tier2}")
        
        return classifications
    
    def save_classifications(self, classifications: List[Dict], job_role: str):
        """Save classifications directly to job_skills table"""
        
        for c in classifications:
            # Update all job_skills rows with this canonical_skill_id and job_role
            self.supabase.table("job_skills").update({
                "tier1": c['tier1'],
                "tier2": c['tier2'],
                "skill_type": c.get('skill_type'),
                "experience_context": c.get('experience_context')
            }).eq("canonical_skill_id", c['skill_id']).eq("job_role", job_role).execute()
    
    def apply_existing_classifications(self, classified_skills: List[Dict], job_role: str):
        """Apply existing classifications to unclassified skills (no LLM needed)"""
        
        if not classified_skills:
            return 0
        
        print(f"\nApplying {len(classified_skills)} existing classifications...")
        
        # Update job_skills with existing classifications
        updated_count = 0
        for skill in classified_skills:
            # Update all unclassified rows with this canonical_skill_id and job_role
            result = self.supabase.table("job_skills").update({
                "tier1": skill['tier1'],
                "tier2": skill['tier2']
            }).eq("canonical_skill_id", skill['id']).eq("job_role", job_role).is_("tier1", "null").execute()
            
            updated_count += len(result.data)
        
        print(f"  ✓ Applied classifications to {updated_count} skills (no LLM cost)")
        return updated_count
    
    def classify_for_role(self, job_role: str) -> Dict:
        """Classify all skills for a job role"""
        
        print(f"\n{'='*80}")
        print(f"CLASSIFYING SKILLS FOR {job_role}")
        print(f"{'='*80}")
        
        # Get canonical skills for this role (separated into classified and unclassified)
        classified_skills, unclassified_skills = self.get_canonical_skills_for_role(job_role)
        
        print(f"\nCanonical skills for {job_role}:")
        print(f"  Already classified: {len(classified_skills)}")
        print(f"  Need classification: {len(unclassified_skills)}")
        
        # Apply existing classifications (no LLM cost)
        if classified_skills:
            self.apply_existing_classifications(classified_skills, job_role)
        
        if not unclassified_skills:
            print("\n✓ All skills already classified!")
            return {
                "job_role": job_role,
                "skills_classified": 0,
                "skills_cached": len(classified_skills)
            }
        
        # Classify only unclassified skills
        print(f"\nCalling LLM to classify {len(unclassified_skills)} new skills...")
        classifications = self.classify_skills(unclassified_skills, job_role)
        
        # Save to database
        print(f"Saving classifications to database...")
        self.save_classifications(classifications, job_role)
        
        # Print summary
        tier1_counts = {}
        for c in classifications:
            tier1 = c['tier1']
            tier1_counts[tier1] = tier1_counts.get(tier1, 0) + 1
        
        print(f"\n{'='*80}")
        print(f"CLASSIFICATION COMPLETE FOR {job_role}")
        print(f"{'='*80}")
        print(f"New skills classified: {len(classifications)}")
        print(f"Cached classifications applied: {len(classified_skills)}")
        print(f"Total skills: {len(classifications) + len(classified_skills)}")
        
        print(f"\nBreakdown by Tier1:")
        for tier1, count in sorted(tier1_counts.items()):
            print(f"  {tier1}: {count} skills")
        
        return {
            "job_role": job_role,
            "skills_classified": len(classifications),
            "skills_cached": len(classified_skills),
            "tier1_breakdown": tier1_counts
        }
