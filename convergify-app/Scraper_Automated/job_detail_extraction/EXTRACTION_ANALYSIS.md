# Job Detail Extraction - Analysis Results

## Verified URLs Tested
- **MyCareersFuture**: https://www.mycareersfuture.gov.sg/job/information-technology/ai-engineer-full-stack-developer-iotalents-06fdb1899a115964d985219a2b6c2072
- **LinkedIn**: https://www.linkedin.com/jobs/view/4143856014

---

## MyCareersFuture - Available Data

### ✅ Successfully Extracted Fields

| Field | Selector | Example Value |
|-------|----------|---------------|
| **Job Title** | `h1` | "AI Engineer / Full-Stack Developer" |
| **Salary** | `.salary` | "$4,000to$5,500 Monthly" |
| **Job Type** | `[class*='employment']` | "Permanent" |
| **Description** | `[data-testid='job-description']` | Full description available |

### 📋 Available data-testid Attributes

**Job Details:**
- `job-details-info-job-title`
- `job-details-info-employment-type`
- `job-details-info-seniority`
- `job-details-info-min-experience`
- `job-details-info-location-span`
- `job-details-info-job-categories`
- `job-details-info-last-posted-date`
- `job-details-info-job-expiry-date`
- `job-details-info-num-of-applications`
- `job-details-info-job-post-id`

**Salary:**
- `salary-info`
- `salary-range`
- `salary-type`
- `salary-desc`

**Company:**
- `company-info-logo`
- `company-info-about`
- `company-info-write-up`
- `company-info-more-jobs`
- `company-hire-info`

**Skills:**
- `skills-info`
- `skills-needed`
- `skill-matched-desc`

**Description:**
- `job-description`
- `description-content`

### 🎯 Recommended Selectors for MyCareersFuture

```python
MYCAREERSFUTURE_SELECTORS = {
    # Primary selectors using data-testid (most reliable)
    "job_title": "[data-testid='job-details-info-job-title']",
    "employment_type": "[data-testid='job-details-info-employment-type']",
    "seniority": "[data-testid='job-details-info-seniority']",
    "experience": "[data-testid='job-details-info-min-experience']",
    "location": "[data-testid='job-details-info-location-span']",
    "category": "[data-testid='job-details-info-job-categories']",
    "date_posted": "[data-testid='job-details-info-last-posted-date']",
    "expiry_date": "[data-testid='job-details-info-job-expiry-date']",
    "num_applications": "[data-testid='job-details-info-num-of-applications']",
    
    # Salary
    "salary_range": "[data-testid='salary-range']",
    "salary_type": "[data-testid='salary-type']",
    
    # Description
    "description": "[data-testid='job-description']",
    
    # Skills
    "skills": "[data-testid='skills-needed']",
    
    # Company
    "company_about": "[data-testid='company-info-about']",
    
    # Fallback selectors
    "job_title_fallback": "h1",
    "salary_fallback": ".salary",
    "employment_type_fallback": "[class*='employment']",
}
```

---

## LinkedIn - Available Data

### ✅ Successfully Extracted Fields

| Field | Selector | Example Value |
|-------|----------|---------------|
| **Job Title** | `.top-card-layout__title` | "Machine Learning Engineer - Singapore" |
| **Company** | `.topcard__org-name-link` | "WeRide" |
| **Description** | `.description__text` | Full description available |

### 📋 Job Criteria Available

From `.description__job-criteria-item`:
- **Seniority level**: "Not Applicable"
- **Employment type**: "Full-time"
- **Job function**: "Engineering and Information Technology"
- **Industries**: "Technology, Information and Internet"

### 🎯 Recommended Selectors for LinkedIn

```python
LINKEDIN_SELECTORS = {
    # Basic info
    "job_title": ".top-card-layout__title",
    "company": ".topcard__org-name-link",
    "location": ".topcard__flavor--bullet",
    "date_posted": ".posted-time-ago__text",
    
    # Description
    "description": ".description__text",
    
    # Job criteria (need to parse from items)
    "job_criteria_items": ".description__job-criteria-item",
    "criteria_header": ".description__job-criteria-subheader",
    "criteria_text": ".description__job-criteria-text",
}
```

---

## Comparison: What's Available on Each Site

### Common Fields (Both Sites)
- ✅ Job Title
- ✅ Job Description
- ✅ Employment Type (Full-time, Permanent, etc.)
- ✅ Location

### MyCareersFuture Exclusive
- ✅ **Salary Range** (e.g., "$4,000 to $5,500 Monthly")
- ✅ **Application Deadline** (Expiry date)
- ✅ **Last Posted Date**
- ✅ **Number of Applications**
- ✅ **Seniority Level** (Executive, Professional, etc.)
- ✅ **Minimum Experience Required**
- ✅ **Skills Needed** (structured list)
- ✅ **Company Information** (About, write-up)

### LinkedIn Exclusive
- ✅ **Job Function** (Engineering and Information Technology)
- ✅ **Industries** (Technology, Information and Internet)
- ❌ Salary (rarely available)
- ❌ Application deadline

---

## Recommended Fields to Extract (Prioritized)

### Priority 1: Essential Fields (Both Sites)
1. **Job Title** - Available on both
2. **Company Name** - Available on both
3. **Location** - Available on both
4. **Job Description** - Available on both
5. **Employment Type** - Available on both (Full-time, Intern, Contract, Permanent)

### Priority 2: High-Value Fields (Site-Specific)
6. **Salary Range** - MyCareersFuture only ⭐
7. **Application Deadline** - MyCareersFuture only ⭐
8. **Date Posted** - MyCareersFuture only
9. **Experience Level** - MyCareersFuture (min experience), LinkedIn (seniority)
10. **Skills Required** - MyCareersFuture only ⭐

### Priority 3: Classification Fields
11. **Job Category** - MyCareersFuture
12. **Industry** - LinkedIn
13. **Seniority Level** - MyCareersFuture

### Priority 4: Additional Context
14. **Number of Applications** - MyCareersFuture
15. **Company About** - MyCareersFuture
16. **Job Function** - LinkedIn

---

## Implementation Strategy

### Phase 1: Core Extraction (Implement First)
Use `data-testid` selectors for MyCareersFuture (most reliable):
- Job title, company, location
- Salary range
- Employment type
- Description
- Application deadline
- Date posted

Use class selectors for LinkedIn:
- Job title, company, location
- Description
- Parse job criteria items for employment type, seniority, industry

### Phase 2: Enhanced Extraction
- Skills extraction (MyCareersFuture)
- Experience requirements
- Number of applications
- Company information

### Phase 3: Data Normalization
- Standardize employment types (Full-time, Part-time, Intern, Contract, Permanent)
- Normalize salary formats
- Parse and standardize dates
- Extract experience years from text

---

## Database Schema Recommendations

Based on available data, add these fields to `job_listings` table:

```sql
-- Core fields (already exist)
url TEXT PRIMARY KEY
website TEXT
job_role TEXT
job_title TEXT
company TEXT
location TEXT

-- New fields to add
salary_range TEXT              -- "$4,000 to $5,500 Monthly"
employment_type TEXT           -- "Full-time", "Permanent", "Contract", "Intern"
seniority_level TEXT           -- "Executive", "Professional", "Manager"
min_experience TEXT            -- "3 years", "Fresh graduate"

-- Dates
date_posted TEXT
last_updated TEXT
application_deadline TEXT

-- Classification
job_category TEXT              -- "Information Technology"
industry TEXT                  -- "Technology, Information and Internet"
job_function TEXT              -- "Engineering and Information Technology"

-- Content
description TEXT
skills_required TEXT           -- Comma-separated or JSON
requirements TEXT

-- Metadata
num_applications INTEGER       -- MyCareersFuture only
company_about TEXT
extracted BOOLEAN DEFAULT FALSE
extracted_at TIMESTAMP
```

---

## Next Steps

1. ✅ **Verified actual page structure** - DONE
2. ⏭️ **Update extractors** with correct selectors (data-testid for MCF)
3. ⏭️ **Test extraction** on multiple URLs
4. ⏭️ **Add database migration** for new fields
5. ⏭️ **Implement batch extraction** from existing URLs
6. ⏭️ **Add data normalization** layer

---

## Notes

- MyCareersFuture uses `data-testid` attributes extensively - these are the most reliable selectors
- LinkedIn structure is more class-based and may change more frequently
- MyCareersFuture has significantly more structured data available
- Salary information is a key differentiator for MyCareersFuture
- Both sites are JavaScript-rendered, requiring browser automation