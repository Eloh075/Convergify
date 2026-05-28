# Job Processing Pipeline

Complete multi-phase pipeline for processing job postings with AI-powered classification and skill extraction.

## Overview

This pipeline transforms raw job postings into structured, analyzable data through multiple processing phases:

```
Raw Job Data → Phase 1 → Phase 2 → Phase 3 → Analyzed Data
```

## Pipeline Phases

### Phase 1: Job Classification & Skill Extraction ✅ COMPLETE

**Status**: 100% complete (1,980/1,980 jobs processed)

**What it does:**
- Classifies jobs by experience level (Internship → Executive)
- Identifies role sub-clusters (Frontend, Backend, Data Science, etc.)
- Extracts technical and soft skills with confidence scores
- Provides evidence snippets for each extracted skill

**Key Stats:**
- 1,980 jobs processed
- 19,204 skills extracted
- 100% success rate
- ~15 seconds per job (parallel processing)

**Technology:**
- Google Gemini/Gemma AI (models/gemma-3-12b-it)
- Parallel processing (7 workers)
- Automatic API key rotation (13 keys)
- Real-time monitoring

[📖 Phase 1 Documentation](./phase_1/README.md)

### Phase 2: Skills Normalization 🔜 UPCOMING

**What it will do:**
- Normalize skill names (e.g., "React.js" → "React")
- Deduplicate similar skills
- Map to standard skill taxonomies
- Cluster related skills
- Categorize skills (Technical, Soft, Domain-specific)

**Planned approach:**
- Fuzzy matching for skill deduplication
- LLM-assisted skill normalization
- Taxonomy mapping (O*NET, ESCO, etc.)

### Phase 3: Advanced Analytics 📋 PLANNED

**What it will do:**
- Skill demand analysis
- Skill co-occurrence patterns
- Career pathway identification
- Skill gap analysis
- Market trend detection

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install google-generativeai supabase python-dotenv

# Set up environment variables
# Create .env file with:
# - GEMINI_API_KEYS (comma-separated)
# - SUPABASE_URL
# - SUPABASE_KEY
```

### Run Phase 1 Processing

```bash
cd Processing_Pipeline/phase_1
python batch_process_all_jobs_parallel.py
```

## Project Structure

```
Processing_Pipeline/
├── README.md                    # This file - Pipeline overview
├── phase_1/                     # Phase 1: Classification & Extraction
│   ├── README.md               # Phase 1 detailed documentation
│   ├── batch_process_all_jobs_parallel.py  # Main parallel processor
│   ├── parallel_processor.py   # Thread pool manager
│   ├── job_processor.py        # Job processing logic
│   ├── gemini_client.py        # Gemini API client
│   ├── config.py               # Configuration
│   ├── models.py               # Data models
│   └── sub_clusters.py         # Role definitions
├── phase_2/                     # Phase 2: Skills Normalization (upcoming)
└── phase_3/                     # Phase 3: Advanced Analytics (planned)
```

## Database Schema

### Core Tables

**job_details** - Raw job data
- url, job_title, description, processed, error_message

**job_classifications** - Phase 1 output
- url, experience_level, role_sub_cluster, cluster_type, confidence

**job_skills** - Phase 1 output
- url, skill_name, confidence, evidence, category_hint

## Technology Stack

- **AI/ML**: Google Gemini/Gemma (models/gemma-3-12b-it)
- **Database**: Supabase (PostgreSQL)
- **Language**: Python 3.x
- **Concurrency**: Threading (7 workers)
- **API Management**: Custom key rotation with circuit breaker

## Performance

### Phase 1 Results

- **Total Processing Time**: ~8 hours for 1,980 jobs
- **Average per Job**: 15 seconds
- **Throughput**: 45+ jobs/minute (parallel)
- **Success Rate**: 100%
- **API Efficiency**: 13 keys with 1-minute cooldown rotation

### Optimization Techniques

1. **Parallel Processing**: 7 concurrent workers
2. **API Key Rotation**: Maximizes throughput, avoids rate limits
3. **Single DB Writer**: Prevents connection pool exhaustion
4. **Smart Retry Logic**: Exponential backoff with key rotation
5. **Input Cleaning**: Prevents JSON parsing errors

## Monitoring

Real-time monitoring includes:
- Progress percentage
- Success/failure counts
- Queue sizes
- API key health
- Throughput (tasks/minute)
- ETA estimation

## Contributing

When adding new phases:
1. Create `phase_N/` folder
2. Add `phase_N/README.md` with detailed documentation
3. Update this main README with phase overview
4. Follow existing patterns (parallel processing, error handling, monitoring)

## Next Steps

1. ✅ Phase 1: Complete
2. 🔜 Phase 2: Skills Normalization - Start development
3. 📋 Phase 3: Advanced Analytics - Planning

## License

[Add license information]

## Contact

[Add contact information]

