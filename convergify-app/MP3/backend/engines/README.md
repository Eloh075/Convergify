# Strategic Career Analysis Engines

This directory contains the core engines for strategic career analysis with semantic matching and evidence extraction.

## Structure

```
engines/
├── skill_extraction/      # Extract skills from job descriptions
├── skill_classification/  # Classify and normalize skills
├── strategic_analysis/    # Semantic matching with evidence
├── resume_optimizer/      # Auto-generate optimized resumes
├── config.py             # Shared configuration
└── gemini_client.py      # Gemini API wrapper
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Gemini API key:**
   - Get your API key from: https://makersuite.google.com/app/apikey
   - Add to `.env` file:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```

3. **Verify setup:**
   ```python
   from engines.config import EngineConfig
   EngineConfig.validate()  # Should not raise an error
   ```

## Usage

Each engine can be imported and used independently:

```python
from engines.skill_extraction import SkillExtractor
from engines.skill_classification import SkillClassifier
from engines.strategic_analysis import StrategicAnalyzer
from engines.resume_optimizer import ResumeOptimizer

# Initialize with API key (or uses .env)
extractor = SkillExtractor()
classifier = SkillClassifier()
analyzer = StrategicAnalyzer()
optimizer = ResumeOptimizer()
```

## Configuration

All engines share configuration from `config.py`:
- `GEMINI_API_KEY`: Your Gemini API key (required)
- `CACHE_VERSION`: Version for cache invalidation
- `MAX_LLM_RETRIES`: Number of retry attempts for failed API calls
- And more...

See `config.py` for full configuration options.

## Testing

Run tests with:
```bash
pytest tests/engines/
```

Property-based tests use Hypothesis for comprehensive testing.
