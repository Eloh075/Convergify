# Job Detail Extraction Component

This component extracts detailed information from job postings on LinkedIn and SkillsFuture (MyCareersFuture) websites.

## Overview

The component analyzes job pages and extracts structured information including:
- Job title, company, location
- Job description and requirements
- Employment terms (job type, experience level, salary)
- Classification (industry, sector, category)
- Dates (posted, updated, application deadline)

## Architecture

```
job_detail_extraction/
├── __init__.py
├── config.py           # Configuration settings
├── models.py           # Data models (JobDetails)
├── extractors.py       # Site-specific extractors
├── database.py         # Database operations
├── engine.py           # Main extraction engine
├── main.py            # CLI interface
├── analyze_job_pages.py      # Analysis tools
└── detailed_job_analysis.py  # Detailed analysis
```

## Key Features

### 1. **Site-Specific Extractors**
- `LinkedInJobDetailExtractor`: Extracts from LinkedIn using CSS selectors and JSON-LD
- `SkillsFutureJobDetailExtractor`: Extracts from MyCareersFuture with pattern matching

### 2. **Data Model**
```python
class JobDetails:
    url: str                    # Job URL
    website: str               # LinkedIn or SkillsFuture
    job_title: str             # Full job title
    company: str               # Company name
    location: str              # Job location
    salary_range: str          # e.g., "$6,000 to $7,800 Monthly"
    job_type: str              # Full-time, Intern, Contract, Permanent
    experience_level: str      # Junior, Senior, Mid-level
    description: str           # Full job description
    # ... and more fields
```

### 3. **Extraction Methods**
- **CSS Selectors**: Primary extraction method
- **JSON-LD Parsing**: For structured data (LinkedIn)
- **Pattern Matching**: For SkillsFuture specific patterns
- **Text Analysis**: Fallback method

## Available Information by Site

### LinkedIn
- ✓ Job title, company, location
- ✓ Job description
- ✓ Job type (Full-time, Intern, etc.)
- ✓ Experience level
- ✓ Industry/sector
- ✗ Salary (rarely available)
- ✗ Application deadline

### SkillsFuture
- ✓ Job title, company, location
- ✓ Salary range ✓
- ✓ Job type (Permanent, Contract, etc.) ✓
- ✓ Seniority level (Executive, Professional)
- ✓ Application deadline ✓
- ✓ Last updated date ✓
- ✓ Job sector/category
- ✓ Requirements, skills, responsibilities

## Usage

### 1. Extract Single Job
```python
from job_detail_extraction.engine import JobDetailExtractionEngine

engine = JobDetailExtractionEngine()
result = engine.extract_single_job(
    url="https://www.linkedin.com/jobs/view/4143856014",
    job_role="AI Engineer",
    suffix="Associate"
)
```

### 2. Batch Extraction from Database
```python
from job_detail_extraction.engine import JobDetailExtractionEngine
from job_detail_extraction.database import JobDetailDatabase

database = JobDetailDatabase(supabase_client)
engine = JobDetailExtractionEngine(database=database)

# Extract 50 jobs from database
results = engine.extract_from_database(limit=50, website="LinkedIn")
```

### 3. CLI Interface
```bash
# Extract single URL
python job_detail_extraction/main.py --url "https://www.linkedin.com/jobs/view/4143856014"

# Batch extract from database
python job_detail_extraction/main.py --batch --limit 20 --website LinkedIn
```

## Database Integration

The component updates the `job_listings` table with extracted details:
- Sets `extracted = True` when successful
- Updates fields like `job_title`, `company`, `salary_range`, etc.
- Stores `extracted_at` timestamp
- Tracks errors in `extraction_error`

## Configuration

Modify `config.py` to adjust:
- Browser settings (headless mode, timeouts)
- CSS selectors for each site
- Retry logic and delays
- Extraction preferences

## Analysis Tools

The component includes analysis scripts:
- `analyze_job_pages.py`: Basic structure analysis
- `detailed_job_analysis.py`: Deep analysis of page structure

## Future Enhancements

1. **More Websites**: Add extractors for Indeed, Glassdoor, etc.
2. **AI Extraction**: Use LLMs for better text understanding
3. **Salary Normalization**: Convert salary ranges to standardized format
4. **Skill Extraction**: Parse skills from descriptions
5. **Company Information**: Enrich with company data from APIs

## Dependencies

- `scraper.browser_manager`: For browser automation
- `loguru`: For logging
- `Supabase`: For database operations (optional)

## Notes

- LinkedIn often requires login for full access
- SkillsFuture has rate limiting
- Some fields may not be available on all job postings
- Extraction success depends on website structure stability
## Database Schema

### Table 1: `job_listings` (Existing)
Stores basic job information from URL scraping:
```sql
url TEXT PRIMARY KEY,
website TEXT,
job_role TEXT,
scraped_at TIMESTAMPTZ,
extracted BOOLEAN DEFAULT FALSE,
job_sector TEXT,
location TEXT,
experience_level TEXT,
date_posted TEXT,
suffix TEXT
```

### Table 2: `job_details` (New)
Stores detailed job information from page extraction:
```sql
-- Primary key and foreign key
url TEXT PRIMARY KEY REFERENCES job_listings(url),

-- Basic job information
job_title TEXT,
company TEXT,
location TEXT,

-- Dates
date_posted TEXT,
last_updated TEXT,
application_deadline TEXT,

-- Employment terms
job_type TEXT,  -- Full-time, Part-time, Intern, Contract, Permanent
experience_level TEXT,  -- Junior, Senior, Mid-level, Entry-level
seniority_level TEXT,  -- Executive, Professional, Manager, etc.
salary_range TEXT,  -- e.g., "$6,000 to $7,800 Monthly"

-- Classification
industry TEXT,
job_sector TEXT,
category TEXT,

-- Content
description TEXT,
requirements TEXT,
skills TEXT,
responsibilities TEXT,

-- Technical fields
extracted_at TIMESTAMPTZ DEFAULT NOW(),
success BOOLEAN DEFAULT FALSE,
error_message TEXT,
raw_data JSONB  -- Store raw extracted data
```

### Relationship
- `job_details.url` → `job_listings.url` (Foreign Key)
- When extraction succeeds: `job_listings.extracted = TRUE`
- Failed extractions can be retried

## Database Operations

The `JobDetailDatabase` class handles:
1. **Saving extracted details** to `job_details` table
2. **Updating extraction status** in `job_listings` table
3. **Getting jobs to extract** (unextracted or failed)
4. **Generating extraction statistics**

## Running the Extraction

```bash
# Test extraction (no database)
python job_detail_extraction/test_extraction.py

# Integration test
python job_detail_extraction/integration_test.py

# Extract from database (requires Supabase client)
python job_detail_extraction/main.py --batch --limit 20 --website LinkedIn
```

## Setting Up Supabase Client

To connect to your database, you'll need to set up a Supabase client:

```python
import os
from supabase import create_client
from job_detail_extraction.database import JobDetailDatabase

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Create database instance
database = JobDetailDatabase(supabase_client=supabase)
```