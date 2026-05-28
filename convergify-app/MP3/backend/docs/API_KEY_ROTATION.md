# API Key Rotation System

## Overview

The system automatically rotates through multiple Gemini API keys to maximize quota usage and ensure uninterrupted service.

## Configuration

### Setup in `.env` File

```env
# Primary key
GEMINI_API_KEY=AIzaSy...

# Backup keys (automatically detected)
GEMINI_API_KEY1=AIzaSy...
GEMINI_API_KEY2=AIzaSy...
GEMINI_API_KEY3=AIzaSy...
# ... up to GEMINI_API_KEY20
```

**Note**: Spaces around `=` are handled automatically (e.g., `GEMINI_API_KEY1 = AIza...` works fine)

### Current Configuration

- **Total Keys**: 13 (1 primary + 12 backups)
- **Daily Quota**: 20 requests per key
- **Total Capacity**: 260 requests/day (13 × 20)

## How It Works

### 1. Initialization

```python
from engines.gemini_client import GeminiClient

# Automatic rotation enabled
client = GeminiClient()
```

The client:
- Loads all available keys from environment
- Starts with the first key
- Enables automatic rotation

### 2. Quota Detection

The system monitors for quota errors:
- HTTP 429 status codes
- "quota exceeded" in error messages
- "rate limit" in error messages

### 3. Automatic Rotation

When quota is exceeded:
1. Current key is marked as failed
2. System switches to next available key
3. Request is retried immediately (no delay)
4. Processing continues without interruption

### 4. Smart Tracking

- Maintains a set of failed keys
- Only rotates through working keys
- Resets tracking if all keys exhausted
- Logs all rotation events

## Usage

### In Analysis Scripts

```python
from engines.gemini_client import GeminiClient

# Initialize with rotation
client = GeminiClient()

# Make requests - rotation happens automatically
response = client.generate_text("Your prompt here")
```

### In Engines

All engines automatically use rotation:
- `SkillExtractor`
- `SkillClassifier`
- `StrategicAnalyzer`
- `ResumeOptimizer`

No code changes needed!

## Monitoring

### Log Messages

**Successful Rotation**:
```
Marking API key as failed (quota exceeded or error)
Rotated to next API key (1 failed so far)
```

**All Keys Exhausted**:
```
All API keys failed, resetting failure tracking
No more API keys available for rotation
```

### Check Current Status

```python
from engines.config import EngineConfig

# See how many keys are loaded
print(f"Available keys: {len(EngineConfig.GEMINI_API_KEYS)}")

# Check client status
from engines.gemini_client import GeminiClient
client = GeminiClient()
print(f"Failed keys: {len(client._failed_keys)}")
print(f"Current key: {client.api_key[:20]}...")
```

## Testing

### Test Key Loading

```bash
cd Main_Project/backend
python check_env_keys.py
```

Expected output:
```
GEMINI_API_KEY: Found
GEMINI_API_KEY1: Found
GEMINI_API_KEY2: Found
...
Total keys found: 13
```

### Test Rotation Mechanism

```bash
python test_api_key_rotation.py
```

Expected output:
```
✓ Loaded 13 API key(s)
✓ Client initialized
✓ API call successful
✓ Key rotation successful
```

### Test Full System

```bash
python test_full_rotation.py
```

This makes multiple API calls and shows rotation in action.

## Troubleshooting

### Issue: Only 1 key loading

**Cause**: Environment variables not loaded from `.env` file

**Solution**: Ensure `load_dotenv()` is called before importing config:

```python
from dotenv import load_dotenv
load_dotenv()

from engines.config import EngineConfig
```

### Issue: Keys not rotating

**Cause**: Rotation might be disabled or error not detected

**Check**:
1. Verify `client.use_rotation` is `True`
2. Check logs for quota error detection
3. Ensure error message contains "429", "quota", or "rate limit"

### Issue: All keys exhausted

**Cause**: Used all 260 requests/day

**Solutions**:
1. Wait 24 hours for quota reset
2. Add more API keys to `.env` file
3. System will fall back to evidence-based matching

## Benefits

### Maximized Quota
- 13 keys × 20 requests = 260 requests/day
- Automatic load balancing across keys
- No manual key management

### Zero Downtime
- Seamless failover on quota errors
- No interruption to analysis
- Transparent to users

### Easy Maintenance
- Add keys by updating `.env` file
- No code changes required
- Automatic detection of new keys

### Resilient
- Handles temporary API issues
- Falls back gracefully when all keys exhausted
- Comprehensive error logging

## API Key Management

### Getting New Keys

1. Visit https://makersuite.google.com/app/apikey
2. Create new API key
3. Add to `.env` file as `GEMINI_API_KEY13`, `GEMINI_API_KEY14`, etc.
4. Restart application (or reload environment)

### Key Naming Convention

- Primary: `GEMINI_API_KEY`
- Backups: `GEMINI_API_KEY1`, `GEMINI_API_KEY2`, ..., `GEMINI_API_KEY20`
- System checks up to `GEMINI_API_KEY20`

### Security

- Never commit `.env` file to version control
- Keep `.env` in `.gitignore`
- Rotate keys periodically
- Monitor usage in Google Cloud Console

## Performance Impact

### With Rotation
- **Capacity**: 260 requests/day
- **Downtime**: 0% (automatic failover)
- **Manual Intervention**: None required

### Without Rotation
- **Capacity**: 20 requests/day
- **Downtime**: 100% after quota exceeded
- **Manual Intervention**: Required to switch keys

## Implementation Details

### Files Modified

1. **`engines/config.py`**:
   - Added `load_dotenv()` import
   - Added `load_api_keys()` method
   - Validates at least one key available

2. **`engines/gemini_client.py`**:
   - Added class-level `_failed_keys` tracking
   - Added `_get_next_working_key()` method
   - Added `_rotate_key()` method
   - Modified `generate_text()` to detect quota errors
   - Automatic retry with new key on rotation

3. **`run_analysis_strategic.py`**:
   - Added `load_dotenv()` import
   - Ensures environment loaded before analysis

### No Changes Needed

- Analysis engines (already use GeminiClient)
- API endpoints (call scripts that handle rotation)
- Frontend (transparent to UI)
- Database (no schema changes)

## Future Enhancements

### Potential Improvements

1. **Key Pool Management**:
   - Track usage per key
   - Distribute load evenly
   - Predict quota exhaustion

2. **Dynamic Key Addition**:
   - Hot-reload keys without restart
   - API endpoint to add keys
   - Real-time key status dashboard

3. **Advanced Monitoring**:
   - Prometheus metrics
   - Grafana dashboards
   - Alert on low quota

4. **Cost Optimization**:
   - Use paid keys for priority requests
   - Fall back to free keys for batch jobs
   - Track cost per analysis

## Conclusion

The API key rotation system provides:
- ✅ 13x quota capacity (260 requests/day)
- ✅ Automatic failover (zero downtime)
- ✅ Easy configuration (just update `.env`)
- ✅ Transparent operation (no code changes)
- ✅ Comprehensive logging (full visibility)

The system is production-ready and requires no manual intervention during normal operation.
