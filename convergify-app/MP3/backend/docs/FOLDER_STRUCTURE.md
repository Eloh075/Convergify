# Backend Folder Structure

## Core Application Files

### Entry Points
- `main.py` - FastAPI application entry point (API server)
- `celery_app.py` - Celery worker for background tasks
- `config.py` - Application configuration
- `database.py` - Database connection and session management

### Analysis Scripts
- `run_analysis_strategic.py` - Strategic career analysis (main analysis engine)
- `run_analysis_simple.py` - Simple analysis (legacy/fallback)
- `run_scraper.py` - Job scraping script

### Database Management
- `init_db.py` - Initialize database schema
- `manage_db.py` - Database management utilities
- `alembic.ini` - Alembic migration configuration
- `load_scraped_jobs.py` - Load scraped job data into database
- `career_analysis.db` - SQLite database file

### Configuration
- `.env` - Environment variables (API keys, settings)
- `.env.example` - Example environment file
- `.gitignore` - Git ignore rules
- `requirements.txt` - Python dependencies

## Core Directories

### `/api`
FastAPI route handlers
- `analysis.py` - Analysis endpoints
- `job.py` - Job management endpoints
- `resume.py` - Resume upload/management endpoints
- `session.py` - Session management endpoints

### `/models`
SQLAlchemy database models
- `analysis.py` - Analysis results model
- `job.py` - Job posting model
- `resume.py` - Resume model
- `session.py` - Session model
- `user.py` - User model
- `celery_task.py` - Celery task tracking model

### `/schemas`
Pydantic validation schemas
- `analysis.py` - Analysis request/response schemas
- `job.py` - Job schemas
- `resume.py` - Resume schemas
- `session.py` - Session schemas
- `common.py` - Shared schemas

### `/services`
Business logic layer
- `analysis_service.py` - Analysis orchestration
- `job_service.py` - Job management
- `resume_service.py` - Resume processing
- `cache_service.py` - Caching layer for API calls
- `optimization_service.py` - Resume optimization
- `export_service.py` - Export functionality
- `file_service.py` - File handling
- `session_service.py` - Session management
- `celery_service.py` - Celery task management

### `/engines`
Core analysis engines (LLM-powered)
- `/skill_extraction` - Extract skills from text
- `/skill_classification` - Classify and categorize skills
- `/strategic_analysis` - Semantic matching and career analysis
- `/resume_optimizer` - Resume optimization engine
- `gemini_client.py` - Gemini/Gemma API client with key rotation
- `config.py` - Engine configuration

### `/adapters`
External service adapters
- `career_analysis_adapter.py` - Career analysis integration
- `job_scraping_adapter.py` - Job scraping integration
- `skill_classification_adapter.py` - Skill classification integration
- `skill_extraction_adapter.py` - Skill extraction integration

### `/scraper`
Job scraping functionality
- `scraper.py` - Main scraper logic
- `browser_manager.py` - Browser automation
- `search_handler.py` - Search functionality
- `sample_extractor.py` - Data extraction
- `models.py` - Scraper data models
- `config.py` - Scraper configuration

### `/tasks`
Celery background tasks
- `analysis_tasks.py` - Analysis background tasks
- `scraping_tasks.py` - Scraping background tasks

### `/alembic`
Database migrations
- `/versions` - Migration scripts
- `env.py` - Alembic environment
- `script.py.mako` - Migration template

### `/uploads`
User uploaded files
- `/resumes` - Uploaded resume files
- `/temp` - Temporary files

## Utility Directories

### `/tests`
Test files and test data
- `test_*.py` - Unit and integration tests
- `test_*.json` - Test data files

### `/scripts`
Utility scripts for development and debugging
- `check_*.py` - Diagnostic scripts
- `show_expected_results.py` - Display analysis results
- `clear_empty_cache.py` - Cache cleanup
- `generate_analysis_report.py` - Report generation
- `list_available_models.py` - List available LLM models
- `add_sample_jobs.py` - Add sample data

### `/docs`
Documentation files
- `API_KEY_ROTATION.md` - API key rotation documentation
- `DATABASE_SCHEMA.md` - Database schema documentation
- `DIAGNOSIS.md` - Troubleshooting guide
- `MODEL_VERIFICATION.md` - Model verification guide

## Key Features

### API Key Rotation
The system supports automatic rotation across 13 Gemini API keys to handle quota limits. See `engines/gemini_client.py` and `docs/API_KEY_ROTATION.md`.

### Caching
Skill extraction and classification results are cached to reduce API calls and costs. See `services/cache_service.py`.

### Strategic Analysis
The main analysis engine uses semantic matching (not keyword matching) to compare resumes against job requirements. See `engines/strategic_analysis/`.

### Resume Optimization
Generates optimized resume versions based on analysis results. See `engines/resume_optimizer/`.

## Running the Application

### Start API Server
```bash
python main.py
```

### Start Celery Worker
```bash
celery -A celery_app worker --loglevel=info
```

### Run Analysis
```bash
python run_analysis_strategic.py <resume_id> <job_ids_json> market_intelligence
```

### Run Tests
```bash
cd tests
python test_gemma_analysis.py
```

### Run Utility Scripts
```bash
cd scripts
python check_latest_analysis.py
```

## Environment Variables

Required in `.env`:
- `GEMINI_API_KEY` - Primary Gemini API key
- `GEMINI_API_KEY1-12` - Additional keys for rotation
- `GEMINI_MODEL` - Model to use (e.g., `models/gemma-3-27b-it`)
- `DATABASE_URL` - Database connection string
- `CELERY_BROKER_URL` - Celery broker URL
- `CELERY_RESULT_BACKEND` - Celery result backend

See `.env.example` for full list.
