# Phase 1: Job Classification & Skill Extraction

## Overview

Phase 1 processes job descriptions using Google's Gemini/Gemma AI models to extract structured information including experience levels, role classifications, and skills with confidence scores.

## What It Does

Extracts from each job posting:
- **Experience Level**: Internship, Entry Level, Associate, Mid-Senior Level, Director, Executive
- **Role Sub-Cluster**: Frontend, Backend, Data Science, DevOps, etc. (35+ sub-clusters)
- **Cluster Type**: Specific (requires specific tech stack) vs Generalist (rotational/broad)
- **Skills**: Technical and soft skills with confidence scores (0.0-1.0) and evidence snippets

## Architecture

### Parallel Processing System

**Components:**
- **7 Worker Threads**: Process jobs concurrently via API calls
- **Single Database Writer**: Handles all database writes to avoid connection limits
- **KeyPoolManager**: Manages 13 API keys with health tracking and circuit breaker
- **Real-time Monitoring**: Progress updates every 5 seconds with throughput and ETA

**Producer-Consumer Pattern:**
```
Task Queue → Worker Threads → Result Queue → Database Writer
                    ↓
              KeyPoolManager (API key rotation)
```

### Key Files

| File | Purpose |
|------|---------|
| `batch_process_all_jobs_parallel.py` | Main entry point for parallel processing |
| `batch_process_all_jobs.py` | Legacy sequential processor |
| `parallel_processor.py` | Thread pool manager with KeyPoolManager |
| `job_processor.py` | Job classification and skill extraction logic |
| `gemini_client.py` | Google Gemini/Gemma API client with retry logic |
| `config.py` | Configuration (API keys, model, thresholds) |
| `models.py` | Data models (JobProcessingResult, JobClassification, ExtractedSkill) |
| `sub_clusters.py` | Role sub-cluster definitions (35+ clusters) |

## Results

**Final Statistics:**
- ✅ Total Jobs Processed: 1,980
- ✅ Success Rate: 100%
- ✅ Total Classifications: 1,980
- ✅ Total Skills Extracted: 19,204
- ⚡ Average Processing Time: ~15 seconds per job
- 🚀 Speedup: 3.5-4x faster than sequential processing

## Usage

### Run Parallel Batch Processing (Recommended)

```bash
cd Processing_Pipeline/phase_1
python batch_process_all_jobs_parallel.py
```

**Features:**
- 7 concurrent workers
- Automatic API key rotation
- Real-time progress monitoring
- Automatic retry on failures

### Run Sequential Processing (Legacy)

```bash
cd Processing_Pipeline/phase_1
python batch_process_all_jobs.py
```

**Note:** Sequential processing is slower but uses less resources.

## Configuration

Edit `config.py` to configure:

```python
# Model Configuration
GEMINI_MODEL = "models/gemma-3-12b-it"  # Cost-efficient, high velocity
GEMINI_API_KEYS = [...]  # 13 API keys for rotation

# Processing Configuration
SKILL_CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence to include skill
MAX_SKILLS_PER_JOB = 50  # Maximum skills per job

# Retry Configuration
MAX_RETRIES = 3
RETRY_INITIAL_DELAY = 2  # seconds
RETRY_BACKOFF_FACTOR = 2  # exponential backoff
```

## Database Schema

### Tables

**job_details**
- `url` (PK): Job posting URL
- `job_title`: Job title
- `description`: Full job description text
- `processed`: Boolean flag
- `processed_at`: Timestamp
- `error_message`: Error message if failed

**job_classifications**
- `url` (PK): Job posting URL
- `job_title`: Job title
- `job_role`: Job role from job_listings table
- `experience_level`: Classified experience level
- `role_sub_cluster`: Sub-cluster (e.g., "Frontend", "Data Science")
- `cluster_type`: "specific" or "generalist"
- `classification_confidence`: Confidence score (0.0-1.0)
- `job_sector`: Job sector

**job_skills**
- `id` (PK): Auto-increment ID
- `url` (FK): Job posting URL
- `skill_name`: Extracted skill name
- `confidence`: Confidence score (0.0-1.0)
- `evidence`: Array of text snippets mentioning the skill
- `category_hint`: Skill category (e.g., "Programming Language", "Framework")
- `job_role`: Job role (denormalized for querying)
- `role_sub_cluster`: Sub-cluster (denormalized)
- `cluster_type`: Cluster type (denormalized)

## Key Features

### Smart Error Handling

1. **Automatic Retry**: Exponential backoff (2s, 4s, 8s)
2. **API Key Rotation**: Switches keys on quota errors (429)
3. **Failed Job Tracking**: Jobs marked as `processed = false` for automatic retry
4. **Input Cleaning**: Removes smart quotes, escape sequences that break JSON parsing

### Monitoring & Observability

Real-time monitoring displays:
- Jobs processed / total (percentage)
- Success vs failed count
- Queue sizes (tasks and results)
- API key health (available/failed)
- Throughput (tasks/minute)
- ETA (estimated time remaining)

Example output:
```
📊 Status:
   Jobs: 1500/1980 (75.8%)
   Success: 1495 | Failed: 5
   Queue: 10 tasks, 2 results
   Keys: 11/13 available, 2 failed
   Throughput: 45.2 tasks/min
   ETA: 10.6 minutes
```

## Troubleshooting

### Common Issues

**1. JSON Parsing Errors**
- **Cause**: Smart quotes or escape sequences in job descriptions
- **Solution**: Automatically cleaned in `job_processor.py` (lines 50-56)

**2. API Quota Errors (429)**
- **Cause**: Rate limit exceeded on API key
- **Solution**: Automatic key rotation (13 keys available)
- **Cooldown**: 1 minute per failed key

**3. Timeout Errors (504)**
- **Cause**: API request timeout
- **Solution**: Automatic retry with exponential backoff

### Check Failed Jobs

```sql
SELECT url, job_title, error_message 
FROM job_details 
WHERE processed = false AND error_message IS NOT NULL;
```

### Retry Failed Jobs

Failed jobs are automatically retried on next run since they're marked as `processed = false`.

## Performance Optimization

### Parallel Processing Benefits

- **7 Workers**: Process 7 jobs simultaneously
- **No Delay**: Workers run concurrently (no 2-second delay between requests)
- **Single DB Writer**: Avoids connection limit issues
- **Key Rotation**: Maximizes API throughput

### Throughput Calculation

```
Throughput = (completed + failed) / elapsed_time * 60  # tasks/minute
ETA = remaining_jobs / (throughput / 60)  # minutes
```

## Next Steps

Phase 1 is complete! Next phase will focus on:
- Skills normalization and deduplication
- Mapping to standard skill taxonomies
- Skill clustering and categorization
