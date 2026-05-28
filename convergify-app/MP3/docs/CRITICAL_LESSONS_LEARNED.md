# Critical Lessons Learned - MP3 Analysis System

## Purpose
This document captures critical mistakes and lessons learned during MP3 development. These are patterns to AVOID in future development.

---

## 🔴 Critical Mistakes Made

### 1. Infinite Recursion Without Retry Limits
**What Happened:**
- `generate_json` method recursed infinitely when all API keys failed
- Caused 30+ minute hangs with no error message
- System appeared frozen with no way to debug

**Root Cause:**
```python
# BAD - No retry limit
def generate_json(self, prompt, ...):
    try:
        # ... API call
    except QuotaError:
        if self._rotate_key():
            return self.generate_json(prompt, ...)  # ❌ Infinite recursion
```

**Lesson:**
- **ALWAYS add retry limits to recursive functions**
- **ALWAYS fail loudly after max retries**
- **NEVER assume external resources (API keys) are infinite**

**Fix Pattern:**
```python
# GOOD - With retry limit
def generate_json(self, prompt, ..., retry_count: int = 0):
    MAX_RETRIES = len(self.available_keys) if self.use_rotation else 3
    if retry_count >= MAX_RETRIES:
        raise Exception(f"Max retries ({MAX_RETRIES}) exceeded")
    
    try:
        # ... API call
    except QuotaError:
        if self._rotate_key():
            return self.generate_json(prompt, ..., retry_count + 1)  # ✅ Tracked
```

---

### 2. Model Configuration Not Persisting Across Key Rotation
**What Happened:**
- Switched to Gemini 2.5 Flash for large outputs
- When API key rotated, fell back to default model (Gemma 3)
- Caused JSON truncation errors to reappear

**Root Cause:**
```python
# BAD - Model not reconfigured after key rotation
temp_model = genai.GenerativeModel('models/gemini-2.5-flash')
self.llm_client.model = temp_model

# Later, when key rotates...
self._rotate_key()  # ❌ Reconfigures with default model
```

**Lesson:**
- **Model configuration is tied to API key**
- **Must reconfigure model after every key rotation**
- **Don't assume model persists across configuration changes**

**Fix Pattern:**
```python
# GOOD - Reconfigure model with new key
def _call_large_model_with_rotation(self, prompt, retry_count=0):
    # Configure with current key
    genai.configure(api_key=self.llm_client.api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    try:
        response = model.generate_content(prompt)
    except QuotaError:
        if self.llm_client._rotate_key():
            return self._call_large_model_with_rotation(prompt, retry_count + 1)
```

---

### 3. Cached Data Masking Code Fixes
**What Happened:**
- Fixed frequency calculation bug in classifier
- Tests showed fix working correctly
- Frontend still showed old uniform values (10%, 40%)
- Spent hours debugging "broken" code that was actually fixed

**Root Cause:**
- Analysis results stored in database
- Old cached results not cleared after code fix
- System served stale data from cache

**Lesson:**
- **Cache invalidation is critical after code changes**
- **Always clear cache when fixing calculation logic**
- **Test with fresh data, not cached results**
- **Add cache version tracking to detect stale data**

**Prevention Pattern:**
```python
# Add version tracking to cached data
class Job(Base):
    classified_skills = Column(Text)
    classification_version = Column(String)  # ✅ Track version
    
# Clear cache when version changes
CLASSIFICATION_VERSION = "2.0"  # Increment after fixes

if job.classification_version != CLASSIFICATION_VERSION:
    job.classified_skills = None  # Force re-extraction
```

---

### 4. Hardcoded Values in Output Generation
**What Happened:**
- Classifier correctly calculated frequencies
- Output generation hardcoded `job_count = 1` and `growth_trend = 'stable'`
- Made it look like classifier was broken when it wasn't

**Root Cause:**
```python
# BAD - Hardcoded values
top_skills_data.append({
    'skill': skill_match.skill_name,
    'job_count': 1,  # ❌ Always 1
    'growth_trend': 'stable'  # ❌ Placeholder
})
```

**Lesson:**
- **Never hardcode values that should be calculated**
- **Use None/null for unavailable data, not placeholders**
- **Trace data flow from calculation to output**

**Fix Pattern:**
```python
# GOOD - Use actual calculated values
job_count = 1
if classification_result.market_frequencies:
    freq_data = classification_result.market_frequencies.get(skill_name)
    if freq_data:
        job_count = freq_data.raw_frequency  # ✅ Actual value

top_skills_data.append({
    'skill': skill_match.skill_name,
    'job_count': job_count,  # ✅ Calculated
    'growth_trend': None  # ✅ Honest about missing data
})
```

---

### 5. Fallback Logic Contradicting Requirements
**What Happened:**
- User explicitly requested "fail loudly, no fallbacks"
- Code had fallback logic that silently returned placeholder data
- Made debugging impossible (no errors, just wrong data)

**Root Cause:**
```python
# BAD - Silent fallback
try:
    result = llm_classify(skills)
except Exception as e:
    logger.error(f"LLM failed: {e}")
    return self._fallback_classification(skills)  # ❌ Silent failure
```

**Lesson:**
- **Respect user requirements about error handling**
- **Fail loudly when critical operations fail**
- **Don't hide errors with fallback data**
- **Placeholder data is worse than no data**

**Fix Pattern:**
```python
# GOOD - Fail loudly
try:
    result = llm_classify(skills)
except Exception as e:
    logger.error(f"LLM classification failed: {e}")
    raise Exception(
        f"Skill classification failed: {e}. "
        f"Check API keys and model availability."
    )  # ✅ Clear error
```

---

### 6. Subprocess Not Picking Up Code Changes
**What Happened:**
- Fixed code in analyzer.py
- Restarted backend server
- Frontend still got old errors
- Subprocess was using cached Python bytecode

**Root Cause:**
- Python caches compiled bytecode in `__pycache__`
- Subprocess loads cached bytecode, not source
- Server restart doesn't clear subprocess cache

**Lesson:**
- **Clear Python bytecode cache after code changes**
- **Subprocess caching is separate from main process**
- **Use `python -B` to disable bytecode caching in dev**

**Prevention Pattern:**
```bash
# Clear all Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Or run without bytecode caching
python -B main.py
```

---

## ✅ Good Patterns to Follow

### 1. Cache-First with Fallback
```python
# Check cache first, use LLM as fallback
cached = db.query(Cache).filter(Cache.key == key).first()
if cached:
    return cached.value  # ✅ Fast path

# Cache miss - use LLM
result = llm_call(data)
db.add(Cache(key=key, value=result))  # ✅ Cache for next time
return result
```

### 2. Retry with Exponential Backoff
```python
def call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise  # ✅ Fail after max retries
            delay = 2 ** attempt  # Exponential backoff
            time.sleep(delay)
```

### 3. Explicit None for Missing Data
```python
# GOOD - Honest about missing data
{
    'growth_trend': None,  # ✅ Not available
    'salary_range': None,  # ✅ Not provided
}

# BAD - Misleading placeholders
{
    'growth_trend': 'stable',  # ❌ Fake data
    'salary_range': {'min': 0, 'max': 0},  # ❌ Meaningless
}
```

### 4. Version Tracking for Cache
```python
CACHE_VERSION = "2.0"

class CachedData(Base):
    data = Column(Text)
    version = Column(String)  # ✅ Track version
    
# Invalidate on version mismatch
if cached.version != CACHE_VERSION:
    cached = None  # Force refresh
```

---

## 🎯 Development Checklist

Before deploying fixes:
- [ ] Added retry limits to all recursive functions
- [ ] Cleared Python bytecode cache (`__pycache__`)
- [ ] Cleared database cache for affected data
- [ ] Tested with fresh data, not cached results
- [ ] Verified no hardcoded values in output
- [ ] Confirmed error handling matches requirements
- [ ] Checked subprocess picks up code changes
- [ ] Added version tracking to cached data

---

## 📊 Impact Summary

| Mistake | Time Lost | Prevention |
|---------|-----------|------------|
| Infinite recursion | 2 hours | Add retry limits |
| Model not persisting | 3 hours | Reconfigure after rotation |
| Cached data masking fix | 4 hours | Clear cache after fixes |
| Hardcoded values | 2 hours | Trace data flow |
| Silent fallbacks | 3 hours | Fail loudly |
| Subprocess cache | 2 hours | Clear bytecode cache |
| **Total** | **16 hours** | **Follow checklist** |

---

## 🚀 Quick Reference

### Clear All Caches
```bash
# Python bytecode
find . -type d -name "__pycache__" -exec rm -rf {} +

# Database cache
python clear_analysis_cache.py

# Restart services
# Backend will auto-reload with uvicorn --reload
```

### Test After Fixes
```bash
# Run quick validation
python tests/test_9_jobs.py

# Check API quota
python tests/test_quota_all_keys.py

# Full analysis test
python tests/test_analysis_timing.py
```

### Debug Checklist
1. Check logs for actual errors (not cached)
2. Verify code changes loaded (print statement)
3. Clear all caches (Python + DB)
4. Test with fresh data
5. Trace data flow from source to output

---

**Remember: Most "bugs" after fixes are actually cache issues!**
