# Job Scraper - Automated LinkedIn & Skills Career Scraper

A production-ready web scraper for collecting job postings from LinkedIn and MyCareersFuture (Skills Career) in Singapore.

## Features

- **Dual Platform Support**: Scrapes both LinkedIn and Skills Career
- **Pagination**: Automatically handles pagination to collect all available jobs
- **Suffix Expansion**: LinkedIn-specific strategy to maximize job discovery (5x data increase)
- **URL Normalization**: Removes tracking parameters and prevents duplicates
- **Job Role Separation**: Automatically separates base roles and suffixes in database
- **Deduplication**: Tracks and prevents duplicate job URLs
- **Stealth Mode**: Advanced browser fingerprinting protection
- **Database Storage**: Supabase database with metadata tracking
- **Configurable**: Environment variables for easy configuration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

Create a `.env` file (or use the existing one):

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Scraper Configuration
HEADLESS_MODE=true
TIMEOUT_SECONDS=30
MAX_PAGES=20
DELAY_BETWEEN_REQUESTS=2
```

### 3. Run Job Search

**LinkedIn with Suffix Expansion (Recommended):**
```bash
python scrape_linkedin_with_suffixes.py
```

**Skills Career:**
```bash
python scrape_skills_career.py --job-title "AI Engineer" --max-urls 100
```

### 4. Run Bulk Scraping (All 30 Roles)

```bash
python bulk_scrape_all_roles.py
```

This will scrape all 30 predefined job roles from both platforms.

## Key Results

### Pagination Performance
- **LinkedIn**: ~55 jobs per page, supports up to 1000+ jobs per search
- **Skills Career**: 20 jobs per page, typically 100-200 jobs per search

### Suffix Expansion Strategy (LinkedIn Only)

LinkedIn's exact-match bias means different search terms return completely different results:

**Example: "Software Engineer"**
- Base search: 60 jobs
- With top 5 suffixes: 300+ unique jobs (5x increase!)
- **Zero overlap** between suffix variations

**Recommended Top 5 Suffixes:**
1. `` (base role) - 60 jobs
2. ` Intern` - 60 jobs
3. ` Internship` - 60 jobs
4. ` Graduate` - 60 jobs
5. ` Junior` - 58 jobs

### URL Normalization
- Removes LinkedIn tracking parameters (refId, trackingId)
- Normalizes to clean format: `https://www.linkedin.com/jobs/view/{job_id}/`
- Prevents duplicate entries from same job with different tracking URLs

### Job Role and Suffix Separation
- Automatically separates "Software Engineer Intern" into:
  - `job_role`: "Software Engineer"
  - `suffix`: "Intern"
- Enables better querying and analytics
- Jobs without suffixes have `suffix` = NULL

## Project Structure

```
Scraper_Automated/
├── scraper/
│   ├── database/
│   │   └── job_database.py          # Supabase database handler
│   ├── linkedin_scraper.py          # LinkedIn scraper implementation
│   ├── suffix_parser.py             # Job role and suffix separation
│   ├── url_normalizer.py            # URL normalization utility
│   ├── browser_manager.py           # Playwright browser control
│   ├── url_scraper.py               # Pagination handler
│   └── config.py                    # Configuration loader
├── scrape_linkedin_with_suffixes.py # Main LinkedIn scraper with suffix expansion
├── scrape_skills_career.py          # Skills Career CLI
├── bulk_scrape_all_roles.py         # Bulk scraper for 30 roles
├── count_jobs.py                     # Quick job counter
├── demo_visible_scraper.py          # Visible demo mode
├── search_job_id.py                 # Search for specific job ID
├── show_suffix_summary.py           # Database suffix summary
├── README.md                        # This file
├── SCRAPER_ARCHITECTURE.md          # Architecture documentation
├── SCRAPER_STATUS.md                # Status documentation
├── RECOMMENDED_SUFFIXES.md          # Suffix recommendations
├── SUFFIX_EXPANSION_GUIDE.md        # Detailed suffix strategy
├── SUFFIX_SEPARATION_COMPLETE.md    # Suffix separation summary
└── URL_DEDUPLICATION_SUMMARY.md     # URL normalization summary
```

## Advanced Usage

### Suffix Expansion for LinkedIn

The main LinkedIn scraper automatically uses suffix expansion with these recommended suffixes:

```python
# Default top 5 suffixes (built into scraper)
RECOMMENDED_SUFFIXES = [
    "",              # Base role
    " Intern",       # 60+ jobs
    " Internship",   # 60+ jobs  
    " Graduate",     # 60+ jobs
    " Junior",       # 58+ jobs
    " Associate",    # 58+ jobs
]

# Usage
from scrape_linkedin_with_suffixes import scrape_with_suffixes

# Scrape with automatic suffix expansion (5x data increase)
results = scrape_with_suffixes("AI Engineer", max_urls=100)
print(f"Total jobs found: {results['total_new']}")

# Custom suffixes for specific needs
intern_suffixes = ["", " Intern", " Internship", " Summer Intern"]
results = scrape_with_suffixes("Data Analyst", suffixes=intern_suffixes)
```

**Why Suffix Expansion Works:**
- LinkedIn uses exact-match bias - "AI Engineer" and "AI Engineer Intern" return completely different job sets
- Zero overlap between suffix variations (0% duplicate rate)
- 5x data increase with minimal API calls
- Only works for LinkedIn (not Skills Career)

### Custom Job Roles

Edit `bulk_scrape_all_roles.py` to modify the `JOB_ROLES` list:

```python
JOB_ROLES = [
    "AI Engineer",
    "Data Scientist", 
    "Software Engineer",
    # Add your roles here
]
```

### Database Queries

The scraper stores data in Supabase with automatic job role and suffix separation:

```python
from scraper.database.job_database import JobDatabase

db = JobDatabase()

# Get all AI Engineer jobs (any suffix)
jobs = db.get_urls_by_job_role("AI Engineer")

# Get all internship positions
result = db.supabase.table("job_listings").select("*").eq("suffix", "Intern").execute()
internships = result.data

# Get base-level positions (no suffix)
result = db.supabase.table("job_listings").select("*").is_("suffix", "null").execute()
base_jobs = result.data
```

**Database Schema:**
```sql
CREATE TABLE job_listings (
    url TEXT PRIMARY KEY,           -- Normalized: https://www.linkedin.com/jobs/view/{job_id}/
    website TEXT NOT NULL,          -- "LinkedIn" or "SkillsCareer"
    job_role TEXT NOT NULL,         -- Clean base role: "Software Engineer"
    suffix TEXT,                    -- Job level: "Intern" or NULL
    scraped_at TIMESTAMP WITH TIME ZONE NOT NULL,
    extracted BOOLEAN DEFAULT FALSE,
    job_sector TEXT,
    location TEXT,
    experience_level TEXT,
    date_posted TEXT
);
```

**Key Features:**
- **URL Normalization**: Removes tracking parameters (refId, trackingId) to prevent duplicates
- **Job Role Separation**: "Software Engineer Intern" → job_role: "Software Engineer", suffix: "Intern"
- **Automatic Deduplication**: Same job with different URLs stored only once

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SUPABASE_URL` | - | Supabase project URL (required) |
| `SUPABASE_KEY` | - | Supabase API key (required) |
| `HEADLESS_MODE` | `true` | Run browser in headless mode |
| `TIMEOUT_SECONDS` | `30` | Page load timeout |
| `MAX_PAGES` | `20` | Maximum pages to scrape per search |
| `DELAY_BETWEEN_REQUESTS` | `2` | Delay between page requests (seconds) |

### CLI Arguments

**LinkedIn Suffix Scraper:**
```bash
python scrape_linkedin_with_suffixes.py
# Uses predefined base role and top 5 suffixes
```

**Skills Career Scraper:**
```bash
python scrape_skills_career.py \
  --job-title "Data Analyst" \
  --max-urls 50 \
  --employment-type fulltime
```

## Utility Scripts

### Count Jobs (No Scraping)
```bash
python count_jobs.py
```
Quickly counts available jobs without saving to database.

### Demo Visible Mode
```bash
python demo_visible_scraper.py
```
Runs scraper in visible mode to see browser automation in action.

### Search Specific Job ID
```bash
python search_job_id.py
```
Search for a specific LinkedIn job ID in the database.

### Show Suffix Summary
```bash
python show_suffix_summary.py
```
Display database summary grouped by job roles and suffixes.

## Best Practices

1. **Rate Limiting**: Use delays between requests to avoid IP bans
2. **Headless Mode**: Run in headless mode for production
3. **Suffix Strategy**: Use suffix expansion only for LinkedIn (not Skills Career)
4. **Database Backups**: Regularly backup Supabase database
5. **Error Handling**: Monitor logs for scraping failures
6. **URL Normalization**: All URLs are automatically normalized to prevent duplicates

## Troubleshooting

### Browser Not Found
```bash
playwright install chromium
```

### Rate Limited
- Increase `DELAY_BETWEEN_REQUESTS` in `.env`
- Reduce `MAX_PAGES`
- Use VPN or proxy

### No Results Found
- Check if job title is spelled correctly
- Try broader search terms
- Verify site is accessible

### Database Connection Issues
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check Supabase project status
- Ensure network connectivity

## System Architecture

### Current Active Scrapers

1. **LinkedIn with Suffix Expansion** ✅ PRODUCTION READY
   - Entry point: `scrape_linkedin_with_suffixes.py`
   - Features: 5x data increase, URL normalization, role/suffix separation
   - Performance: 300+ jobs per role

2. **Skills Career** ✅ PRODUCTION READY
   - Entry point: `scrape_skills_career.py`
   - Features: Full pagination, employment type filtering
   - Performance: 100-200 jobs per role

3. **Indeed** ⚠️ LIMITED (First page only)
   - Entry point: `scrape_indeed.py`
   - Limitation: Only 10-16 jobs per search (login required for pagination)
   - Use: Supplementary data only

### Shared Components
- `scraper/browser_manager.py` - Playwright with stealth mode
- `scraper/database/job_database.py` - Supabase integration
- `scraper/url_normalizer.py` - URL deduplication
- `scraper/suffix_parser.py` - Job role and suffix separation

## Performance Metrics

**Tested on "Software Engineer" (March 2026):**
- LinkedIn (with suffix expansion): 300+ jobs (5 suffix variations)
- Skills Career: 120 jobs (6 pages)
- Total: 420+ unique jobs
- Scraping time: ~4 minutes
- Duplicate rate: 0% (thanks to URL normalization)

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.
