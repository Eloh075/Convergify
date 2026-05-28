# Analysis Database Structure & Frontend Integration

## Overview

This document explains how analysis results are structured in the database, how they flow to the frontend, and what data is available for the redesigned Analysis Results page.

---

## Database Structure

### 1. Analysis Table (`analyses`)

**Primary storage for analysis metadata and results**

```sql
CREATE TABLE analyses (
    id VARCHAR PRIMARY KEY,                    -- UUID
    resume_id VARCHAR NOT NULL,                -- FK to resumes.id
    job_ids TEXT NOT NULL,                     -- JSON array of job IDs
    analysis_type VARCHAR DEFAULT 'comprehensive',  -- 'comprehensive', 'single_job', 'market_intelligence'
    status VARCHAR DEFAULT 'pending',          -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    task_id VARCHAR,                           -- Celery task ID for tracking
    created_at DATETIME,                       -- When analysis was created
    start_date DATETIME,                       -- Legacy field (kept for compatibility)
    started_at DATETIME,                       -- When processing actually started
    completion_date DATETIME,                  -- When analysis completed
    results TEXT,                              -- JSON object with ALL analysis data
    error_message TEXT,                        -- Error details if failed
    optimized_resume_id VARCHAR,               -- FK to optimized_resumes.id
    FOREIGN KEY (resume_id) REFERENCES resumes(id),
    FOREIGN KEY (optimized_resume_id) REFERENCES optimized_resumes(id)
);
```

**Key Properties:**
- `job_ids_list`: Property that parses JSON array to Python list
- `results_dict`: Property that parses JSON results to Python dict
- `duration`: Calculated property (completion_date - start_date)
- `is_completed`: Boolean check if status == 'completed'
- `job_count`: Number of jobs analyzed

---

## Results JSON Structure

The `results` column contains a comprehensive JSON object with ALL analysis data:

```json
{
  "overall_match_score": 38.2,
  "category_scores": {
    "Must-have": 45.0,
    "Nice-to-have": 35.0,
    "Preferred": 30.0
  },
  "skill_matches": [
    {
      "skill_name": "Python",
      "canonical_name": "Python",
      "match_status": "Strong Match",
      "match_type": "Exact",
      "confidence_score": 0.95,
      "evidence": {
        "found": true,
        "text_snippets": ["5 years of Python development"],
        "origin_locations": ["Experience"],
        "timeline": "2018-2023",
        "confidence": 0.95
      },
      "substitution_reasoning": null,
      "importance": "Must-have",
      "market_frequency": 0.6
    }
  ],
  "recommendations": [
    {
      "priority": "High",
      "category": "Skill Development",
      "title": "Learn Machine Learning Frameworks",
      "description": "Focus on PyTorch and TensorFlow...",
      "action_items": [
        "Complete PyTorch tutorial",
        "Build 2-3 ML projects"
      ],
      "evidence_references": []
    }
  ],
  "summary": {
    "total_skills_required": 116,
    "strong_matches": 31,
    "partial_matches": 25,
    "missing_skills": 60,
    "overall_readiness": "Needs Development"
  },
  "market_insights": {
    "total_jobs_analyzed": 10,
    "top_skills_by_demand": [
      {
        "skill": "Artificial Intelligence & Machine Learning",
        "demand_score": 1.0,
        "job_count": 10,
        "child_skills": {
          "PyTorch": 2,
          "Machine Learning": 2,
          "Computer Vision": 1
        },
        "growth_trend": "stable",
        "importance": "Must-have"
      }
    ],
    "must_have_skills": ["Python", "Machine Learning"],
    "nice_to_have_skills": ["Docker", "Kubernetes"],
    "competition_level": "High",
    "skill_trends": {}
  },
  "top_skills": [
    {
      "skill_name": "Artificial Intelligence & Machine Learning",
      "demand_percentage": 100.0,
      "job_count": 10,
      "growth_trend": "stable"
    }
  ],
  "skill_gaps_prioritized": [
    {
      "skill_name": "PyTorch",
      "importance": "Must-have",
      "market_frequency": 0.2,
      "priority_score": 0.8,
      "reasoning": "Critical skill appearing in 20% of jobs"
    }
  ],
  "canonical_groups": {
    "Artificial Intelligence & Machine Learning": {
      "canonical_name": "Artificial Intelligence & Machine Learning",
      "child_skills": ["AI", "Machine Learning", "Deep Learning", "PyTorch"],
      "child_frequencies": {
        "PyTorch": 2,
        "Machine Learning": 2,
        "Reinforcement Learning": 2
      },
      "total_job_mentions": 10,
      "aggregated_frequency": 1.0
    }
  }
}
```

---

## API Endpoints

### 1. Create Analysis
**POST** `/api/analyses/`

**Request:**
```json
{
  "resume_id": "uuid",
  "job_ids": ["uuid1", "uuid2"],
  "analysis_type": "comprehensive"
}
```

**Response:**
```json
{
  "id": "uuid",
  "resume_id": "uuid",
  "job_ids": ["uuid1", "uuid2"],
  "status": "pending",
  "created_at": "2026-02-09T12:00:00",
  "message": "Analysis started in background"
}
```

### 2. Get Analysis Status
**GET** `/api/analyses/{analysis_id}/status`

**Response:**
```json
{
  "analysis_id": "uuid",
  "status": "running",
  "analysis_type": "comprehensive",
  "created_at": "2026-02-09T12:00:00",
  "started_at": "2026-02-09T12:00:05",
  "completed_at": null,
  "progress_percentage": 50,
  "stage": "semantic_matching",
  "current_status": "Matching skills...",
  "jobs_processed": 5,
  "total_jobs": 10,
  "has_results": false
}
```

### 3. Get Analysis Results
**GET** `/api/analyses/{analysis_id}/results`

**Response:** Full results JSON (see structure above)

### 4. Get Specific Data
- **GET** `/api/analyses/{analysis_id}/recommendations` - Just recommendations
- **GET** `/api/analyses/{analysis_id}/skill-gaps` - Just skill gaps
- **GET** `/api/analyses/{analysis_id}` - Full analysis metadata + results

---

## Frontend Integration

### Current Flow

1. **User triggers analysis** → `AnalysisLauncher.tsx`
   - Calls `POST /api/analyses/`
   - Receives analysis ID

2. **Poll for status** → `AnalysisProgressMonitor.tsx`
   - Calls `GET /api/analyses/{id}/status` every 2 seconds
   - Shows progress bar and current stage
   - Detects completion when `status === 'completed'`

3. **Load results** → `AnalysisResults.tsx`
   - Calls `GET /api/analyses/{id}/results`
   - Receives full results JSON
   - Renders tabs: Overview, Skill Gaps, Skill Matches, Market Insights, Recommendations, Career Paths

### Current Component Structure

```
AnalysisResults.tsx
├── Overview Tab
│   ├── Match Score (circular gauge)
│   ├── Category Scores (bar chart)
│   └── Summary Stats
├── Skill Gaps Tab
│   ├── Filters (search, category, sort)
│   ├── Gap Cards (with importance badges)
│   └── Learning Resources
├── Skill Matches Tab
│   ├── Strong Matches
│   ├── Partial Matches
│   └── Evidence Details
├── Market Insights Tab
│   ├── Top Skills by Demand
│   ├── Competition Level
│   └── Salary Insights
├── Recommendations Tab
│   ├── High Priority
│   ├── Medium Priority
│   └── Low Priority
└── Career Paths Tab
    └── Suggested Roles
```

---

## New Data Available for Redesign

### 1. Canonical Skill Groups
**Location:** `results.canonical_groups`

**What it provides:**
- Parent skill name (e.g., "Artificial Intelligence & Machine Learning")
- List of child skills (e.g., ["AI", "Machine Learning", "PyTorch"])
- Frequency of each child skill
- Total job mentions (aggregated)
- Aggregated demand percentage

**Use cases:**
- Show skill hierarchies in Market Insights
- Expandable skill cards showing variants
- Better understanding of skill relationships
- More accurate demand visualization

### 2. Enhanced Market Insights
**Location:** `results.market_insights.top_skills_by_demand`

**New fields:**
- `child_skills`: Dict of child skill frequencies
- `importance`: Skill importance level
- `demand_score`: Accurate aggregated demand (0-1)
- `job_count`: Number of jobs mentioning this skill

**Use cases:**
- Drill-down from parent to child skills
- Show "Python appears in 6/10 jobs as: Python (6), Python 3 (2)"
- Filter by importance level
- Sort by actual demand vs. importance

### 3. Skill Match Evidence
**Location:** `results.skill_matches[].evidence`

**Fields:**
- `found`: Boolean
- `text_snippets`: Array of relevant resume excerpts
- `origin_locations`: Where in resume (Experience, Skills, etc.)
- `timeline`: When skill was used
- `confidence`: Evidence confidence score

**Use cases:**
- Show proof of skills in resume
- Timeline visualization of skill usage
- Confidence-based filtering
- Evidence-based skill verification

### 4. Prioritized Skill Gaps
**Location:** `results.skill_gaps_prioritized`

**Fields:**
- `skill_name`: Skill to learn
- `importance`: Must-have/Nice-to-have/Preferred
- `market_frequency`: How common in market
- `priority_score`: Calculated priority (0-1)
- `reasoning`: Why this skill is important

**Use cases:**
- Smart learning path recommendations
- Priority-based skill gap visualization
- ROI calculation for learning each skill
- Personalized learning roadmap

### 5. Detailed Recommendations
**Location:** `results.recommendations`

**Fields:**
- `priority`: High/Medium/Low
- `category`: Skill Development/Resume Optimization/Application Strategy
- `title`: Short title
- `description`: Detailed explanation
- `action_items`: Specific steps to take
- `evidence_references`: Links to relevant data

**Use cases:**
- Actionable task list
- Category-based filtering
- Priority-based sorting
- Progress tracking

---

## Redesign Recommendations

### 1. Add Canonical Skill Visualization
**Current:** Skills listed flatly with individual percentages
**Proposed:** 
- Hierarchical skill cards
- Parent skill shows aggregated demand
- Expandable to show child skills
- Visual indicator of skill variants

**Example:**
```
┌─────────────────────────────────────────────┐
│ Artificial Intelligence & Machine Learning  │
│ 100% demand (10/10 jobs)                    │
│                                             │
│ ▼ Show 25 variants                          │
│   ├─ PyTorch: 2 mentions                    │
│   ├─ Machine Learning: 2 mentions           │
│   ├─ Reinforcement Learning: 2 mentions     │
│   └─ ... 22 more                            │
└─────────────────────────────────────────────┘
```

### 2. Add Evidence-Based Skill Verification
**Current:** Just shows "Strong Match" or "Partial Match"
**Proposed:**
- Show evidence snippets from resume
- Timeline of skill usage
- Confidence score visualization
- "Prove it" button to expand evidence

**Example:**
```
Python - Strong Match (95% confidence)
├─ Evidence from Experience:
│  "5 years of Python development building ML pipelines"
├─ Timeline: 2018-2023
└─ [View full evidence]
```

### 3. Add Smart Learning Path
**Current:** Flat list of skill gaps
**Proposed:**
- Priority-based learning roadmap
- Estimated time to learn
- ROI calculation (importance × market demand)
- Suggested learning order
- Progress tracking

**Example:**
```
Your Learning Path (12 weeks)
┌─────────────────────────────────────┐
│ Week 1-4: PyTorch (High Priority)  │
│ ROI: 8.5/10 | Demand: 20%          │
│ [Start Learning] [Mark Complete]    │
├─────────────────────────────────────┤
│ Week 5-8: Docker (Medium Priority) │
│ ROI: 6.2/10 | Demand: 15%          │
└─────────────────────────────────────┘
```

### 4. Add Market Intelligence Dashboard
**Current:** Simple list of top skills
**Proposed:**
- Demand trend visualization
- Competition heatmap
- Salary correlation
- Geographic demand
- Industry breakdown

### 5. Add Comparison View
**Current:** Single analysis view
**Proposed:**
- Compare multiple analyses
- Track progress over time
- Before/after resume optimization
- Skill gap reduction tracking

---

## Additional Data Needed for Redesign

### 1. Historical Data
**What:** Previous analyses for same resume
**Why:** Show progress over time, skill gap reduction
**How:** Query `analyses` table filtered by `resume_id`

### 2. Job Details
**What:** Full job information for analyzed jobs
**Why:** Show which jobs require which skills, drill-down capability
**How:** Join `analyses.job_ids` with `jobs` table

### 3. Learning Resources
**What:** Courses, tutorials, certifications for each skill
**Why:** Direct links to learning materials
**How:** External API or curated database

### 4. Salary Data
**What:** Salary ranges for skills and roles
**Why:** ROI calculation, career path planning
**How:** Aggregate from job postings or external API

### 5. Skill Relationships
**What:** Related skills, prerequisites, skill trees
**Why:** Suggest complementary skills, learning order
**How:** Graph database or predefined taxonomy

### 6. Resume Optimization Diff
**What:** Before/after comparison of resume
**Why:** Show what changed, impact of changes
**How:** Already available in `optimized_resumes` table

---

## Performance Considerations

### Current Issues
1. **Large JSON payload**: Full results can be 50KB+
2. **No pagination**: All skills loaded at once
3. **No caching**: Results fetched on every page load

### Recommendations
1. **Lazy loading**: Load tabs on-demand
2. **Pagination**: Paginate skill lists (20 per page)
3. **Client-side caching**: Cache results in React Query
4. **Compression**: Gzip API responses
5. **Selective loading**: Separate endpoints for each tab

---

## Frontend State Management

### Current Approach
- React Query for API calls
- Local state for filters/sorting
- No global state management

### Recommendations for Redesign
1. **Use React Query cache**: Avoid refetching
2. **Optimistic updates**: Update UI before API response
3. **Background refetch**: Refresh data periodically
4. **Error boundaries**: Graceful error handling
5. **Loading skeletons**: Better UX during loading

---

## Summary

### Available Data
✅ Canonical skill groups with child frequencies
✅ Evidence-based skill matching with confidence scores
✅ Prioritized skill gaps with reasoning
✅ Detailed recommendations with action items
✅ Market insights with aggregated demand
✅ Category scores and overall match score

### Missing Data (for enhanced redesign)
❌ Historical analysis data (progress tracking)
❌ Learning resources per skill
❌ Salary data per skill
❌ Skill relationship graph
❌ Geographic/industry breakdowns

### Redesign Priorities
1. **Canonical skill visualization** (data available)
2. **Evidence-based verification** (data available)
3. **Smart learning path** (data available)
4. **Market intelligence dashboard** (partial data)
5. **Comparison view** (needs historical data)
