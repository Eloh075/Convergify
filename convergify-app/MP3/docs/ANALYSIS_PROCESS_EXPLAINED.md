# Career Analysis Process - Step by Step

This document explains how the system analyzes your resume against job postings to generate career insights.

---

## Overview

**Input:** Your resume + Multiple job postings  
**Output:** Match score, skill gaps, recommendations, market insights

**Process:** 10 steps that transform raw text into actionable career advice

---

## Step 1: Load Your Data

### What Goes In
- Your resume (PDF or text file)
- Job postings you're interested in (10 jobs in this example)

### What Comes Out
- Resume text extracted and cleaned
- Job descriptions extracted and cleaned
- Each job has: title, company, location, description

### Example
```
Resume: "Software engineer with 3 years experience in Python..."
Job 1: "AI Engineer at DHL - requires Python, Machine Learning..."
Job 2: "Staff AI Engineer at OKBL - requires Blockchain, AI Agents..."
...
Job 10: "Business+AI Consultant - requires Consulting, AI..."
```

---

## Step 2: Extract Skills from Jobs

### What Goes In
- 10 job descriptions (raw text)

### What Happens
- System reads each job description
- Identifies technical skills (Python, Machine Learning, etc.)
- Identifies soft skills (Leadership, Communication, etc.)
- Identifies domain skills (AI, Blockchain, etc.)

### What Comes Out
- Job 1: 17 skills extracted
- Job 2: 11 skills extracted
- Job 3: 11 skills extracted
- ...
- Job 10: 7 skills extracted

### Example
```
Job 1 (AI Engineer at DHL):
- Machine Learning
- Generative AI
- AI Architecture
- MLOps
- Python
- ... (12 more)
```

**Note:** Skills are cached - if we've seen this job before, we reuse the extracted skills to save time.

---

## Step 3: Classify Skills into Categories

### What Goes In
- All extracted skills from all jobs (116 total skills in this example)

### What Happens
- Each skill gets classified into categories:
  - **Tier 1:** Technical / Soft / Domain
  - **Tier 2:** Programming / Cloud / Leadership / etc.
- Each skill gets an importance level based on frequency:
  - **Must-have:** Appears in 60%+ of jobs
  - **Nice-to-have:** Appears in 30-60% of jobs
  - **Preferred:** Appears in <30% of jobs

### What Comes Out
- Classified skills with categories and importance
- Market frequency for each skill (0.0 to 1.0)

### Example
```
Python:
- Tier 1: Technical
- Tier 2: Programming Languages
- Frequency: 6/10 jobs = 0.6 (60%)
- Importance: Must-have

Blockchain Data Analysis:
- Tier 1: Technical
- Tier 2: Data & Analytics
- Frequency: 1/10 jobs = 0.1 (10%)
- Importance: Preferred
```

---

## Step 4: Semantic Matching + Canonical Grouping (Single LLM Call)

### What Goes In
- Your resume text
- All 116 classified skills from all jobs
- Market frequencies

### What Happens (Two Tasks in One LLM Call)

**Task 1: Semantic Skill Matching**
- For each required skill, system checks:
  - **Does your resume mention this skill?** (semantic, not keyword)
  - **How strongly does it match?** (confidence 0-100%)
  - **What type of match?** (Exact / Semantic / Substitution / None)
  - **Where is the evidence?** (specific text from resume)

**Task 2: Canonical Grouping**
- Group related skills under canonical parent names
- Examples:
  - "AI", "Generative AI", "Machine Learning", "Deep Learning" → "Artificial Intelligence & Machine Learning"
  - "React.js", "ReactJS", "React Native" → "React"
  - "Python", "Python 3", "Python Programming" → "Python"
- Calculate aggregated demand across all child skills
- Track which specific children were mentioned in which jobs

### What Comes Out

**Skill Matches (116 total):**
- Strong Match: 31 skills (clear evidence, 80-100% confidence)
- Partial Match: 25 skills (some evidence, 50-80% confidence)
- Missing: 60 skills (no evidence, <50% confidence)

**Canonical Groups (9 groups):**
```
1. Artificial Intelligence & Machine Learning
   - Demand: 100% (10/10 jobs)
   - Children: 25 skills
     • PyTorch: 2 mentions
     • Machine Learning: 2 mentions
     • Reinforcement Learning: 2 mentions
     • Computer Vision: 1 mention
     • ... 21 more

2. Programming Languages
   - Demand: 100% (10/10 jobs)
   - Children: 5 skills
     • Python: 6 mentions
     • TypeScript: 1 mention
     • Java: 1 mention
     • C++: 1 mention
     • Go: 1 mention

3. Cloud & DevOps
   - Demand: 100% (10/10 jobs)
   - Children: 13 skills
     • MLOps: 2 mentions
     • Azure: 2 mentions
     • GCP: 1 mention
     • ... 10 more
```

### Why This Matters

**Before Canonical Grouping:**
- "Artificial Intelligence (AI)": 10% demand (1/10 jobs)
- "Generative AI": 10% demand (1/10 jobs)
- "Machine Learning": 20% demand (2/10 jobs)
- Each AI skill counted separately

**After Canonical Grouping:**
- "Artificial Intelligence & Machine Learning": 100% demand (10/10 jobs)
- All AI-related skills aggregated under one parent
- More accurate representation of market demand

**Performance Benefit:**
- Single LLM call does both tasks (no additional API cost)
- Results cached in database for future analyses
- 38+ common mappings pre-seeded (AI/ML, React, Node.js, cloud platforms)

### Example Match
```
Python:
- Status: Strong Match
- Match Type: Exact
- Confidence: 95%
- Evidence: "5 years of Python development", "Built ML pipelines using Python"
- Resume mentions: 3 times
- Job mentions: 6 jobs
- Canonical group: "Programming Languages"

Blockchain Data Analysis:
- Status: Missing
- Match Type: None
- Confidence: 0%
- Evidence: None found
- Resume mentions: 0
- Job mentions: 1 job
- Canonical group: "Data & Analytics"
```

---

## Step 5: Extract Evidence from Resume

### What Goes In
- Your resume text
- Matched skills from Step 4

### What Happens
- For each matched skill, extract:
  - **Text snippets:** Specific sentences mentioning the skill
  - **Origin locations:** Where in resume (Experience, Skills, Projects, etc.)
  - **Timeline:** When skill was used (if dates available)
  - **Confidence:** How strong is the evidence (0-100%)

### What Comes Out
- Evidence objects for each skill match
- Reconciled confidence scores (LLM confidence + evidence confidence)

### Example
```
Python Evidence:
- Found: Yes
- Snippets: 
  • "5 years of Python development building ML pipelines"
  • "Developed REST APIs using Python and FastAPI"
- Locations: Experience, Skills
- Timeline: 2018-2023
- Confidence: 95%

Machine Learning Evidence:
- Found: Yes
- Snippets:
  • "Built predictive models using TensorFlow"
- Locations: Experience
- Timeline: 2020-2023
- Confidence: 75%
```

---

## Step 6: Calculate Overall Match Score

### What Goes In
- All skill matches with their confidence scores
- Market frequencies (how important each skill is)

### What Happens
- Weight each skill by its market frequency
- Strong matches contribute more to score
- Missing must-have skills hurt score more
- Formula: Weighted average of all skill confidences

### What Comes Out
- Overall match score: 38.2% (in this example)
- Breakdown:
  - Strong matches: 31 skills
  - Partial matches: 25 skills
  - Missing skills: 60 skills

### Example
```
Calculation:
- Python (60% frequency, 95% match) → contributes heavily
- Machine Learning (20% frequency, 75% match) → contributes moderately
- Blockchain (10% frequency, 0% match) → contributes nothing

Overall: 38.2% match
```

---

## Step 7: Identify Skill Gaps

### What Goes In
- All missing skills
- Their importance levels
- Their market frequencies

### What Happens
- Filter to only missing skills
- Calculate priority score for each:
  - Priority = (Importance × 0.6) + (Market Demand × 0.4)
- Sort by priority (highest first)

### What Comes Out
- Prioritized list of 60 skill gaps
- Each gap shows:
  - Skill name
  - Importance (Must-have / Nice-to-have / Preferred)
  - Market demand (0-100%)
  - Priority score (calculated)
  - Reasoning

### Example
```
Top Skill Gaps:

1. PyTorch
   - Importance: Must-have
   - Market Demand: 20% (2/10 jobs)
   - Priority Score: 0.8
   - Reasoning: "Must-have skill appearing in 20% of jobs"

2. LangGraph
   - Importance: Nice-to-have
   - Market Demand: 30% (3/10 jobs)
   - Priority Score: 0.72
   - Reasoning: "Nice-to-have skill appearing in 30% of jobs"
```

---

## Step 8: Generate Market Insights

### What Goes In
- All classified skills
- Job counts for each skill
- Your match results

### What Happens
- Identify top 10 most in-demand skills using canonical groups
- Calculate competition level based on your match score:
  - High competition: <50% match
  - Medium competition: 50-75% match
  - Low competition: >75% match
- Separate must-have vs nice-to-have skills
- Track child skill breakdown for each canonical group

### What Comes Out
- Market insights report:
  - Top skills in demand (sorted by frequency)
  - Competition level
  - Must-have skills list
  - Nice-to-have skills list

### Example
```
Market Insights:

Top Skills (Using Canonical Groups):
1. Artificial Intelligence & Machine Learning
   - Demand: 100% (10/10 jobs)
   - Children: 25 skills
     • PyTorch: 2 mentions
     • Machine Learning: 2 mentions
     • Reinforcement Learning: 2 mentions
     • ... 22 more

2. Programming Languages
   - Demand: 100% (10/10 jobs)
   - Children: 5 skills
     • Python: 6 mentions
     • TypeScript: 1 mention
     • ... 3 more

3. Cloud & DevOps
   - Demand: 100% (10/10 jobs)
   - Children: 13 skills
     • MLOps: 2 mentions
     • Azure: 2 mentions
     • ... 11 more

Competition: High (you have 38.2% match)

Must-have skills: (none - all skills appear in <60% of jobs individually)
Nice-to-have: LangGraph, Communication Skills, MLOps
```

---

## Step 9: Generate Recommendations

### What Goes In
- Your skill gaps
- Your skill matches
- Market insights
- Your overall match score

### What Happens
- Analyze your profile to identify:
  - **Immediate actions:** Skills to learn first
  - **Career paths:** Roles you can target
  - **Strengths to leverage:** Skills you already have
  - **Timeline:** How long to reach goals

### What Comes Out
- Actionable recommendations with:
  - Priority level (High / Medium / Low)
  - Category (Skill Development / Career Strategy / etc.)
  - Specific action items
  - Evidence references

### Example
```
Recommendation 1: Strengthen Core AI Skills
Priority: High
Category: Skill Development

Description:
Focus on building foundational AI skills that appear across multiple job postings.

Action Items:
- Complete online course in Machine Learning fundamentals
- Build 2-3 AI projects for portfolio
- Get hands-on with LangChain and AI Agents
- Practice with real datasets

Recommendation 2: Target Entry-Level AI Roles
Priority: High
Category: Career Strategy

Description:
Your current skill set aligns best with junior AI positions.

Action Items:
- Apply to AI Engineer roles at startups
- Highlight Python and development experience
- Build AI portfolio to demonstrate capability
- Network with AI professionals
```

---

## Step 10: Create Optimized Resume

### What Goes In
- Your original resume
- Analysis results (gaps, matches, recommendations)
- Job requirements

### What Happens
- Identify sections to strengthen
- Suggest keyword additions
- Recommend experience highlighting
- Validate changes don't break resume structure

### What Comes Out
- Optimized resume with tracked changes
- Change count: 0 (in this example - no changes made)
- Validation status: Passed

---

## Data Flow Summary

```
Your Resume + 10 Jobs
    ↓
[Extract Skills] → 116 raw skills from all jobs
    ↓
[Classify Skills] → Skills categorized with importance levels
    ↓
[Semantic Match + Canonical Group] → Single LLM call:
    • 116 skill matches (31 strong, 25 partial, 60 missing)
    • 9 canonical groups with aggregated frequencies
    • Cached to database for future analyses
    ↓
[Extract Evidence] → Find proof in resume for each match
    ↓
[Calculate Score] → 38.2% overall match
    ↓
[Identify Gaps] → 60 prioritized skill gaps
    ↓
[Market Insights] → Top skills by canonical groups
    ↓
[Recommendations] → Actionable next steps
    ↓
[Optimize Resume] → Suggested improvements
```

---

## Key Metrics Explained

### Overall Match Score (38.2%)
- **What it means:** You match 38.2% of the requirements across all 10 jobs
- **How it's calculated:** Weighted average of all skill matches by importance
- **What's good:** 70%+ is strong, 50-70% is moderate, <50% needs work

### Skill Gaps (60 identified)
- **What it means:** 60 skills required by jobs that you don't have
- **How they're prioritized:** By (importance × 3.0) + (market demand × 1.0)
- **What to do:** Focus on top 5-10 gaps with highest priority scores

### Skill Matches (116 found)
- **What it means:** 116 skills from jobs that you have some level of match with
- **Strong matches (31):** Skills you clearly demonstrate with evidence
- **Partial matches (25):** Skills you somewhat demonstrate
- **Missing (60):** Skills you don't demonstrate

### Canonical Groups (9 created)
- **What it means:** Related skills grouped under parent names
- **Example:** "AI", "Machine Learning", "Deep Learning" → "Artificial Intelligence & Machine Learning"
- **Why it matters:** Shows true market demand (100% vs 10% for AI skills)
- **Cached:** Mappings saved to database for faster future analyses

### Market Demand (0-100%)
- **What it means:** Percentage of jobs requiring this skill
- **Example:** 60% = 6 out of 10 jobs need this skill
- **What's important:** Focus on skills with >30% demand

### Importance Level
- **Must-have (100%):** Critical for the role, appears in 60%+ jobs
- **Nice-to-have (70%):** Valuable but not critical, 30-60% jobs
- **Preferred (40%):** Bonus skill, <30% jobs

---

## Performance Stats

### Caching Strategy

**Skill Extraction Cache:**
- **Location:** `jobs.classified_skills` column in database
- **Cached Jobs:** 0/10 (first time analyzing these jobs)
- **Cache Hit Rate:** 0%
- **Benefit:** Next analysis with same jobs will skip extraction step

**Canonical Mapping Cache:**
- **Location:** `skill_canonical_cache` table in database
- **Pre-seeded:** 38+ common mappings (AI/ML, React, Node.js, cloud platforms)
- **Auto-learning:** New mappings added automatically during analysis
- **Benefit:** Reduces LLM calls for canonical grouping

**What this means:** 
- First analysis: ~3-5 minutes (extracts skills + creates canonical mappings)
- Subsequent analyses: ~2-3 minutes (uses cached skills + cached mappings)
- Cache grows smarter with each analysis

---

## Time Breakdown

Typical analysis with 10 jobs takes **3-5 minutes**:

1. **Load data:** 5 seconds
2. **Extract skills:** 60-90 seconds (cached after first time)
3. **Classify skills:** 30-60 seconds
4. **Semantic match + Canonical group:** 90-120 seconds (single LLM call)
   - Matches 116 skills semantically
   - Groups related skills into 9 canonical parents
   - Caches canonical mappings to database
5. **Extract evidence:** 20-30 seconds
6. **Calculate scores:** 5 seconds
7. **Generate insights:** 10 seconds
8. **Create recommendations:** 20-30 seconds
9. **Optimize resume:** 20-30 seconds

**Total:** ~3-5 minutes for comprehensive analysis

**Performance Notes:**
- Skill extraction cached per job (60-90s → 0s on repeat)
- Canonical mappings cached globally (reduces future LLM calls)
- Single LLM call for matching + grouping (no additional API cost)
- Gemini 2.5 Flash used for large outputs (65K tokens vs 8K)

---

## What Makes This Analysis Accurate?

### 1. Semantic Understanding (Not Keyword Matching)
- Doesn't just match keywords
- Understands "Python developer" matches "Python programming"
- Recognizes "built ML models" as evidence of "Machine Learning"
- Uses LLM to understand context and meaning

### 2. Canonical Skill Grouping
- Groups related skills under parent names
- "AI", "Generative AI", "Machine Learning" → "Artificial Intelligence & Machine Learning"
- Shows true market demand (100% vs 10%)
- Preserves granularity with child skill breakdown

### 3. Evidence-Based Matching
- Every match requires evidence from your resume
- Shows specific text snippets as proof
- Confidence scores reflect evidence strength
- Reconciles LLM confidence with evidence confidence

### 4. Market-Weighted Scoring
- Skills appearing in more jobs count more
- Must-have skills weighted 3x higher than preferred
- Reflects real market demand and importance
- Priority scores guide learning path

### 5. Database Caching
- Skill extraction cached per job
- Canonical mappings cached globally
- 38+ common mappings pre-seeded
- Cache grows smarter with each analysis

### 6. Context-Aware Analysis
- Considers job titles and descriptions
- Understands industry-specific terminology
- Adapts to different career levels
- Provides role-specific recommendations

---

*This analysis process is designed to give you actionable insights for your job search and career development.*
