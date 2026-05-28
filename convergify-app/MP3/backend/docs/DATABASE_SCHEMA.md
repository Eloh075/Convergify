# Career Analysis Platform - Database Schema Reference

**Database Location**: `backend/career_analysis.db` (SQLite)

## Table Overview

1. **users** - User management
2. **resumes** - Resume storage and metadata
3. **optimized_resumes** - AI-optimized resume versions
4. **jobs** - Job postings and requirements
5. **job_groups** - Custom job groupings
6. **analyses** - Career analysis sessions
7. **analysis_sessions** - Session management for workflows
8. **celery_tasks** - Background task tracking
9. **skill_canonical_cache** - Canonical skill mapping cache

---

## Table Schemas

### 1. users
```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,           -- UUID string
    created_at DATETIME,             -- User creation timestamp
    last_active DATETIME             -- Last activity timestamp
);
```

**Relationships:**
- One-to-many with `resumes` (user_id)
- One-to-many with `analysis_sessions` (user_id)

---

### 2. resumes
```sql
CREATE TABLE resumes (
    id VARCHAR PRIMARY KEY,           -- UUID string
    user_id VARCHAR NOT NULL,        -- FK to users.id
    filename VARCHAR NOT NULL,       -- Original filename
    original_text TEXT NOT NULL,     -- Extracted text content
    file_path VARCHAR NOT NULL,      -- File storage path
    file_size INTEGER NOT NULL,      -- File size in bytes
    upload_date DATETIME,            -- Upload timestamp
    analysis_status VARCHAR,         -- Status: pending, processing, completed, failed, skills_extracted
    extracted_skills TEXT,           -- JSON array of skills
    optimized_version_id VARCHAR,    -- FK to optimized_resumes.id
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (optimized_version_id) REFERENCES optimized_resumes(id)
);
```

**Key Fields:**
- `analysis_status` values: "pending", "processing", "completed", "failed", "skills_extracted"
- `extracted_skills`: JSON array stored as TEXT
- `file_size`: Integer (bytes)

**Relationships:**
- Many-to-one with `users` (user_id)
- One-to-one with `optimized_resumes` (optimized_version_id)
- One-to-many with `analyses` (resume_id)

---

### 3. optimized_resumes
```sql
CREATE TABLE optimized_resumes (
    id VARCHAR PRIMARY KEY,           -- UUID string
    original_resume_id VARCHAR NOT NULL, -- FK to resumes.id
    optimized_text TEXT NOT NULL,    -- AI-optimized content
    changes TEXT NOT NULL,            -- JSON array of changes made
    improvement_score FLOAT,          -- Score improvement (0.0-1.0)
    target_job_ids TEXT NOT NULL,    -- JSON array of target job IDs
    generated_date DATETIME,          -- Generation timestamp
    file_path VARCHAR,                -- Optional file storage path
    
    FOREIGN KEY (original_resume_id) REFERENCES resumes(id)
);
```

**Key Fields:**
- `changes`: JSON array of modification details
- `target_job_ids`: JSON array of job IDs used for optimization
- `improvement_score`: Float between 0.0 and 1.0

---

### 4. jobs
```sql
CREATE TABLE jobs (
    id VARCHAR PRIMARY KEY,           -- UUID string
    title VARCHAR NOT NULL,          -- Job title
    company VARCHAR NOT NULL,        -- Company name
    description TEXT NOT NULL,       -- Job description
    requirements TEXT,               -- JSON array of requirements
    location VARCHAR,                -- Job location
    employment_type VARCHAR,         -- Employment type (full-time, part-time, contract, internship, etc.)
    salary_min INTEGER,              -- Minimum salary
    salary_max INTEGER,              -- Maximum salary
    source VARCHAR NOT NULL,         -- Data source (manual, scraped, etc.)
    scraped_date DATETIME,           -- When scraped (if applicable)
    required_skills TEXT,            -- JSON array of required skills
    skills_processed BOOLEAN,        -- Whether skills have been extracted/processed
    group_id VARCHAR,                -- FK to job_groups.id
    created_date DATETIME,           -- Creation timestamp
    
    FOREIGN KEY (group_id) REFERENCES job_groups(id)
);
```

**Key Fields:**
- `requirements`: JSON array stored as TEXT
- `required_skills`: JSON array stored as TEXT
- `skills_processed`: Boolean flag indicating if skills extraction has been completed
- `employment_type`: String indicating job type ("full-time", "part-time", "contract", "internship", etc.)
- `source`: String indicating data source
- `salary_min/max`: Integer values (not formatted strings)

**Relationships:**
- Many-to-one with `job_groups` (group_id)

---

### 5. job_groups
```sql
CREATE TABLE job_groups (
    id VARCHAR PRIMARY KEY,           -- UUID string
    name VARCHAR NOT NULL,           -- Group name
    description TEXT,                -- Group description
    group_type VARCHAR DEFAULT 'custom', -- Group type: "scraped" or "custom"
    job_ids TEXT NOT NULL,           -- JSON array of job IDs
    created_date DATETIME,           -- Creation timestamp
    analysis_results TEXT            -- JSON array of analysis results
);
```

**Key Fields:**
- `group_type`: String indicating group origin ("scraped" for auto-created from scraping, "custom" for user-created)
- `job_ids`: JSON array of job ID strings
- `analysis_results`: JSON array of analysis data

**Relationships:**
- One-to-many with `jobs` (group_id)

---

### 6. analyses
```sql
CREATE TABLE analyses (
    id VARCHAR PRIMARY KEY,           -- UUID string
    resume_id VARCHAR NOT NULL,      -- FK to resumes.id
    job_ids TEXT NOT NULL,           -- JSON array of job IDs analyzed
    analysis_type VARCHAR DEFAULT 'comprehensive', -- Analysis type: comprehensive, single_job, market_analysis
    status VARCHAR DEFAULT 'pending', -- Status: pending, processing, completed, failed
    task_id VARCHAR,                 -- Celery task ID for background job tracking
    created_at DATETIME,             -- Analysis creation timestamp
    start_date DATETIME,             -- Analysis start time (kept for backward compatibility)
    started_at DATETIME,             -- When analysis actually started processing
    completion_date DATETIME,        -- Analysis completion time
    results TEXT,                    -- JSON object with analysis results
    error_message TEXT,              -- Error details if analysis failed
    optimized_resume_id VARCHAR,     -- FK to optimized_resumes.id
    
    FOREIGN KEY (resume_id) REFERENCES resumes(id),
    FOREIGN KEY (optimized_resume_id) REFERENCES optimized_resumes(id)
);
```

**Key Fields:**
- `analysis_type` values: "comprehensive", "single_job", "market_analysis" (default: "comprehensive")
- `status` values: "pending", "processing", "completed", "failed" (default: "pending")
- `task_id`: Celery task ID string for tracking background job execution
- `created_at`: Timestamp when analysis record was created
- `start_date`: Legacy field kept for backward compatibility (defaults to created_at)
- `started_at`: Timestamp when analysis processing actually began (set when task starts)
- `error_message`: TEXT field containing error details if status is "failed"
- `job_ids`: JSON array of job ID strings
- `results`: JSON object with analysis data

**Timestamp Fields Explained:**
- `created_at`: When the analysis was requested/created in the database
- `start_date`: Legacy field (kept for backward compatibility, defaults to created_at)
- `started_at`: When the Celery background task actually started processing
- `completion_date`: When the analysis finished (success or failure)

**Model Properties (Python):**
- `job_ids_list` / `job_ids_list.setter` - Converts JSON job_ids to/from Python list
- `results_dict` / `results_dict.setter` - Converts JSON results to/from Python dict
- `duration` - Calculated duration between start_date and completion_date
- `completed_at` - Alias for completion_date (for naming consistency)
- `is_completed` - Boolean check if status is "completed" and completion_date is set
- `job_count` - Number of jobs in the analysis (length of job_ids_list)

**Relationships:**
- Many-to-one with `resumes` (resume_id)
- Many-to-one with `optimized_resumes` (optimized_resume_id)

---

### 7. analysis_sessions
```sql
CREATE TABLE analysis_sessions (
    id VARCHAR PRIMARY KEY,           -- UUID string
    user_id VARCHAR NOT NULL,        -- FK to users.id
    title VARCHAR NOT NULL,          -- Session title
    description TEXT,                -- Session description
    created_at DATETIME,             -- Creation timestamp
    updated_at DATETIME,             -- Last update timestamp
    completed_at DATETIME,           -- Completion timestamp
    status VARCHAR,                  -- Status: active, completed, archived
    session_type VARCHAR,            -- Type: comprehensive, single_job, market_analysis
    resume_ids TEXT NOT NULL,        -- JSON array of resume IDs
    job_ids TEXT NOT NULL,           -- JSON array of job IDs
    analysis_ids TEXT NOT NULL,      -- JSON array of analysis IDs
    configuration TEXT,              -- JSON object with session config
    tags TEXT,                       -- JSON array of user tags
    total_jobs INTEGER,              -- Count of jobs in session
    total_resumes INTEGER,           -- Count of resumes in session
    total_analyses INTEGER,          -- Count of analyses in session
    overall_match_score FLOAT,       -- Overall session score
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Key Fields:**
- `status` values: "active", "completed", "archived"
- `session_type` values: "comprehensive", "single_job", "market_analysis"
- All `*_ids` fields: JSON arrays stored as TEXT
- `configuration`: JSON object for session settings
- `tags`: JSON array of string tags

**Relationships:**
- Many-to-one with `users` (user_id)

---

### 8. celery_tasks
```sql
CREATE TABLE celery_tasks (
    id VARCHAR PRIMARY KEY,           -- UUID string
    task_id VARCHAR UNIQUE NOT NULL, -- Celery task ID
    task_name VARCHAR NOT NULL,      -- Task function name
    status VARCHAR,                  -- Task status
    args TEXT,                       -- JSON array of task arguments
    kwargs TEXT,                     -- JSON object of task keyword arguments
    result TEXT,                     -- JSON object of task result
    error TEXT,                      -- Error message if failed
    created_at DATETIME,             -- Task creation time
    started_at DATETIME,             -- Task start time
    completed_at DATETIME            -- Task completion time
);
```

**Key Fields:**
- `status` values: "pending", "STARTED", "SUCCESS", "FAILURE"
- `args`: JSON array of positional arguments
- `kwargs`: JSON object of keyword arguments
- `result`: JSON object with task results

---

### 9. skill_canonical_cache
```sql
CREATE TABLE skill_canonical_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Auto-incrementing ID
    skill_name VARCHAR NOT NULL UNIQUE,   -- Specific skill name (indexed)
    canonical_name VARCHAR NOT NULL,      -- Canonical parent skill (indexed)
    confidence FLOAT DEFAULT 1.0,         -- LLM confidence in mapping (0.0-1.0)
    created_at DATETIME,                  -- Cache entry creation time
    updated_at DATETIME                   -- Last update time
);

CREATE INDEX idx_skill_canonical_lookup ON skill_canonical_cache(skill_name, canonical_name);
```

**Purpose:**
Caches canonical skill mappings to reduce LLM API calls. Maps specific skill names to their canonical parent names.

**Example Mappings:**
- "Generative AI" → "Artificial Intelligence (AI)"
- "React.js" → "React"
- "Python 3" → "Python"

**Key Fields:**
- `skill_name`: Specific skill variant (unique, indexed)
- `canonical_name`: Standardized parent skill name (indexed)
- `confidence`: LLM confidence score (0.0 to 1.0, default 1.0)
- `created_at`: When mapping was first cached
- `updated_at`: When mapping was last updated

**Indexes:**
- Unique index on `skill_name` for fast lookups
- Index on `canonical_name` for reverse lookups
- Composite index on `(skill_name, canonical_name)` for relationship queries

**Usage Pattern:**
1. Check cache for skill_name before calling LLM
2. If found, use cached canonical_name
3. If not found, call LLM and cache result
4. Update confidence if LLM provides new mapping

---

## JSON Field Patterns

### Common JSON Fields:
- **Skills Arrays**: `["Python", "JavaScript", "SQL"]`
- **Job IDs Arrays**: `["job-uuid-1", "job-uuid-2"]`
- **Requirements Arrays**: `["Bachelor's degree", "3+ years experience"]`
- **Tags Arrays**: `["urgent", "remote", "senior-level"]`
- **Configuration Objects**: `{"max_jobs": 50, "include_salary": true}`

### Model Properties (Python):
All models have helper properties to convert JSON fields:
- `skills_list` / `skills_list.setter`
- `job_ids_list` / `job_ids_list.setter`
- `requirements_list` / `requirements_list.setter`
- `tags_list` / `tags_list.setter`
- `configuration_dict` / `configuration_dict.setter`

---

## API Schema Field Names

### Resume Fields:
- `id`, `user_id`, `filename`, `file_size`, `upload_date`
- `analysis_status`, `extracted_skills`, `optimized_version_id`

### Job Fields:
- `id`, `title`, `company`, `description`, `location`
- `employment_type`, `salary_min`, `salary_max`, `source`, `required_skills`
- `created_date`, `scraped_date`, `group_id`

### Job Scraping Fields:
- `search_terms` - List of search terms for job scraping
- `employment_type` - Employment type filter (default: "full-time")
- `max_jobs` - Maximum number of jobs to scrape (default: 10)
- `location` - Optional location filter

### Session Fields:
- `id`, `user_id`, `title`, `description`, `status`, `session_type`
- `created_at`, `updated_at`, `completed_at`
- `resume_ids`, `job_ids`, `analysis_ids`
- `total_jobs`, `total_resumes`, `total_analyses`
- `overall_match_score`, `configuration`, `tags`

### Analysis Fields:
- `id`, `resume_id`, `job_ids`, `analysis_type`, `status`
- `start_date`, `completion_date`, `results`
- `optimized_resume_id`

---

## Status Values Reference

### Resume Status:
- `"pending"` - Uploaded, not processed
- `"processing"` - Currently being analyzed
- `"completed"` - Analysis complete
- `"failed"` - Analysis failed
- `"skills_extracted"` - Skills extracted successfully

### Analysis Status:
- `"pending"` - Queued for processing
- `"processing"` - Currently running
- `"completed"` - Successfully completed
- `"failed"` - Failed with error

### Analysis Types:
- `"comprehensive"` - Full analysis with multiple jobs and market insights
- `"single_job"` - Analysis focused on one specific job opportunity
- `"market_analysis"` - Market research and demand analysis focused

### Session Status:
- `"active"` - Currently being worked on
- `"completed"` - Finished and closed
- `"archived"` - Archived for storage

### Session Types:
- `"comprehensive"` - Full analysis with multiple jobs
- `"single_job"` - Analysis for one specific job
- `"market_analysis"` - Market research focused

### Analysis API Schemas

#### AnalysisCreateRequest
Request schema for creating new analysis sessions:
```python
{
    "resume_id": "resume-uuid",                              # Required
    "job_ids": ["job-uuid-1", "job-uuid-2"],               # Optional
    "analysis_type": "comprehensive"                         # Optional, default: "comprehensive"
}
```

#### AnalysisResponse
Response schema for analysis data:
```python
{
    "id": "analysis-uuid",                                   # Analysis ID
    "resume_id": "resume-uuid",                             # Resume ID
    "job_ids": ["job-uuid-1", "job-uuid-2"],               # Job IDs list
    "analysis_type": "comprehensive",                        # Analysis type
    "status": "completed",                                   # Status
    "task_id": "celery-task-uuid",                          # Celery task ID for tracking
    "created_at": "2024-01-01T10:00:00Z",                  # Creation timestamp
    "start_date": "2024-01-01T10:00:00Z",                  # Start timestamp (legacy)
    "started_at": "2024-01-01T10:00:05Z",                  # Processing start timestamp
    "completion_date": "2024-01-01T10:30:00Z",             # Completion timestamp
    "completed_at": "2024-01-01T10:30:00Z",                # Alias for completion_date
    "results": {...},                                        # Analysis results object
    "error_message": "Error details if failed",             # Error message (if status is "failed")
    "optimized_resume_id": "optimized-resume-uuid",         # Optional optimized resume
    "duration": "0:30:00",                                   # Duration timedelta
    "job_count": 2                                          # Number of jobs analyzed
}
```

**New Fields for Background Task Tracking:**
- `task_id`: Celery task ID for monitoring background job progress
- `created_at`: When the analysis was created/requested
- `started_at`: When the background task actually started processing (may differ from created_at)
- `error_message`: Detailed error information if the analysis failed

#### AnalysisResultsResponse
Response schema for detailed analysis results:
```python
{
    "analysis_id": "analysis-uuid",                          # Analysis ID
    "resume_id": "resume-uuid",                             # Resume ID
    "resume_filename": "resume.pdf",                         # Resume filename
    "job_count": 2,                                         # Number of jobs
    "job_titles": ["Software Engineer", "Data Scientist"],  # Job titles
    "analysis_type": "comprehensive",                        # Analysis type
    "status": "completed",                                   # Status
    "task_id": "celery-task-uuid",                          # Celery task ID
    "results": {...},                                        # Detailed results
    "error_message": "Error details if failed",             # Error message (if failed)
    "created_at": "2024-01-01T10:00:00Z",                  # Creation time
    "started_at": "2024-01-01T10:00:05Z",                  # Processing start time
    "completed_at": "2024-01-01T10:30:00Z"                 # Completion time
}
```

---

## API Schema Reference

### Job API Schemas

#### JobCreateRequest
Request schema for creating new job postings:
```python
{
    "title": "Software Engineer",                            # Required
    "company": "Tech Corp",                                  # Required
    "description": "Full job description text",             # Required
    "requirements": ["Bachelor's degree", "3+ years exp"],  # Optional
    "location": "Singapore",                                 # Optional
    "employment_type": "full-time",                          # Optional
    "salary_min": 50000,                                     # Optional
    "salary_max": 80000,                                     # Optional
    "skills": ["Python", "JavaScript"]                      # Optional
}
```

#### JobResponse
Response schema for job data with computed properties:
```python
{
    "id": "job-uuid",                                        # Job ID
    "title": "Software Engineer",                           # Job title
    "company": "Tech Corp",                                  # Company name
    "description": "Full job description",                  # Description
    "requirements": ["Bachelor's degree"],                  # Requirements list
    "location": "Singapore",                                 # Location
    "employment_type": "full-time",                          # Employment type
    "salary_min": 50000,                                     # Min salary
    "salary_max": 80000,                                     # Max salary
    "source": "scraped",                                     # Data source
    "scraped_date": "2024-01-01T10:00:00Z",                # Scrape timestamp
    "required_skills": ["Python", "JavaScript"],            # Skills list
    "skills_processed": true,                                # Skills extraction status
    "group_id": "group-uuid",                               # Group ID
    "created_date": "2024-01-01T10:00:00Z",                # Creation time
    "salary_range": "$50,000 - $80,000"                    # Computed property
}
```

**Note**: JobResponse includes a `from_job_model()` class method that properly converts Job model instances to response schemas using the model's property getters for JSON fields.

#### ScrapingConfig
Configuration schema for advanced scraping settings:
```python
{
    "search_terms": ["data scientist", "machine learning"],   # Required
    "location": "Remote",                                     # Optional
    "max_jobs": 50,                                          # Default: 50
    "employment_type": "contract",                           # Optional
    "experience_level": "senior"                             # Optional
}
```

#### ScrapingJob
Status tracking schema for scraping operations:
```python
{
    "id": "scraping-job-uuid",                               # Job ID
    "status": "running",                                     # Status
    "progress": 75,                                          # 0-100
    "total_jobs": 100,                                       # Target count
    "scraped_jobs": 75,                                      # Current count
    "errors": ["Rate limit exceeded"],                       # Error list
    "started_at": "2024-01-01T10:00:00Z",                   # Start time
    "estimated_completion": "2024-01-01T10:30:00Z"          # ETA
}
```

#### JobGroupCreateRequest
Request schema for creating job groups:
```python
{
    "name": "Senior Developer Roles",                        # Required
    "description": "High-level development positions",      # Optional
    "job_ids": ["job-uuid-1", "job-uuid-2"]                # Optional
}
```

#### JobGroupResponse
Response schema for job group data:
```python
{
    "id": "group-uuid",                                      # Group ID
    "name": "Senior Developer Roles",                       # Group name
    "description": "High-level development positions",      # Description
    "group_type": "custom",                                  # "scraped" or "custom"
    "job_ids": ["job-uuid-1", "job-uuid-2"]                # Job IDs list
}
```

**Note**: `group_type` indicates the origin of the job group:
- `"scraped"`: Auto-created from scraping operations
- `"custom"`: Manually created by users

#### JobFilters
Filtering schema for job search operations:
```python
{
    "title": "engineer",                                     # Optional
    "company": "Google",                                     # Optional
    "location": "Singapore",                                 # Optional
    "employment_type": "full-time",                          # Optional
    "source": "scraped",                                     # Optional
    "salary_min": 50000,                                     # Optional
    "salary_max": 100000,                                    # Optional
    "skills": ["Python", "JavaScript"],                     # Optional
    "group_id": "group-uuid"                                 # Optional
}
```

#### ScrapingRequest
Request schema for initiating job scraping operations:
```python
{
    "search_terms": ["software engineer", "python developer"],  # Required
    "employment_type": "full-time",                            # Default: "full-time"
    "max_jobs": 10,                                           # Default: 10
    "location": "Singapore"                                   # Optional
}
```

---

## Important Notes

1. **All IDs are UUID strings**, not integers
2. **JSON fields are stored as TEXT** and need parsing
3. **Timestamps use datetime objects**, not strings in Python
4. **File sizes are integers** (bytes), not formatted strings
5. **Salary values are integers**, not formatted currency strings
6. **Foreign key relationships** must be maintained
7. **Use model properties** for JSON field access in Python
8. **Status values are lowercase strings** with underscores
9. **Analysis timestamp fields**:
   - `created_at`: When analysis record was created in database
   - `start_date`: Legacy field (kept for backward compatibility)
   - `started_at`: When Celery background task actually started processing
   - `completion_date`: When analysis finished (success or failure)
10. **Background task tracking**: Use `task_id` field to track Celery job progress
11. **Error handling**: Check `error_message` field when `status` is "failed"

---

## Common Mistakes to Avoid

❌ **Wrong**: `resume.skills` (doesn't exist)
✅ **Correct**: `resume.skills_list` (property that parses JSON)

❌ **Wrong**: `session.job_ids` (returns JSON string)
✅ **Correct**: `session.job_ids_list` (returns Python list)

❌ **Wrong**: `job.salary = "$50,000"` (formatted string)
✅ **Correct**: `job.salary_min = 50000` (integer)

❌ **Wrong**: `analysis.status = "COMPLETED"` (uppercase)
✅ **Correct**: `analysis.status = "completed"` (lowercase)

❌ **Wrong**: Using integer IDs
✅ **Correct**: Using UUID strings for all IDs