# Career Analysis Platform - Backend

FastAPI backend for the career analysis platform with resume processing, job scraping, and AI-powered skill analysis.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- SQLite (included with Python)
- Google Gemini API key (13 keys configured for rotation)

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY(s)
```

3. **Initialize database:**
```bash
python init_db.py
```

4. **Run migrations:**
```bash
python -m alembic upgrade head
```

5. **Start the server:**
```bash
python main.py
```

The API will be available at http://localhost:8000

### Optional: Add Sample Data
```bash
python scripts/add_sample_jobs.py
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
backend/
├── main.py                    # FastAPI application entry point
├── config.py                  # Configuration settings with Pydantic
├── database.py                # SQLAlchemy engine and session management
├── init_db.py                 # Database initialization script
├── requirements.txt           # Python dependencies
├── alembic.ini               # Alembic configuration
│
├── api/                      # API route handlers
│   ├── analysis.py           # Analysis endpoints (create, status, results)
│   ├── job.py                # Job management endpoints
│   ├── resume.py             # Resume management endpoints
│   └── session.py            # Session management endpoints
│
├── models/                   # SQLAlchemy ORM models
│   ├── analysis.py           # Analysis model with JSON results
│   ├── job.py                # Job and JobGroup models
│   ├── resume.py             # Resume and OptimizedResume models
│   ├── session.py            # AnalysisSession model
│   ├── skill_canonical.py    # Skill canonicalization cache (NEW)
│   ├── celery_task.py        # Background task tracking
│   └── user.py               # User model
│
├── schemas/                  # Pydantic schemas for validation
│   ├── analysis.py           # Analysis request/response schemas
│   ├── job.py                # Job DTOs
│   ├── resume.py             # Resume DTOs
│   ├── session.py            # Session DTOs
│   └── common.py             # Shared schemas
│
├── services/                 # Business logic services
│   ├── analysis_service.py   # Analysis orchestration
│   ├── job_service.py        # Job management and filtering
│   ├── resume_service.py     # Resume parsing and management
│   ├── optimization_service.py # Resume optimization
│   ├── cache_service.py      # Skill classification caching
│   ├── export_service.py     # Export functionality (JSON/PDF)
│   ├── file_service.py       # File upload/download handling
│   └── celery_service.py     # Background task management
│
├── engines/                  # Modular analysis engines
│   ├── gemini_client.py      # LLM client with API key rotation
│   ├── config.py             # Engine configuration
│   │
│   ├── skill_extraction/     # Extract skills from text
│   │   ├── extractor.py      # Main extraction logic
│   │   └── models.py         # Extraction data models
│   │
│   ├── skill_classification/ # Classify and categorize skills
│   │   ├── classifier.py     # Batch classification with normalization
│   │   ├── taxonomy.py       # Skill taxonomy and categories
│   │   └── models.py         # Classification data models
│   │
│   ├── strategic_analysis/   # Career analysis and recommendations
│   │   ├── analyzer.py       # Semantic matching with canonical grouping
│   │   ├── evidence_extractor.py # Extract evidence from resume
│   │   └── models.py         # Analysis data models
│   │
│   └── resume_optimizer/     # Resume improvement suggestions
│       ├── optimizer.py      # Optimization logic
│       ├── diff_generator.py # Generate before/after diff
│       └── models.py         # Optimizer data models
│
├── scraper/                  # Job scraping module
│   ├── scraper.py            # Main scraper orchestration
│   ├── browser_manager.py   # Playwright browser lifecycle
│   ├── search_handler.py     # Search functionality
│   ├── sample_extractor.py   # Job data extraction
│   ├── config.py             # Scraper configuration
│   └── models.py             # Scraper data models
│
├── alembic/                  # Database migrations
│   ├── versions/             # Migration scripts (0001-0008)
│   │   ├── 0001_initial_migration.py
│   │   ├── 0002_add_sessions_table.py
│   │   ├── 0003_add_employment_type_to_jobs.py
│   │   ├── 0004_add_group_type_to_job_groups.py
│   │   ├── 0005_add_skills_processed_to_jobs.py
│   │   ├── 0006_add_analysis_type_to_analyses.py
│   │   ├── 0007_add_skill_classification_cache.py
│   │   └── 0008_add_skill_canonical_cache.py (NEW)
│   └── env.py                # Alembic environment
│
├── scripts/                  # Utility scripts
│   ├── add_sample_jobs.py    # Add test data
│   ├── generate_analysis_report.py # Report generation
│   ├── clear_empty_cache.py  # Cache maintenance
│   └── extract_analysis_data.py # Data extraction
│
├── uploads/                  # File upload storage
│   ├── resumes/              # Uploaded resumes (UUID filenames)
│   └── temp/                 # Temporary file processing
│
├── docs/                     # Backend documentation
│   ├── DATABASE_SCHEMA.md    # Database schema documentation
│   ├── FOLDER_STRUCTURE.md   # Detailed folder structure
│   └── API_KEY_ROTATION.md   # API key rotation guide
│
├── tests/                    # Test files
│   ├── test_analysis_timing.py
│   └── test_quota_all_keys.py
│
└── Subprocess Scripts        # Analysis subprocess scripts
    ├── run_analysis_strategic.py  # Strategic analysis (primary)
    ├── run_analysis_simple.py     # Simple analysis (legacy)
    └── run_scraper.py             # Job scraping subprocess
```

## 🔧 Core Features

### 1. Resume Processing
- Upload PDF/TXT/DOCX resumes
- Extract text content
- Parse skills and experience
- Store with UUID filenames

### 2. Job Management
- Manual job entry
- Web scraping from MyCareersFuture
- Job grouping and organization
- Employment type filtering

### 3. Strategic Analysis
- **Semantic skill matching** using Gemini 2.5 Flash (not keyword matching)
- **Canonical skill grouping** - groups related skills (e.g., "AI", "Generative AI", "Machine Learning" → "Artificial Intelligence & Machine Learning")
- **Evidence extraction** - finds proof of skills in resume with confidence scores
- **Market intelligence** - analyzes demand across jobs with aggregated frequencies
- **Prioritized skill gaps** - identifies critical missing skills with ROI scores
- **Actionable recommendations** - provides specific next steps with action items

### 4. Skill Canonicalization
- **Database caching** - stores canonical skill mappings in `skill_canonical_cache` table
- **Semantic grouping** - "Generative AI", "AI Agents", "Machine Learning" → "Artificial Intelligence & Machine Learning"
- **Frequency aggregation** - accurate demand scores (e.g., 100% vs 10% for AI skills across 10 jobs)
- **38+ seed mappings** - pre-loaded common skills (AI/ML, React, Node.js, cloud platforms)
- **Auto-learning** - cache grows automatically with each analysis
- **Single LLM call** - integrated into semantic matching step (no additional API costs)

### 5. Resume Optimization
- Generate improved resume based on analysis
- Show before/after comparison
- Highlight changes and improvements
- Export optimized version

## 🗄️ Database

### Schema
The application uses SQLite with the following main tables:

**Core Tables:**
- `users` - User accounts
- `resumes` - Uploaded resume data with text content
- `optimized_resumes` - Generated optimized resumes
- `jobs` - Job postings with skills and employment type
- `job_groups` - Job organization and grouping
- `analyses` - Analysis metadata and results (JSON)
- `sessions` - Analysis session tracking

**Cache Tables:**
- `skill_canonical_cache` - Canonical skill mappings (NEW)
- `jobs.classified_skills` - Cached extracted skills per job

### Key Features
- **JSON storage** - Complex data stored as JSON in TEXT columns
- **Property getters** - Automatic JSON parsing via SQLAlchemy properties
- **Relationships** - Foreign keys with cascade deletes
- **Indexes** - Optimized for common queries

### Migrations
Database migrations are managed with Alembic:

```bash
# Apply all migrations
python -m alembic upgrade head

# Check current version
python -m alembic current

# Create new migration
python -m alembic revision --autogenerate -m "description"

# Rollback one migration
python -m alembic downgrade -1

# Stamp database (if tables already exist)
python -m alembic stamp head
```

### Database Location
- **Development**: `backend/career_analysis.db`
- **Documentation**: See `docs/ANALYSIS_DATABASE_STRUCTURE.md`

## 🔌 API Endpoints

### Resumes
- `POST /api/resumes/` - Upload resume (multipart/form-data)
- `GET /api/resumes/` - List resumes with filters
- `GET /api/resumes/{id}` - Get resume details
- `DELETE /api/resumes/{id}` - Delete resume
- `GET /api/resumes/{id}/download` - Download original file

### Jobs
- `GET /api/jobs/` - List jobs (with filters: company, location, source)
- `POST /api/jobs/` - Create job manually
- `GET /api/jobs/{id}` - Get job details
- `DELETE /api/jobs/{id}` - Delete job
- `POST /api/jobs/scrape` - Start job scraping (async)
- `GET /api/jobs/groups` - List job groups
- `POST /api/jobs/groups` - Create job group

### Analysis
- `POST /api/analyses/` - Create and start analysis (async)
- `GET /api/analyses/{id}/status` - Get real-time status with progress
- `GET /api/analyses/{id}/results` - Get full analysis results
- `GET /api/analyses/{id}` - Get analysis metadata
- `GET /api/analyses/` - List analyses with filters
- `DELETE /api/analyses/{id}` - Delete analysis
- `POST /api/analyses/{id}/retry` - Retry failed analysis
- `POST /api/analyses/{id}/cancel` - Cancel running analysis
- `GET /api/analyses/{id}/recommendations` - Get just recommendations
- `GET /api/analyses/{id}/skill-gaps` - Get just skill gaps
- `POST /api/analyses/{id}/export` - Export results (JSON/PDF)

### Sessions
- `POST /api/sessions/` - Create session
- `GET /api/sessions/` - List sessions
- `GET /api/sessions/{id}` - Get session details
- `PUT /api/sessions/{id}` - Update session
- `DELETE /api/sessions/{id}` - Delete session

## 🔄 Analysis Flow

### Strategic Analysis (Primary)

1. **User creates analysis** → API receives resume_id + job_ids
2. **Subprocess spawned** → `run_analysis_strategic.py` runs in background
3. **Skill extraction** → Extract skills from jobs (with caching in `jobs.classified_skills`)
4. **Skill classification** → Batch classify all skills with normalization using Gemini 2.5 Flash
5. **Resume parsing** → Extract skills from resume text
6. **Semantic matching + Canonical grouping** → Single LLM call to:
   - Match resume skills to job skills semantically (not keyword matching)
   - Group related skills under canonical names (e.g., "AI" variants → "Artificial Intelligence & Machine Learning")
   - Calculate aggregated demand frequencies
   - Cache canonical mappings to database
7. **Evidence extraction** → Find proof of skills in resume with confidence scores
8. **Market intelligence** → Analyze demand, trends, competition using canonical groups
9. **Skill gap prioritization** → Rank missing skills by importance × market demand
10. **Recommendations** → Generate actionable next steps with specific action items
11. **Resume optimization** → Create improved resume version (optional)
12. **Results saved** → Store in database as JSON in `analyses.results`
13. **Frontend displays** → Real-time progress → Final results with canonical skill visualization

### Performance
- **With 10 jobs (cached)**: ~3-4 minutes
- **With 10 jobs (first run)**: ~5-8 minutes
- **Timeout**: 20 minutes
- **Progress tracking**: Real-time updates via status endpoint

## 🧠 AI/LLM Integration

### Gemini API Configuration
- **Primary model**: `gemini-2.5-flash` (65K output tokens)
- **Fallback model**: `gemma-3-27b-it` (8K output tokens)
- **API key rotation**: 13 keys configured for quota management
- **Automatic retry**: Rotates keys on quota errors
- **Fail loudly**: No silent fallbacks - errors are reported

### Key Rotation Strategy
```python
# Configured in .env
GEMINI_API_KEY=key1
GEMINI_API_KEY1=key2
GEMINI_API_KEY2=key3
# ... up to GEMINI_API_KEY19
```

**Benefits:**
- Increased quota (13x)
- Automatic failover
- No manual intervention
- Logged rotation events

### LLM Usage
1. **Skill Extraction** - Extract skills from job descriptions
2. **Skill Classification** - Classify skills into categories
3. **Semantic Matching** - Match resume skills to job skills
4. **Canonical Grouping** - Group related skills semantically
5. **Evidence Extraction** - Find skill evidence in resume
6. **Resume Optimization** - Generate improved resume

## 🕷️ Job Scraping

The scraper uses Playwright to scrape jobs from MyCareersFuture:

```bash
# Via API endpoint
POST /api/jobs/scrape
{
  "search_terms": ["Software Engineer"],
  "employment_type": "full-time",
  "max_jobs": 10
}
```

**Features:**
- Headless browser automation
- Keyboard navigation for reliability
- Employment type filtering
- Configurable job limits
- Error handling and retries

**Performance:**
- ~2-5 minutes for 10 jobs
- Runs as background subprocess
- Progress tracking available

## ⚙️ Configuration

### Environment Variables
Create a `.env` file (copy from `.env.example`):

```bash
# Gemini API Keys (required for analysis)
GEMINI_API_KEY=your_primary_key
GEMINI_API_KEY1=your_key_2
GEMINI_API_KEY2=your_key_3
# ... add up to GEMINI_API_KEY19

# Database
DATABASE_URL=sqlite:///./career_analysis.db

# Server
PORT=8000
HOST=0.0.0.0

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=pdf,txt,docx

# CORS
FRONTEND_URL=http://localhost:5173
```

### Engine Configuration
Located in `engines/config.py`:
- Model selection
- Temperature settings
- Token limits
- Retry configuration
- Threshold values

## 🧪 Testing

### Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# List jobs
curl http://localhost:8000/api/jobs/

# List resumes
curl http://localhost:8000/api/resumes/

# Get analysis status
curl http://localhost:8000/api/analyses/{id}/status
```

### Database Queries
```bash
# Open database
sqlite3 career_analysis.db

# List tables
.tables

# Count records
SELECT COUNT(*) FROM jobs;
SELECT COUNT(*) FROM resumes;
SELECT COUNT(*) FROM analyses;

# Check canonical cache
SELECT COUNT(*) FROM skill_canonical_cache;
SELECT * FROM skill_canonical_cache WHERE canonical_name LIKE '%AI%';

# View recent analyses
SELECT id, status, created_at, job_count FROM analyses ORDER BY created_at DESC LIMIT 5;
```

### Test Scripts
```bash
# Test analysis timing
python tests/test_analysis_timing.py

# Test API key quota
python tests/test_quota_all_keys.py

# Test with 9 jobs
python tests/test_9_jobs.py
```

## 🐛 Troubleshooting

### Server Issues
**Server won't start:**
- Check Python version: `python --version` (need 3.11+)
- Check port 8000 is free: `netstat -an | findstr 8000`
- Check dependencies: `pip install -r requirements.txt`
- Check .env file exists with API keys

**Import errors:**
- Ensure virtual environment activated
- Check Python path includes backend directory
- Verify all dependencies installed

### Database Issues
**Migration errors:**
- Check current version: `python -m alembic current`
- Stamp if tables exist: `python -m alembic stamp head`
- Reinitialize if needed: `python init_db.py`

**Locked database:**
- Close all connections
- Restart server
- Check for zombie processes

### Analysis Issues
**Analysis fails:**
- Check API keys in .env
- Check subprocess script exists: `run_analysis_strategic.py`
- Check database has resume and jobs
- Check backend logs for errors
- Verify Gemini API quota

**Analysis timeout:**
- Default timeout is 20 minutes
- Check if LLM API is responding
- Reduce number of jobs for testing
- Check API key rotation is working

**Canonical grouping not working:**
- Check `skill_canonical_cache` table exists
- Run migration: `python -m alembic upgrade head`
- Check cache has seed data: `SELECT COUNT(*) FROM skill_canonical_cache;`
- Should have 38+ entries

### Scraping Issues
**Scraper fails:**
- Check Playwright installed: `playwright install`
- Check browser drivers: `playwright install chromium`
- Check network connection
- Verify MyCareersFuture site is accessible

## 📦 Dependencies

### Core Framework
- **FastAPI** 0.104.1 - Web framework with automatic OpenAPI docs
- **Uvicorn** - ASGI server with hot reload
- **SQLAlchemy** 2.0.23 - ORM for database operations
- **Alembic** 1.12.1 - Database migrations
- **Pydantic** 2.5.0 - Data validation and settings

### File Processing
- **PyPDF2** - PDF parsing
- **pdfplumber** - Advanced PDF extraction
- **python-multipart** - File upload handling
- **python-docx** - DOCX parsing

### Web Scraping
- **Playwright** 1.40.0 - Browser automation
- **BeautifulSoup4** - HTML parsing

### AI/LLM
- **google-generativeai** 0.3.2 - Gemini API client

### Utilities
- **python-dotenv** - Environment variable management
- **pytest** 7.4.3 - Testing framework

## 🚀 Deployment

### Production Checklist
- [ ] Set all environment variables
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up reverse proxy (nginx/Apache)
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure CORS for production domain
- [ ] Set up logging and monitoring
- [ ] Use Gunicorn for production server
- [ ] Set up automated backups
- [ ] Configure rate limiting
- [ ] Set up error tracking (Sentry)

### Production Server
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 1200 \
  --access-logfile - \
  --error-logfile -
```

### Database Migration
```bash
# Backup SQLite
cp career_analysis.db career_analysis.db.backup

# Export data
python scripts/export_data.py

# Switch to PostgreSQL
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Run migrations
python -m alembic upgrade head

# Import data
python scripts/import_data.py
```

## 🔐 Security

### Implemented
- ✅ File upload validation (extension, size)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CORS configuration for frontend origin
- ✅ Path sanitization (prevent directory traversal)
- ✅ UUID filenames (prevent filename attacks)
- ✅ API key rotation (prevent quota exhaustion)

### Recommended for Production
- [ ] Authentication and authorization
- [ ] Rate limiting per user/IP
- [ ] Input sanitization and validation
- [ ] HTTPS only
- [ ] Secure headers (HSTS, CSP, etc.)
- [ ] API key encryption at rest
- [ ] Audit logging
- [ ] Regular security updates

## 📊 Monitoring

### Logs
- **Application logs**: stdout/stderr
- **Access logs**: Uvicorn/Gunicorn
- **Error logs**: Python logging module
- **Analysis logs**: Subprocess stderr

### Metrics to Track
- API response times
- Analysis completion times
- LLM API usage and costs
- Cache hit rates
- Error rates
- Database query performance

## 📝 Notes

- Analysis runs as subprocess (not Celery) for simplicity
- Progress tracking is in-memory (lost on restart)
- File uploads stored in `uploads/` directory
- Database is SQLite (upgrade to PostgreSQL for production)
- Canonical cache grows automatically with each analysis
- API key rotation is automatic and logged

## 📚 Additional Documentation

- **Database Structure**: `docs/ANALYSIS_DATABASE_STRUCTURE.md`
- **Folder Structure**: `docs/FOLDER_STRUCTURE.md`
- **API Key Rotation**: `docs/API_KEY_ROTATION.md`
- **Critical Lessons**: `../docs/CRITICAL_LESSONS_LEARNED.md`
- **Analysis Process**: `../docs/ANALYSIS_PROCESS_EXPLAINED.md`
- **Analysis Results**: `../docs/ANALYSIS_RESULTS_COMPREHENSIVE.md`

## 📄 License

This project is for educational purposes.

---

**Backend is ready to power intelligent career analysis!** 🚀
