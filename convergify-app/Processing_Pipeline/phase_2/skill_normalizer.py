"""
Skill Normalizer

Handles chunked batch normalization of skills using LLM.
"""
import json
from typing import List, Dict, Set
from supabase import Client
from gemini_client import GeminiClient
from config import Phase2Config


class SkillNormalizer:
    """Normalizes raw skills to canonical skills using chunked batch processing"""
    
    def __init__(self, supabase: Client, gemini_client: GeminiClient):
        self.supabase = supabase
        self.gemini = gemini_client
        self.chunk_size = Phase2Config.CHUNK_SIZE
    
    def get_existing_canonical_names(self) -> Set[str]:
        """Get all existing canonical names from job_skills"""
        result = self.supabase.table("job_skills").select("canonical_name").execute()
        return set([r['canonical_name'] for r in result.data if r['canonical_name']])
    
    def get_canonical_skills(self) -> List[str]:
        """Get all existing canonical skills"""
        result = self.supabase.table("canonical_skills").select("canonical_name").execute()
        return [r['canonical_name'] for r in result.data]
    
    def get_skill_mappings(self, job_role: str = None) -> Dict[str, str]:
        """Get existing skill_name -> canonical_name mappings"""
        query = self.supabase.table("job_skills").select("skill_name, canonical_name").not_.is_("canonical_name", "null")
        
        if job_role:
            query = query.eq("job_role", job_role)
        
        result = query.execute()
        
        # Build mapping (skill_name -> canonical_name)
        mappings = {}
        for r in result.data:
            if r['canonical_name']:
                mappings[r['skill_name']] = r['canonical_name']
        
        return mappings
    
    def get_unknown_skills(self, job_role: str = None) -> Set[str]:
        """Get UNIQUE skills that haven't been normalized yet"""
        query = self.supabase.table("job_skills").select("skill_name").is_("canonical_name", "null")
        
        if job_role:
            query = query.eq("job_role", job_role)
        
        result = query.execute()
        
        # Get unique skill names
        unknown = set([r['skill_name'] for r in result.data])
        
        # Filter out skills that already have mappings (from ALL jobs, not just current job)
        existing_mappings = self.get_skill_mappings()  # Get ALL mappings across all jobs
        unknown = unknown - set(existing_mappings.keys())
        
        return unknown
    
    def chunk_skills(self, skills: Set[str]) -> List[List[str]]:
        """Split skills into chunks"""
        skills_list = sorted(list(skills))
        chunks = []
        
        for i in range(0, len(skills_list), self.chunk_size):
            chunk = skills_list[i:i + self.chunk_size]
            chunks.append(chunk)
        
        return chunks
    
    def normalize_chunk(
        self, 
        chunk: List[str], 
        canonical_skills: List[str]
    ) -> Dict[str, str]:
        """Normalize a chunk of skills using LLM with retry logic"""
        
        max_retries = 3
        for attempt in range(max_retries):
            prompt = f"""Here is our current master list of Canonical Skills:
{json.dumps(canonical_skills, indent=2)}

Here are {len(chunk)} new raw skills scraped from job postings:
{json.dumps(chunk, indent=2)}

Your task: Map every single new raw skill to an existing Canonical Skill. 
If a raw skill absolutely does not fit, invent a clean, generic Canonical Skill for it.

Examples:
- "ReactJS v18" → "React" (existing canonical)
- ".NET 8" → ".NET" (existing canonical)
- "SomeWeirdTool" → "SomeWeirdTool" (new canonical, no match found)
- "python programming" → "Python" (existing canonical)

You MUST return a complete JSON dictionary containing exactly {len(chunk)} keys, formatted like this:
{{
  "raw_skill_1": "Canonical_Skill",
  "raw_skill_2": "New_Canonical_Skill",
  ...
}}

CRITICAL RULES:
1. Return ALL {len(chunk)} mappings. Do not skip any skills.
2. Use existing canonical skills whenever possible.
3. Only create new canonical skills when absolutely necessary.
4. Keep canonical names clean and generic (no version numbers, no special characters).
5. Return ONLY the JSON dictionary, no other text.
"""
            
            try:
                # Call LLM
                mappings = self.gemini.generate_json(prompt)
                
                # Validate response
                if len(mappings) != len(chunk):
                    missing = set(chunk) - set(mappings.keys())
                    extra = set(mappings.keys()) - set(chunk)
                    
                    if attempt < max_retries - 1:
                        print(f"    ⚠️  LLM returned {len(mappings)} mappings, expected {len(chunk)}. Retrying (attempt {attempt + 2}/{max_retries})...")
                        if missing:
                            print(f"        Missing: {missing}")
                        if extra:
                            print(f"        Extra: {extra}")
                        continue
                    else:
                        # Last attempt - try to fix it
                        if missing and not extra:
                            # LLM skipped some skills - map them to themselves
                            print(f"    ⚠️  Auto-fixing {len(missing)} missing skills by mapping to themselves")
                            for skill in missing:
                                mappings[skill] = skill
                        elif extra and not missing:
                            # LLM added extra skills - remove them
                            print(f"    ⚠️  Removing {len(extra)} extra mappings")
                            for skill in extra:
                                del mappings[skill]
                        else:
                            raise Exception(
                                f"LLM returned {len(mappings)} mappings, expected {len(chunk)}. "
                                f"Missing: {missing}, Extra: {extra}"
                            )
                
                return mappings
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"    ⚠️  Error: {e}. Retrying (attempt {attempt + 2}/{max_retries})...")
                    continue
                else:
                    raise
        
        raise Exception(f"Failed to normalize chunk after {max_retries} attempts")
    
    def save_mappings(self, mappings: Dict[str, str], job_role: str = None):
        """Save canonical names directly to job_skills table"""
        
        # Get unique canonical skills
        canonical_skills = set(mappings.values())
        
        # Insert new canonical skills to canonical_skills table
        for canonical in canonical_skills:
            self.supabase.table("canonical_skills").upsert({
                "canonical_name": canonical
            }, on_conflict="canonical_name").execute()
        
        # Get canonical skill IDs
        result = self.supabase.table("canonical_skills").select(
            "id, canonical_name"
        ).in_("canonical_name", list(canonical_skills)).execute()
        
        canonical_id_map = {r['canonical_name']: r['id'] for r in result.data}
        
        # Update job_skills with canonical names and IDs
        for raw_skill, canonical in mappings.items():
            canonical_id = canonical_id_map[canonical]
            
            # Update all job_skills rows with this skill_name
            update_query = self.supabase.table("job_skills").update({
                "canonical_name": canonical,
                "canonical_skill_id": canonical_id
            }).eq("skill_name", raw_skill)
            
            if job_role:
                update_query = update_query.eq("job_role", job_role)
            
            update_query.execute()
    
    def apply_existing_mappings(self, job_role: str = None):
        """Apply existing skill mappings to unnormalized skills (no LLM needed)"""
        
        # Get existing mappings
        existing_mappings = self.get_skill_mappings()
        
        if not existing_mappings:
            return 0
        
        print(f"\nApplying {len(existing_mappings)} existing mappings...")
        
        # Get canonical skill IDs
        canonical_names = list(set(existing_mappings.values()))
        result = self.supabase.table("canonical_skills").select(
            "id, canonical_name"
        ).in_("canonical_name", canonical_names).execute()
        
        canonical_id_map = {r['canonical_name']: r['id'] for r in result.data}
        
        # Update job_skills with existing mappings
        updated_count = 0
        for skill_name, canonical_name in existing_mappings.items():
            canonical_id = canonical_id_map.get(canonical_name)
            if not canonical_id:
                continue
            
            # Update all unnormalized rows with this skill_name
            update_query = self.supabase.table("job_skills").update({
                "canonical_name": canonical_name,
                "canonical_skill_id": canonical_id
            }).eq("skill_name", skill_name).is_("canonical_name", "null")
            
            if job_role:
                update_query = update_query.eq("job_role", job_role)
            
            result = update_query.execute()
            updated_count += len(result.data)
        
        print(f"  ✓ Applied mappings to {updated_count} skills (no LLM cost)")
        return updated_count
    
    def normalize_all(self, job_role: str = None) -> Dict:
        """Normalize all unknown skills"""
        
        print(f"\n{'='*80}")
        print(f"NORMALIZING SKILLS" + (f" FOR {job_role}" if job_role else ""))
        print(f"{'='*80}")
        
        # Step 0: Apply existing mappings (no LLM cost)
        cached_count = self.apply_existing_mappings(job_role)
        
        # Get unknown skills
        unknown_skills = self.get_unknown_skills(job_role)
        print(f"\nUnknown skills to process: {len(unknown_skills)}")
        
        if not unknown_skills:
            print("No unknown skills to process!")
            return {
                "total_skills": 0,
                "chunks_processed": 0,
                "new_canonical": 0,
                "new_aliases": 0
            }
        
        # Get existing canonical skills
        canonical_skills = self.get_canonical_skills()
        print(f"Existing canonical skills: {len(canonical_skills)}")
        
        # Chunk skills
        chunks = self.chunk_skills(unknown_skills)
        print(f"Created {len(chunks)} chunks (size: {self.chunk_size})")
        
        # Process each chunk
        total_new_canonical = 0
        total_new_aliases = 0
        
        for i, chunk in enumerate(chunks):
            print(f"\nProcessing chunk {i+1}/{len(chunks)} ({len(chunk)} skills)...")
            
            try:
                # Normalize chunk
                mappings = self.normalize_chunk(chunk, canonical_skills)
                
                # Count new canonical skills
                new_canonical = set(mappings.values()) - set(canonical_skills)
                total_new_canonical += len(new_canonical)
                total_new_aliases += len(mappings)
                
                # Save to database
                self.save_mappings(mappings, job_role)
                
                # Update canonical skills list for next chunk
                canonical_skills.extend(list(new_canonical))
                
                print(f"  ✓ Mapped {len(mappings)} skills")
                print(f"  ✓ Created {len(new_canonical)} new canonical skills")
                
            except Exception as e:
                print(f"  ✗ Error processing chunk: {e}")
                raise
        
        print(f"\n{'='*80}")
        print(f"NORMALIZATION COMPLETE")
        print(f"{'='*80}")
        print(f"Total skills processed: {len(unknown_skills)}")
        print(f"Chunks processed: {len(chunks)}")
        print(f"New canonical skills: {total_new_canonical}")
        print(f"New aliases: {total_new_aliases}")
        
        return {
            "total_skills": len(unknown_skills),
            "chunks_processed": len(chunks),
            "new_canonical": total_new_canonical,
            "new_aliases": total_new_aliases
        }
