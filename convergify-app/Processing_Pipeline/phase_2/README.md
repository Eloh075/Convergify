# Phase 2: Context-Aware Skills Normalization

## Overview

Phase 2 normalizes the 19,214 raw skills extracted in Phase 1 into canonical skill groups with context-aware classification. Unlike simple deduplication, this phase understands that the same skill name can have different meanings depending on the job context.

## Why Context-Aware Normalization?

The same skill name means different things in different contexts:

- **"Python"** for a Data Scientist (data analysis, ML, pandas) vs. Backend Engineer (web frameworks, APIs, Django)
- **"Leadership"** for an Intern (project ownership) vs. Director (team management, strategic planning)
- **"Cloud"** for DevOps (infrastructure, Kubernetes) vs. Full Stack (deployment, hosting)

## Normalization Hierarchy (4 Dimensions)

Skills are normalized within a 4-dimensional context:

```
1. job_role (e.g., "AI Engineer", "Software Engineer", "Business Analyst")
   └── 2. role_sub_cluster (e.g., "Computer Vision", "Frontend", "MLOps", or NULL)
       └── 3. experience_level (e.g., "Internship", "Entry Level", "Associate", "Mid-Senior Level", "Director", "Executive")
           └── 4. cluster_type (e.g., "specific" vs "generalist")
```

### Why Each Dimension Matters

**1. job_role** - Different roles have completely different skill sets
- AI Engineer needs ML/AI skills
- Software Engineer needs web/backend skills
- Business Analyst needs business/ops skills

**2. role_sub_cluster** - Specializations within a role
- AI Engineer > Computer Vision (OpenCV, image processing)
- AI Engineer > Generative/NLP (transformers, LLMs)
- Software Engineer > Frontend (React, CSS)
- Software Engineer > Backend (databases, APIs)

**3. experience_level** - Skill depth and leadership expectations
- **Internship**: Basic skills, learning-focused
- **Entry Level**: Foundational skills, 0-2 years
- **Associate**: Intermediate skills, 2-5 years
- **Mid-Senior Level**: Advanced skills, 5-8+ years
- **Director**: Leadership + technical strategy
- **Executive**: Strategic leadership, business acumen

**4. cluster_type** - Specificity of requirements
- **specific**: Requires specific tech stack (e.g., "React developer")
- **generalist**: Rotational/broad (e.g., "any programming language")

## Architecture

### Pipeline Flow

```
Phase 2 Pipeline (Chunked Batch Architecture):
┌─────────────────────────────────────────────────────────────┐
│ Input: job_skills table (19,214 skills from 1,980 jobs)    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Pre-Filter (No LLM - Deduplication)                │
│ - Load all raw skills from job_skills                       │
│ - Remove exact duplicates (Python Set)                      │
│ - Check against existing skill_aliases database             │
│ Result: Only unknown skills need processing                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Chunking (No LLM - Split into batches)             │
│ - Split unknown skills into chunks of 50-100 each           │
│ - Prevents LLM laziness and cutoff issues                   │
│ Result: ~50-85 chunks per job_role                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Chunked LLM Normalization (50-85 calls per role)   │
│ FOR EACH chunk:                                             │
│   - Pass existing canonical skills + chunk                  │
│   - LLM maps raw_skill → canonical_skill                    │
│   - Returns complete JSON dictionary (all skills in chunk)  │
│   - Insert new canonicals and aliases to database           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: LLM Classification (7 calls - One per job_role)    │
│ FOR EACH job_role:                                          │
│   - Get all canonical skills for this role                  │
│   - Pass 24 tier2 categories to LLM                         │
│   - LLM decides which category each skill belongs to        │
│   - Cache classifications for reuse                         │
│ Note: Taxonomy provides categories, LLM classifies skills   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Process Each 4D Context (Math - No LLM)            │
│ FOR EACH (job_role, role_sub_cluster, exp_level, type):    │
│   - Load skills for this exact context                      │
│   - Apply cached classifications from Step 4                │
│   - Calculate frequencies within this context (math)        │
│   - Assign importance based on frequency (math)             │
│   - Write to database with context tags                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Output: Normalized & Classified Skills                      │
│ - skill_aliases: raw_skill → canonical_skill mappings       │
│ - canonical_skills: unique canonical skill names            │
│ - skill_classifications: tier1/tier2/type per role          │
│ - skill_market_frequencies: frequencies per 4D context      │
└─────────────────────────────────────────────────────────────┘
```

### Normalization Method: "Chunked Batch" Architecture

Phase 2 uses an optimized "Chunked Batch" approach that prevents LLM laziness while maintaining extreme cost-efficiency:

**1. Pre-Filter: Deduplication** (No LLM - Pure Python/SQL)
- Load all raw skills from job_skills table
- Remove exact duplicates using Python Set
- Check against existing `skill_aliases` database
- **Result**: Only process truly unknown skills
- Example: 19,214 raw skills → 15,000 already known → 4,214 unknown skills to process

**2. Chunking** (No LLM - Pure Python)
- Split unknown skills into chunks of 50-100 skills each
- **Why chunk?** Prevents LLM from getting lazy or cutting off responses
- **Chunk size**: 50-100 skills per call (optimal for complete responses)
- Example: 4,214 unknown skills → ~50-85 chunks

**3. Chunked LLM Normalization** (50-85 LLM calls per job_role)
- For each chunk, pass existing canonical skills + new chunk
- LLM maps each raw skill to canonical skill or creates new one
- **Prompt ensures**: LLM MUST return complete JSON for all skills in chunk
- **Output**: JSON dictionary mapping raw_skill → canonical_skill
- Example: `{"ReactJS v18": "React", ".NET 8": ".NET", "SomeWeirdTool": "SomeWeirdTool"}`

**4. Database Merge** (No LLM - Pure SQL)
- Insert new canonical skills into `canonical_skills` table
- Insert all mappings into `skill_aliases` table
- Track which skills are new vs. existing

**5. LLM Classification** (7 LLM calls - One per job_role)
- After normalization, classify all canonical skills for each job_role
- **Tier 1**: Technical, Business/Ops, Soft Skills
- **Tier 2**: Programming Languages, Frameworks, Cloud & Infrastructure, etc.
- **Skill Type**: Tool, Concept, Certification, Other
- Classifications cached and reused across all contexts

**6. Frequency Calculation** (No LLM - Pure Math)
- Calculates market demand within each 4D context
- Raw frequency: Count of unique jobs mentioning skill
- Normalized frequency: `unique_jobs / total_jobs_in_context` (0.0-1.0)
- Varies by context (same skill has different frequencies in different contexts)

**7. Importance Assignment** (No LLM - Simple Logic)
- Based on normalized frequency within context
- **Must-have**: >60% of jobs in context
- **Nice-to-have**: 30-60% of jobs in context
- **Preferred**: <30% of jobs in context
- Varies by context (same skill can be Must-have in one context, Preferred in another)

### Key Features

✅ **Efficient LLM Usage** - Only 7 LLM calls total (one per job_role), classifications cached and reused
✅ **Batch Processing** - Processes all skills for a role in one LLM call (cost-efficient)
✅ **Taxonomy-Based Classification** - Predefined skill categories with fallback keyword matching
✅ **Unique Job Tracking** - Counts unique jobs per skill (not total occurrences)
✅ **No Fallback** - Fails loudly when LLM classification fails (ensures quality)
✅ **Evidence Preservation** - Maintains original evidence snippets from Phase 1
✅ **Context-Aware Frequencies** - Same skill has different importance in different contexts
✅ **Fast Processing** - Most operations are pure math/SQL (no LLM needed)

## Database Schema

### New Tables

```sql
-- Normalized skill groups (4D context-aware)
CREATE TABLE normalized_skills (
    id SERIAL PRIMARY KEY,
    canonical_skill_id INTEGER REFERENCES canonical_skills(id),
    job_role TEXT NOT NULL,
    role_sub_cluster TEXT,  -- Can be NULL
    experience_level TEXT NOT NULL,
    cluster_type TEXT NOT NULL,
    job_count INTEGER,  -- Unique jobs in this context
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(canonical_skill_id, job_role, role_sub_cluster, experience_level, cluster_type)
);

-- Skill classifications (per job_role, cached and reused)
CREATE TABLE skill_classifications (
    id SERIAL PRIMARY KEY,
    canonical_skill_id INTEGER REFERENCES canonical_skills(id),
    job_role TEXT NOT NULL,
    tier1 TEXT NOT NULL,
    tier2 TEXT NOT NULL,
    skill_type TEXT,  -- Tool, Concept, Certification, Other
    experience_context TEXT,  -- "5+ years", "Expert", etc.
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(canonical_skill_id, job_role)
);

-- Market frequency data (4D context-aware)
CREATE TABLE skill_market_frequencies (
    id SERIAL PRIMARY KEY,
    canonical_skill_id INTEGER REFERENCES canonical_skills(id),
    job_role TEXT NOT NULL,
    role_sub_cluster TEXT,
    experience_level TEXT NOT NULL,
    cluster_type TEXT NOT NULL,
    raw_frequency INTEGER,  -- Total occurrences in context
    normalized_frequency FLOAT,  -- 0.0 to 1.0 within context
    unique_jobs INTEGER,  -- Number of unique jobs in context
    total_jobs_in_context INTEGER,  -- Total jobs in this context
    importance TEXT,  -- Must-have, Nice-to-have, Preferred
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(canonical_skill_id, job_role, role_sub_cluster, experience_level, cluster_type)
);
```

### Updates to Existing Tables

```sql
-- Update job_skills to reference canonical names
ALTER TABLE job_skills ADD COLUMN canonical_skill_id INTEGER REFERENCES canonical_skills(id);
ALTER TABLE job_skills ADD COLUMN normalization_context TEXT;  -- "AI Engineer > Computer Vision > Entry Level > specific"
```

### New Tables for Chunked Batch Architecture

```sql
-- Canonical skills (master list)
CREATE TABLE canonical_skills (
    id SERIAL PRIMARY KEY,
    canonical_name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Skill aliases (raw_skill → canonical_skill mappings)
CREATE TABLE skill_aliases (
    id SERIAL PRIMARY KEY,
    raw_skill TEXT UNIQUE NOT NULL,
    canonical_skill_id INTEGER REFERENCES canonical_skills(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for fast lookups
CREATE INDEX idx_skill_aliases_raw ON skill_aliases(raw_skill);
CREATE INDEX idx_skill_aliases_canonical ON skill_aliases(canonical_skill_id);
```

## Skill Taxonomy

The taxonomy provides a hierarchical category structure (tier1 and tier2) that the LLM uses to classify skills. The taxonomy defines the **category buckets**, not every individual skill.

### How It Works

1. **Taxonomy provides categories**: 24 tier2 categories across 3 tier1 categories
2. **LLM classifies skills**: For each skill, LLM decides which tier2 category it belongs to
3. **No pre-listing needed**: Skills don't need to be pre-defined in taxonomy
4. **Keyword fallback**: Taxonomy includes keyword-based fallback for edge cases

**Example:**
```
Skill: "LangChain"
LLM Decision: Technical / LLM & Generative AI
Reasoning: Framework for building LLM applications

Skill: "Next.js"
LLM Decision: Technical / Web Frameworks
Reasoning: React-based web framework
```

### Tier 1 Categories (3 total)

- **Technical**: Programming, frameworks, tools, infrastructure, AI/ML, data engineering
- **Business/Ops**: Project management, business analysis, product management, data analysis
- **Soft Skills**: Communication, leadership, problem solving, collaboration, adaptability

### Tier 2 Categories (24 total)

**Technical (18 categories):**
- Programming Languages
- Web Frameworks
- AI/ML Frameworks
- LLM & Generative AI
- Cloud & Infrastructure
- Databases & Data Storage
- Data Engineering & ETL
- Data Science & Analytics
- API & Integration
- Mobile Development
- DevOps & Automation
- Testing & QA
- Security & Blockchain
- Software Engineering
- Computer Science Fundamentals
- Specialized Domains
- Web Technologies
- Tools & Platforms

**Business/Ops (4 categories):**
- Project Management
- Business Analysis
- Data Analysis
- Product Management

**Soft Skills (6 categories):**
- Communication
- Leadership
- Problem Solving
- Collaboration
- Adaptability
- Work Ethic

### Category Coverage

These 24 tier2 categories are broad enough to classify any skill:
- **LangChain** → Technical / LLM & Generative AI
- **Next.js** → Technical / Web Frameworks
- **Kafka** → Technical / Data Engineering & ETL
- **A/B Testing** → Business/Ops / Data Analysis
- **Leadership** → Soft Skills / Leadership

The taxonomy also includes keyword-based fallback logic for skills not explicitly listed, ensuring 100% classification coverage.

### Why This Approach?

**Scalability**: New skills (e.g., future AI frameworks) automatically classified without updating taxonomy

**Flexibility**: LLM adapts to context and handles variations/synonyms

**Simplicity**: 24 categories vs. 389+ individual skills to maintain

**Consistency**: Same category structure across all job roles

## Processing Strategy

### Step 1: Pre-Filter (Deduplication)

```python
# Load all raw skills
raw_skills = db.query("""
    SELECT DISTINCT skill_name 
    FROM job_skills
""")

# Check against existing aliases
existing_aliases = db.query("""
    SELECT raw_skill 
    FROM skill_aliases
""")

# Find unknown skills
unknown_skills = set(raw_skills) - set(existing_aliases)
print(f"Total raw skills: {len(raw_skills)}")
print(f"Already known: {len(existing_aliases)}")
print(f"Unknown skills to process: {len(unknown_skills)}")
```

### Step 2: Chunking

```python
# Split unknown skills into chunks of 50-100
CHUNK_SIZE = 75  # Optimal for complete LLM responses
chunks = [list(unknown_skills)[i:i+CHUNK_SIZE] for i in range(0, len(unknown_skills), CHUNK_SIZE)]
print(f"Created {len(chunks)} chunks")
```

### Step 3: Chunked LLM Normalization

```python
# Get existing canonical skills
canonical_skills = db.query("""
    SELECT canonical_name 
    FROM canonical_skills
""")

for chunk_idx, chunk in enumerate(chunks):
    print(f"Processing chunk {chunk_idx+1}/{len(chunks)}")
    
    # Build prompt
    prompt = f"""Here is our current master list of Canonical Skills:
{json.dumps(canonical_skills, indent=2)}

Here are {len(chunk)} new raw skills scraped from job postings:
{json.dumps(chunk, indent=2)}

Your task: Map every single new raw skill to an existing Canonical Skill. 
If a raw skill absolutely does not fit, invent a clean, generic Canonical Skill for it.

You MUST return a complete JSON dictionary containing exactly {len(chunk)} keys, formatted like this:
{{"raw_skill_1": "Canonical_Skill", "raw_skill_2": "New_Canonical_Skill"}}

CRITICAL: Return ALL {len(chunk)} mappings. Do not skip any skills."""
    
    # Call LLM
    mappings = llm_client.generate_json(prompt)
    
    # Validate response
    if len(mappings) != len(chunk):
        raise Exception(f"LLM returned {len(mappings)} mappings, expected {len(chunk)}")
    
    # Insert new canonical skills
    for canonical in set(mappings.values()):
        db.execute("""
            INSERT INTO canonical_skills (canonical_name)
            VALUES (%s)
            ON CONFLICT (canonical_name) DO NOTHING
        """, [canonical])
    
    # Insert aliases
    for raw_skill, canonical in mappings.items():
        canonical_id = db.query("""
            SELECT id FROM canonical_skills WHERE canonical_name = %s
        """, [canonical])[0]['id']
        
        db.execute("""
            INSERT INTO skill_aliases (raw_skill, canonical_skill_id)
            VALUES (%s, %s)
            ON CONFLICT (raw_skill) DO NOTHING
        """, [raw_skill, canonical_id])
```

### Step 4: LLM Classification (per job_role)

```python
# Get all job roles
job_roles = db.query("""
    SELECT DISTINCT job_role 
    FROM job_classifications
""")

for job_role in job_roles:
    print(f"Classifying skills for {job_role}")
    
    # Get all canonical skills for this role
    canonical_skills = db.query("""
        SELECT DISTINCT cs.id, cs.canonical_name
        FROM canonical_skills cs
        JOIN skill_aliases sa ON sa.canonical_skill_id = cs.id
        JOIN job_skills js ON js.skill_name = sa.raw_skill
        JOIN job_classifications jc ON jc.url = js.url
        WHERE jc.job_role = %s
    """, [job_role])
    
    # LLM Classification
    # LLM decides which tier2 category each skill belongs to
    # Taxonomy provides the category structure (24 tier2 categories)
    classifications = classify_skills_with_llm(canonical_skills, job_role)
    
    # Insert classifications
    for skill_id, classification in classifications.items():
        db.execute("""
            INSERT INTO skill_classifications 
            (canonical_skill_id, job_role, tier1, tier2, skill_type, experience_context)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (canonical_skill_id, job_role) DO UPDATE SET
                tier1 = EXCLUDED.tier1,
                tier2 = EXCLUDED.tier2,
                skill_type = EXCLUDED.skill_type,
                experience_context = EXCLUDED.experience_context
        """, [skill_id, job_role, classification['tier1'], classification['tier2'], 
              classification['skill_type'], classification['experience_context']])
```

### Step 5: Process 4D Contexts (Math - No LLM)

```python
# Get all unique 4D contexts
contexts = db.query("""
    SELECT DISTINCT 
        jc.job_role,
        jc.role_sub_cluster,
        jc.experience_level,
        jc.cluster_type,
        COUNT(DISTINCT jc.url) as total_jobs
    FROM job_classifications jc
    GROUP BY jc.job_role, jc.role_sub_cluster, jc.experience_level, jc.cluster_type
    HAVING COUNT(DISTINCT jc.url) >= 3
    ORDER BY jc.job_role, jc.role_sub_cluster, jc.experience_level, jc.cluster_type
""")

for context in contexts:
    # Calculate frequencies
    frequencies = db.query("""
        SELECT 
            cs.id as canonical_skill_id,
            cs.canonical_name,
            COUNT(DISTINCT jc.url) as unique_jobs,
            COUNT(DISTINCT jc.url)::float / %s as normalized_frequency
        FROM canonical_skills cs
        JOIN skill_aliases sa ON sa.canonical_skill_id = cs.id
        JOIN job_skills js ON js.skill_name = sa.raw_skill
        JOIN job_classifications jc ON jc.url = js.url
        WHERE jc.job_role = %s
        AND (jc.role_sub_cluster = %s OR (jc.role_sub_cluster IS NULL AND %s IS NULL))
        AND jc.experience_level = %s
        AND jc.cluster_type = %s
        GROUP BY cs.id, cs.canonical_name
    """, [context['total_jobs'], context['job_role'], context['role_sub_cluster'], 
          context['role_sub_cluster'], context['experience_level'], context['cluster_type']])
    
    # Assign importance and write to database
    for freq in frequencies:
        if freq['normalized_frequency'] > 0.6:
            importance = "Must-have"
        elif freq['normalized_frequency'] >= 0.3:
            importance = "Nice-to-have"
        else:
            importance = "Preferred"
        
        db.execute("""
            INSERT INTO skill_market_frequencies 
            (canonical_skill_id, job_role, role_sub_cluster, experience_level, cluster_type,
             raw_frequency, normalized_frequency, unique_jobs, total_jobs_in_context, importance)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (canonical_skill_id, job_role, role_sub_cluster, experience_level, cluster_type)
            DO UPDATE SET
                raw_frequency = EXCLUDED.raw_frequency,
                normalized_frequency = EXCLUDED.normalized_frequency,
                unique_jobs = EXCLUDED.unique_jobs,
                total_jobs_in_context = EXCLUDED.total_jobs_in_context,
                importance = EXCLUDED.importance
        """, [freq['canonical_skill_id'], context['job_role'], context['role_sub_cluster'],
              context['experience_level'], context['cluster_type'], freq['unique_jobs'],
              freq['normalized_frequency'], freq['unique_jobs'], context['total_jobs'], importance])
```

### LLM Normalization Prompt (Step 3 - Chunked)

```python
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
```

### LLM Classification Prompt (Step 4 - Per Role)

```python
prompt = f"""You are classifying skills for {job_role} roles.

IMPORTANT: Classification is about WHAT the skill IS, not how important it is.
- "Python" is always a "Programming Language" regardless of experience level
- "Leadership" is always a "Soft Skill" regardless of sub-cluster

Available Tier2 Categories:

Technical:
- Programming Languages, Web Frameworks, AI/ML Frameworks, LLM & Generative AI
- Cloud & Infrastructure, Databases & Data Storage, Data Engineering & ETL
- Data Science & Analytics, API & Integration, Mobile Development
- DevOps & Automation, Testing & QA, Security & Blockchain
- Software Engineering, Computer Science Fundamentals, Specialized Domains
- Web Technologies, Tools & Platforms

Business/Ops:
- Project Management, Business Analysis, Data Analysis, Product Management

Soft Skills:
- Communication, Leadership, Problem Solving, Collaboration, Adaptability, Work Ethic

Skills to classify for {job_role}:
{skills_json}

For each skill, provide:
1. **tier1** and **tier2** from the categories above (must be valid combination)
2. **skill_type**: Tool, Concept, Certification, or Other
3. **experience_context**: Extract any experience level if mentioned (e.g., "5+ years", "Expert")

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

CRITICAL: You must classify ALL {len(skills)} skills. Choose the most appropriate tier2 category for each skill.
"""
```

**Note**: The LLM decides which tier2 category each skill belongs to. The taxonomy provides the category structure, not a pre-defined list of skills.

## Expected Results

- **Input**: 19,214 raw skills across 1,980 jobs
- **After Pre-Filter**: ~4,000-6,000 unknown skills (rest already in database)
- **Chunking**: ~50-85 chunks per job_role (75 skills per chunk)
- **LLM Calls**: 
  - Normalization: ~350-600 calls total (~50-85 per role × 7 roles)
  - Classification: 7 calls (one per job_role)
  - **Total**: ~360-610 LLM calls
- **Output**: ~10,000-15,000 canonical skills with context-aware frequencies
- **Processing Time**: ~30-60 minutes total
- **Cost**: ~$5-10 (chunked normalization + classification)
- **Reduction**: ~40-50% reduction in unique skills through normalization

### Performance Breakdown

**Step 1: Pre-Filter** (SQL)
- Time: <1 second
- Cost: $0

**Step 2: Chunking** (Python)
- Time: <1 second
- Cost: $0

**Step 3: Chunked LLM Normalization** (LLM)
- Time: ~20-40 minutes (~350-600 API calls)
- Cost: ~$4-9
- Calls: ~50-85 per role × 7 roles

**Step 4: LLM Classification** (LLM)
- Time: ~1-2 minutes (7 API calls)
- Cost: ~$0.50-1.00
- Calls: 7 (one per job_role)

**Step 5: Process 4D Contexts** (Math/SQL)
- Time: ~5-10 minutes (186 contexts)
- Cost: $0 (no LLM, pure math)
- Operations: Frequency calculation, importance assignment, database writes

### Future Runs (Incremental)

After initial run, subsequent batches are much faster:
- Pre-filter eliminates most skills (already in database)
- Only process truly new skills
- Example: 500 new jobs → 100 unknown skills → 2 chunks → ~14 LLM calls total

## Key Files

| File | Purpose |
|------|---------|
| `README.md` | This file - Phase 2 documentation |
| `batch_normalize_skills.py` | Main entry point for normalization |
| `skill_normalizer.py` | Normalization logic |
| `taxonomy.py` | Skill taxonomy (from MP3) |
| `gemini_client.py` | Reuse from phase_1 |
| `config.py` | Phase 2 configuration |
| `models.py` | Data models |

## Usage

```bash
cd Processing_Pipeline/phase_2
python batch_normalize_skills.py
```

## Benefits

1. **Prevents LLM Laziness**: Chunking ensures complete responses (no cutoffs or skipped skills)
2. **Incremental Processing**: Pre-filter eliminates already-known skills, only process new ones
3. **Future-Proof**: Subsequent batches are much faster (most skills already normalized)
4. **Context-Aware Frequencies**: Same skill has different importance in different contexts
5. **Market Intelligence**: Frequency-based importance reflects real demand per context
6. **Career Pathways**: Track skill evolution across experience levels
7. **Targeted Matching**: Match candidates to jobs based on context-specific skills
8. **Quality-First**: Validation ensures LLM returns complete mappings
9. **Scalable**: Works for initial 20K skills and future incremental batches

## Next Steps

After Phase 2 completion:
- Phase 3: Advanced Analytics (skill demand trends, co-occurrence patterns, career pathways)
- Integration with MP3 Career Analysis System for resume matching
