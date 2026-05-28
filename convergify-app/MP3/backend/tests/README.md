# Test Scripts

This directory contains essential test scripts for the MP3 backend.

## Essential Tests

### 1. `test_analysis_timing.py`
**Purpose:** Comprehensive end-to-end analysis test with 10 jobs
- Tests full analysis pipeline
- Measures performance and timing
- Shows detailed progress
- **Usage:** `python test_analysis_timing.py`

### 2. `test_9_jobs.py`
**Purpose:** Quick analysis test with 9 jobs
- Faster than 10-job test
- Good for quick validation
- **Usage:** `python test_9_jobs.py`

### 3. `test_generate_json.py`
**Purpose:** Test LLM JSON generation
- Validates `generate_json` method
- Tests with and without schema
- **Usage:** `python test_generate_json.py`

## Utility Tests

### 4. `list_all_models.py`
**Purpose:** List all available Gemini models
- Shows model capabilities
- Displays input/output token limits
- **Usage:** `python list_all_models.py`

### 5. `test_quota_all_keys.py` ⭐ IMPORTANT
**Purpose:** Check API key quota status
- Tests all 13 API keys
- Shows which keys have quota remaining
- Tests Gemini 2.5 models
- **Usage:** `python test_quota_all_keys.py`
- **When to use:** Before running analysis, or when getting quota errors

## Legacy Tests (Keep for Reference)

### 6. `test_all_components.py`
Legacy component test

### 7. `test_classifier_output.py`
Legacy classifier test

### 8. `test_frequency_fix.py`
Legacy frequency test

### 9. `test_real_analysis.py`
Legacy analysis test

## Quick Reference

### Check if system is working:
```bash
python test_9_jobs.py
```

### Check API quota:
```bash
python test_quota_all_keys.py
```

### Full performance test:
```bash
python test_analysis_timing.py
```

### Test LLM functionality:
```bash
python test_generate_json.py
```

## Expected Performance

- **2 jobs:** ~75 seconds (37s per job)
- **9 jobs:** ~3-4 minutes (20-25s per job)
- **10 jobs:** ~4-5 minutes (25-30s per job)

With caching, subsequent runs are faster.

## Troubleshooting

### "Quota exceeded" errors
Run `python test_quota_all_keys.py` to check which keys still have quota.

### "Response too large" errors
The system should automatically handle this with Gemini 2.5 Flash or batching.

### Analysis fails
1. Check backend is running
2. Check database has resume and jobs
3. Check API keys are valid
4. Run `python test_generate_json.py` to test LLM

## Notes

- All tests use the same database as the main application
- Tests create analysis records in the database
- Use `python clear_analysis_cache.py` to clear test data
