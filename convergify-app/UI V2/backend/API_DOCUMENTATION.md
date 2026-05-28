# Backend API Documentation

## Overview
This document tracks all API endpoints for the UI V2 backend, including their purposes, request/response formats, dependencies, and frontend usage.

---

## Base URL
- **Development**: `http://localhost:54321/functions/v1`
- **Production**: `https://[project-ref].supabase.co/functions/v1`

---

## Shared Utilities

### Types (`_shared/types.ts`)
**Status**: ✅ Created

Defines TypeScript interfaces used across all Edge Functions:
- `MarketSkill` - Market skill data structure
- `AnalysisContext` - Role/specialty/experience context
- `GapAnalysisResult` - Gap analysis output format
- `AnalysisJob` - Analysis job status tracking
- `AnalysisResult` - Complete analysis result format

### Market Skills Helper (`_shared/market-skills.ts`)
**Status**: ✅ Created

**Function**: `getMarketSkills(supabaseUrl, supabaseKey, role, specialty, experienceLevels)`

**Purpose**: Retrieves and aggregates market skill data for given contexts

**Features**:
- Queries `skill_market_frequencies` for each experience level
- Aggregates frequencies across multiple levels
- Handles "Insufficient Data" by rolling up to parent contexts
- Returns sorted skills by frequency

### Gap Analysis Helper (`_shared/gap-analysis.ts`)
**Status**: ✅ Created

**Function**: `calculateGapAnalysis(resumeSkills, marketSkills)`

**Purpose**: Calculates match score and categorizes skill gaps

**Features**:
- Matches resume skills against market requirements (case-insensitive)
- Categorizes skills into Dealbreakers/Differentiators/Bonus
- Calculates match score based on Must-have skills only
- Returns detailed breakdown of matched vs gap skills

---

## Endpoints

### 1. GET /target-options

**Purpose**: Returns available roles, specialties, and experience levels for the target selection UI

**Status**: ✅ Created

**File Location**: `UI V2/backend/supabase/functions/target-options/index.ts`

**Request**:
```http
GET /target-options
```

**Response**:
```json
{
  "roles": [
    "AI Engineer",
    "Business Analyst",
    "Data Analyst",
    "Full Stack Developer",
    "Product Manager",
    "Software Engineer"
  ],
  "specialties": {
    "Software Engineer": ["Backend", "Frontend", "Generalist", "Systems"],
    "AI Engineer": ["Computer Vision", "Generalist", "Generative/NLP", "MLOps"],
    "Full Stack Developer": ["Enterprise", "JavaScript Ecosystem", "Python/Ruby"],
    "Business Analyst": ["Agile/Scrum", "IT/Systems", "Strategy/Operations"],
    "Data Analyst": ["Business Intelligence", "Marketing/Growth"],
    "Product Manager": ["Core/Feature", "Technical"]
  },
  "experience_levels": [
    "Associate",
    "Entry Level",
    "Internship",
    "Mid-Senior Level"
  ]
}
```

**Database Tables Used**:
- `skill_market_frequencies` (read)

**Frontend Usage**:
- `UI V2/frontend/src/app/components/JobDescriptionStep.tsx` - Populates role/specialty/experience dropdowns
- Called on component mount to populate target selection UI

**Dependencies**: 
- `exec_sql` RPC function (Supabase database function for executing raw SQL)

**Processing Steps**:
1. Execute three separate SQL queries via `exec_sql` RPC function:
   - Query 1: Get distinct roles filtered by `cluster_type = 'specific'`, ordered alphabetically
   - Query 2: Get distinct role-specialty pairs where specialty is not null, ordered by role and specialty
   - Query 3: Get distinct experience levels, ordered alphabetically
2. Build roles array from Query 1 results
3. Build specialties object by grouping Query 2 results by role
4. Build experience_levels array from Query 3 results
5. Return JSON response with roles, specialties, and experience_levels

**Notes**:
- ✅ Fully implemented with synchronous processing
- ✅ Uses raw SQL via `exec_sql` RPC for efficient distinct queries
- ✅ Uses SERVICE_ROLE_KEY for database access (changed from ANON_KEY)
- ✅ Filters for `cluster_type = 'specific'` to exclude generalist contexts
- ✅ Sorting done at database level (ORDER BY) for better performance
- ✅ Three separate queries for cleaner, more efficient data retrieval
- No authentication required (public endpoint)
- Fast response time (optimized SQL queries)

### 2. POST /analyze-job-posting

**Purpose**: Analyzes a specific job posting by extracting skills, classifying the job, and matching against market data

**Status**: ✅ Created (Mock LLM Integration)

**File Location**: `UI V2/backend/supabase/functions/analyze-job-posting/index.ts`

**Request**:
```json
{
  "job_title": "Senior AI Engineer",
  "company": "TechVault AI",
  "job_description": "Build and deploy cutting-edge ML models...",
  "resume_file": "base64_encoded_pdf"
}
```

**Response**:
```json
{
  "analysis_id": "uuid",
  "job_classification": {
    "role": "AI Engineer",
    "specialty": "Generative/NLP",
    "experience": "Mid-Senior Level",
    "confidence": 0.92
  },
  "job_match": {
    "score": 78,
    "matched_skills": ["Python", "PyTorch"],
    "missing_skills": ["Client Communication"]
  },
  "market_match": {
    "score": 85,
    "dealbreakers": { "matched": [...], "gaps": [...] },
    "differentiators": { "matched": [...], "gaps": [...] },
    "bonus": { "matched": [...], "gaps": [...] }
  },
  "insights": {
    "unique_to_job": ["Client Communication"],
    "unique_to_market": ["TensorFlow", "Kubernetes"]
  },
  "market_context": {
    "job_count": 47,
    "role": "AI Engineer",
    "specialty": "Generative/NLP",
    "experience": "Mid-Senior Level",
    "description": "AI Engineer / Generative/NLP / Mid-Senior Level"
  },
  "summary": {
    "job_skills_count": 7,
    "market_skills_count": 46,
    "resume_skills_count": 6,
    "total_skills": 46,
    "must_have_count": 12,
    "nice_to_have_count": 18,
    "preferred_count": 16,
    "matched_count": 9
  }
}
```

**Error Responses**:
```json
// Missing required fields
{
  "error": "Missing required fields: job_title, job_description"
}

// Missing resume
{
  "error": "Missing resume_file"
}

// Insufficient market data
{
  "error": "Insufficient market data for classified job context",
  "classification": {
    "role": "AI Engineer",
    "specialty": "Generative/NLP",
    "experience": "Mid-Senior Level",
    "confidence": 0.92
  },
  "suggestion": "The job classification may be too specific. Try a more general role."
}
```

**Database Tables Used**:
- `skill_market_frequencies` (read) - For market comparison via `getMarketSkills()`
- `canonical_skills` (read) - For skill normalization (via market-skills helper)

**Frontend Usage**:
- `UI V2/frontend/src/app/components/JobDescriptionStep.tsx` - Mode 1 (Specific Job Posting)
- Called when user submits job description + resume

**Dependencies**:
- `getMarketSkills()` from `_shared/market-skills.ts` - Retrieves and aggregates market data
- `calculateGapAnalysis()` from `_shared/gap-analysis.ts` - Calculates match score and gaps
- LLM (Gemini) for skill extraction (TODO - currently using mock data)
- LLM (Gemini) for job classification (TODO - currently using mock data)
- LLM (Gemini) for resume parsing (TODO - currently using mock data)

**Processing Steps**:
1. Query `skill_market_frequencies` table filtered by `cluster_type = 'specific'`
2. Log number of context rows retrieved for debugging
3. Iterate through contexts to build roles map and experience levels set
4. Group specialties by role dynamically
5. Sort roles alphabetically (done in-memory, not via database ORDER BY)
6. Log number of roles found and role list for debugging
7. Return JSON response with roles, specialties, and experience_levels

**Notes**:
- ✅ Fully implemented with synchronous processing
- ✅ Filters for `cluster_type = 'specific'` to exclude generalist contexts
- ✅ Groups specialties by role dynamically from database
- ✅ Sorted alphabetically for consistent UI display
- ✅ Includes console logging for debugging (row count, role count, role list)
- No authentication required (public endpoint)
- Fast response time (simple database query)

---

### 2. POST /analyze-job-posting

**Purpose**: Analyzes a specific job posting by extracting skills, classifying the job, and matching against market data

**Status**: ✅ Created (Mock LLM Integration)

**File Location**: `UI V2/backend/supabase/functions/analyze-job-posting/index.ts`

**Request**:
```json
{
  "job_title": "Senior AI Engineer",
  "company": "TechVault AI",
  "job_description": "Build and deploy cutting-edge ML models...",
  "resume_file": "base64_encoded_pdf"
}
```

**Response**:
```json
{
  "analysis_id": "uuid",
  "job_classification": {
    "role": "AI Engineer",
    "specialty": "Generative/NLP",
    "experience": "Mid-Senior Level",
    "confidence": 0.92
  },
  "job_match": {
    "score": 78,
    "matched_skills": ["Python", "PyTorch"],
    "missing_skills": ["Client Communication"]
  },
  "market_match": {
    "score": 85,
    "dealbreakers": { "matched": [...], "gaps": [...] },
    "differentiators": { "matched": [...], "gaps": [...] },
    "bonus": { "matched": [...], "gaps": [...] }
  },
  "insights": {
    "unique_to_job": ["Client Communication"],
    "unique_to_market": ["TensorFlow", "Kubernetes"]
  },
  "market_context": {
    "job_count": 47,
    "role": "AI Engineer",
    "specialty": "Generative/NLP",
    "experience": "Mid-Senior Level",
    "description": "AI Engineer / Generative/NLP / Mid-Senior Level"
  },
  "summary": {
    "job_skills_count": 7,
    "market_skills_count": 46,
    "resume_skills_count": 6,
    "total_skills": 46,
    "must_have_count": 12,
    "nice_to_have_count": 18,
    "preferred_count": 16,
    "matched_count": 9
  }
}
```

**Error Responses**:
```json
// Missing required fields
{
  "error": "Missing required fields: job_title, job_description"
}

// Missing resume
{
  "error": "Missing resume_file"
}

// Insufficient market data
{
  "error": "Insufficient market data for classified job context",
  "classification": {
    "role": "AI Engineer",
    "specialty": "Generative/NLP",
    "experience": "Mid-Senior Level",
    "confidence": 0.92
  },
  "suggestion": "The job classification may be too specific. Try a more general role."
}
```

**Database Tables Used**:
- `skill_market_frequencies` (read) - For market comparison via `getMarketSkills()`
- `canonical_skills` (read) - For skill normalization (via market-skills helper)

**Frontend Usage**:
- `UI V2/frontend/src/app/components/JobDescriptionStep.tsx` - Mode 1 (Specific Job Posting)
- Called when user submits job description + resume

**Dependencies**:
- `getMarketSkills()` from `_shared/market-skills.ts` - Retrieves and aggregates market data
- `calculateGapAnalysis()` from `_shared/gap-analysis.ts` - Calculates match score and gaps
- LLM (Gemini) for skill extraction (TODO - currently using mock data)
- LLM (Gemini) for job classification (TODO - currently using mock data)
- LLM (Gemini) for resume parsing (TODO - currently using mock data)

**Processing Steps**:
1. Validate input (job_title, job_description, resume_file required)
2. Generate unique analysis ID using `crypto.randomUUID()`
3. Extract skills from job description using `extractJobSkills()` (currently mock data)
4. Classify job into role/specialty/experience using `classifyJob()` (currently mock data)
5. Extract skills from resume using `extractResumeSkills()` (currently mock data)
6. Query market data for classified context using `getMarketSkills()`
7. Return 404 if insufficient market data available
8. Calculate job match score using `calculateJobMatch()` (simple string matching)
9. Calculate market match using `calculateGapAnalysis()`
10. Identify skills unique to job vs unique to market (top 10 market skills)
11. Build context description and summary statistics
12. Return complete analysis result

**Notes**:
- ✅ Fully implemented with synchronous processing
- ✅ Input validation for required fields
- ✅ Error handling for insufficient market data
- ✅ Dual analysis: job-specific match + market comparison
- ✅ Identifies skills unique to the job vs unique to the market
- ⏳ Job skill extraction uses mock data - needs Gemini API integration
- ⏳ Job classification uses mock data - needs Gemini API integration
- ⏳ Resume skill extraction uses mock data - needs Gemini API integration
- ⏳ TODO: Implement async processing with job queue for production
- ⏳ TODO: Add PDF parsing (decode base64, extract text)
- ⏳ TODO: Normalize extracted skills against `canonical_skills` table

---

### 3. POST /analyze-market-role

**Purpose**: Analyzes resume against selected market role/specialty/experience levels

**Status**: ✅ Created (with Gemini integration)

**File Location**: `UI V2/backend/supabase/functions/analyze-market-role/index.ts`

**Request**:
```json
{
  "role": "Software Engineer",
  "specialty": "Backend",
  "experience_levels": ["Internship", "Entry Level"],
  "resume_file": "base64_encoded_pdf"
}
```

**Response**:
```json
{
  "analysis_id": "uuid",
  "match_score": 78,
  "market_context": {
    "job_count": 142,
    "role": "Software Engineer",
    "specialty": "Backend",
    "experience_levels": ["Internship", "Entry Level"],
    "description": "Software Engineer / Backend / Internship + Entry Level"
  },
  "dealbreakers": { 
    "matched": [
      {
        "canonical_name": "Python",
        "tier1": "Technical",
        "tier2": "Programming Languages",
        "frequency_percentage": 95.7,
        "importance": "Must-have",
        "unique_jobs": 135,
        "total_jobs_in_context": 142
      }
    ], 
    "gaps": [...] 
  },
  "differentiators": { "matched": [...], "gaps": [...] },
  "bonus": { "matched": [...], "gaps": [...] },
  "summary": { 
    "total_skills": 46, 
    "must_have_count": 12, 
    "nice_to_have_count": 18,
    "preferred_count": 16,
    "matched_count": 9 
  }
}
```

**Error Responses**:
```json
// Missing required fields
{
  "error": "Missing required fields: role, experience_levels"
}

// Missing resume file
{
  "error": "Missing resume_file"
}

// File too large
{
  "error": "Resume file too large. Maximum size is 5MB."
}

// Insufficient market data
{
  "error": "Insufficient market data for selected role/specialty/experience levels",
  "suggestion": "Try selecting different experience levels or a more general specialty"
}
```

**Database Tables Used**:
- `skill_market_frequencies` (read) - For market requirements via `getMarketSkills()`
- `canonical_skills` (read) - For skill normalization (via resume-extractor helper)
- `job_skills` (read) - For tier1/tier2 classification (via market-skills helper)
- `analysis_jobs` (write) - Stores analysis job status
- `analysis_results` (write) - Stores completed analysis results

**Frontend Usage**:
- `UI V2/frontend/src/app/components/JobDescriptionStep.tsx` - Mode 2 (General Role Selection)
- `UI V2/frontend/src/app/components/MarketIntelligenceDashboard.tsx` - Displays results
- Called when user selects role/specialty/experience + uploads resume

**Dependencies**:
- `extractResumeSkills()` from `_shared/resume-extractor.ts` - Extracts skills from resume using Gemini API
  - Uses `callGemini()` from `_shared/gemini-client.ts` for LLM calls
  - Uses `pako` (npm:pako@2.1.0) for PDF FlateDecode decompression
  - Normalizes extracted skills against `canonical_skills` table
- `getMarketSkills()` from `_shared/market-skills.ts` - Retrieves and aggregates market data
- `calculateGapAnalysis()` from `_shared/gap-analysis.ts` - Calculates match score and gaps

**Processing Steps**:
1. Validate input (role, experience_levels array, resume_file required)
2. Check file size (max 5MB after base64 decoding)
3. Generate unique analysis ID using `crypto.randomUUID()`
4. Extract skills from resume using `extractResumeSkills()`:
   - Decode base64 and detect file type (PDF or text)
   - For PDFs: Extract text using pako decompression for FlateDecode streams
   - Call Gemini API to extract skills from text
   - Normalize extracted skills against `canonical_skills` table (fuzzy matching)
5. Query market data for selected contexts using `getMarketSkills()`
6. Return 404 if insufficient market data available
7. Calculate gap analysis using `calculateGapAnalysis()`
8. Build context description (e.g., "Software Engineer / Backend / Internship + Entry Level")
9. Store analysis job and result in database via `storeAnalysisResult()`
10. Return complete analysis result

**Notes**:
- ✅ Fully implemented with synchronous processing
- ✅ Input validation for required fields and file size (5MB limit)
- ✅ Error handling for insufficient market data
- ✅ Supports multiple experience level selections
- ✅ Aggregates frequencies across selected levels via `getMarketSkills()`
- ✅ Resume skill extraction integrated with Gemini API
- ✅ PDF text extraction with pako decompression for FlateDecode streams
- ✅ Fuzzy skill matching against canonical skills database
- ✅ Stores analysis results in database (analysis_jobs and analysis_results tables)
- ✅ File size validation to prevent oversized uploads
- ⏳ TODO: Implement async processing with job queue for production
- ⏳ TODO: Add support for DOCX files (currently PDF and plain text only)

---

### 4. GET /analysis-status/:id

**Purpose**: Polls for analysis progress to show loading state

**Status**: ✅ Created (Mock Data)

**File Location**: `UI V2/backend/supabase/functions/analysis-status/index.ts`

**Request**:
```http
GET /analysis-status/550e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "status": "processing",
  "progress": {
    "step": "Normalizing your resume skills...",
    "percentage": 60
  }
}
```

**Possible Status Values**:
- `processing` - Analysis in progress
- `completed` - Analysis finished, results available
- `failed` - Analysis failed with error

**Database Tables Used**:
- `analysis_jobs` (read) - Stores analysis status (table not created yet)

**Frontend Usage**:
- `UI V2/frontend/src/app/components/AnalysisWizardLayout.tsx` - Loading state UI
- Polled every 2 seconds while status is "processing"

**Dependencies**:
- `/analyze-job-posting` or `/analyze-market-role` (creates analysis job)

**Notes**:
- Currently returns mock progress data for frontend testing
- TODO: Implement database storage for actual job status tracking
- Randomly simulates different processing stages
- In production, should query `analysis_jobs` table for real status
- Returns progress messages for better UX
- Percentage calculated based on completed steps
- Stops polling when status is "completed" or "failed"

---

### 5. GET /analysis-result/:id

**Purpose**: Returns complete analysis result with match score and gap analysis

**Status**: ✅ Created (Mock Data)

**File Location**: `UI V2/backend/supabase/functions/analysis-result/index.ts`

**Request**:
```http
GET /analysis-result/550e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "match_score": 78,
  "market_context": {
    "job_count": 142,
    "role": "Software Engineer",
    "specialty": "Backend",
    "experience_levels": ["Internship", "Entry Level"],
    "description": "Backend Intern/Entry Level roles"
  },
  "dealbreakers": {
    "matched": [
      {
        "canonical_name": "Python",
        "frequency_percentage": 95.7,
        "tier1": "Technical Skills",
        "tier2": "Programming Languages"
      }
    ],
    "gaps": [
      {
        "canonical_name": "Git",
        "frequency_percentage": 89.2,
        "tier1": "Technical Skills",
        "tier2": "Tools & Platforms"
      }
    ]
  },
  "differentiators": {
    "matched": [],
    "gaps": []
  },
  "bonus": {
    "matched": [],
    "gaps": []
  },
  "summary": {
    "total_skills": 46,
    "must_have_count": 12,
    "nice_to_have_count": 18,
    "preferred_count": 16,
    "matched_count": 9
  }
}
```

**Database Tables Used**:
- `analysis_results` (read) - Stores completed analysis (table not created yet)

**Frontend Usage**:
- `UI V2/frontend/src/app/components/StrategyDashboard.tsx` - Displays results
- Called after `/analysis-status` returns "completed"

**Dependencies**:
- `/analyze-job-posting` or `/analyze-market-role` (creates analysis)
- `/analysis-status` (confirms completion)

**Notes**:
- Currently returns mock data for testing frontend integration
- TODO: Implement database storage for analysis results
- TODO: Add caching (24 hours) for completed analyses
- Match score based on Must-have skills only
- Skills categorized by importance (Dealbreakers/Differentiators/Bonus)

---

### 6. GET /market-skills (Internal Helper)

**Purpose**: Internal helper function to retrieve and aggregate market skills for given contexts

**Status**: ✅ Created

**File Location**: `UI V2/backend/supabase/functions/_shared/market-skills.ts`

**Request**:
```typescript
getMarketSkills(
  role: "Software Engineer",
  specialty: "Backend",
  experienceLevels: ["Internship", "Entry Level"]
)
```

**Response**:
```typescript
{
  skills: MarketSkill[],
  job_count: 142,
  contexts: Context[]
}
```

**Database Tables Used**:
- `skill_market_frequencies` (read)
- `canonical_skills` (read)

**Frontend Usage**: None (internal helper)

**Dependencies**: None

**Notes**:
- Aggregates frequencies across multiple experience levels
- Handles "Insufficient Data" contexts by rolling up to parent
- Calculates importance based on frequency thresholds

---

## Database Schema

### Tables Used

#### canonical_skills
- `id` (PK)
- `canonical_name` (unique)
- `created_at`

**Purpose**: Master list of normalized skill names

---

#### skill_market_frequencies
- `id` (PK)
- `canonical_skill_id` (FK → canonical_skills)
- `job_role`
- `role_sub_cluster`
- `experience_level`
- `cluster_type` ('specific' | 'generalist')
- `raw_frequency`
- `normalized_frequency`
- `unique_jobs`
- `total_jobs_in_context`
- `importance` ('Must-have' | 'Nice-to-have' | 'Preferred' | 'Insufficient Data')
- `created_at`

**Purpose**: Stores skill frequency data for each market context

---

#### analysis_jobs (To Be Created)
- `id` (PK, UUID)
- `status` ('processing' | 'completed' | 'failed')
- `progress_step`
- `progress_percentage`
- `created_at`
- `updated_at`

**Purpose**: Tracks analysis job status for polling

---

#### analysis_results (To Be Created)
- `id` (PK, UUID)
- `analysis_job_id` (FK → analysis_jobs)
- `match_score`
- `market_context` (JSONB)
- `dealbreakers` (JSONB)
- `differentiators` (JSONB)
- `bonus` (JSONB)
- `summary` (JSONB)
- `created_at`

**Purpose**: Stores completed analysis results

---

## Frontend Integration

### Component → Endpoint Mapping

| Component | Endpoints Used | Purpose |
|-----------|---------------|---------|
| `JobDescriptionStep.tsx` | `/target-options` | Load role/specialty/experience options |
| `JobDescriptionStep.tsx` | `/analyze-job-posting` | Submit job posting analysis (Mode 1) |
| `JobDescriptionStep.tsx` | `/analyze-market-role` | Submit market role analysis (Mode 2) |
| `AnalysisWizardLayout.tsx` | `/analysis-status/:id` | Poll for analysis progress |
| `StrategyDashboard.tsx` | `/analysis-result/:id` | Display analysis results |

---

## Environment Variables

### Backend (Supabase Edge Functions)
```env
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_ANON_KEY=[anon-key]
SUPABASE_SERVICE_ROLE_KEY=[service-role-key]
GEMINI_API_KEY=[gemini-api-key]
```

### Frontend
```env
VITE_SUPABASE_URL=https://[project-ref].supabase.co
VITE_SUPABASE_ANON_KEY=[anon-key]
VITE_API_BASE_URL=http://localhost:54321/functions/v1  # Dev
# VITE_API_BASE_URL=https://[project-ref].supabase.co/functions/v1  # Prod
```

---

## Development Workflow

### Adding a New Endpoint

1. **Create Edge Function**:
   ```bash
   cd "UI V2/backend"
   # Create function folder
   mkdir -p supabase/functions/[endpoint-name]
   # Create index.ts
   ```

2. **Update This Documentation**:
   - Add endpoint section with full details
   - Update component mapping table
   - Update database schema if needed

3. **Deploy Function**:
   ```bash
   supabase functions deploy [endpoint-name]
   ```

4. **Update Frontend**:
   - Add API call in relevant component
   - Update types if needed
   - Test integration

---

## Testing

### Manual Testing
```bash
# Test target-options endpoint
curl http://localhost:54321/functions/v1/target-options

# Test with authorization
curl -H "Authorization: Bearer [anon-key]" \
     http://localhost:54321/functions/v1/target-options
```

### Integration Testing
- Test each endpoint with real data
- Verify CORS headers work with frontend
- Check error handling for edge cases

---

## Deployment Checklist

- [ ] All endpoints deployed to Supabase
- [ ] Environment variables configured
- [ ] Frontend updated with production URLs
- [ ] CORS headers configured correctly
- [ ] Database migrations applied
- [ ] API documentation updated
- [ ] Error handling tested
- [ ] Rate limiting configured (if needed)

---

## Notes

- All endpoints use CORS headers for frontend access
- Authentication uses Supabase anon key (public endpoints)
- LLM calls are rate-limited to prevent abuse
- Analysis results cached for 24 hours
- Resume files stored temporarily, deleted after processing

---

**Last Updated**: 2026-03-06
**Version**: 1.0.3
