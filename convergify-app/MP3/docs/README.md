# MP3 Documentation

## Overview

This folder contains comprehensive documentation for the MP3 Career Analysis System.

## Documentation Files

### CRITICAL_LESSONS_LEARNED.md
**Essential reading for developers.** Documents critical mistakes made during development and how to avoid them:
- Infinite recursion without retry limits
- Model configuration not persisting across API key rotation
- Cached data masking code fixes
- Hardcoded values in output generation
- Fallback logic contradicting requirements
- Subprocess not picking up code changes

### ANALYSIS_PROCESS_EXPLAINED.md
**User-friendly guide** explaining how the analysis system works:
- Step-by-step process from input to output
- Data transformations at each stage
- Real examples from actual analysis
- No technical implementation details
- Focuses on information flow

### ANALYSIS_RESULTS_COMPREHENSIVE.md
**Sample output** from a complete analysis run with canonical grouping:
- 10 AI-related jobs analyzed
- Canonical skill grouping implemented
- AI skills properly aggregated (100% demand instead of 10%)
- 9 canonical groups created
- Complete data tables with child skill breakdowns

## Key Features

### Canonical Skill Grouping
The system now groups semantically related skills under canonical parent names:
- **Example**: "AI", "Generative AI", "Machine Learning" → "Artificial Intelligence (AI)"
- **Result**: Accurate demand scores (100% instead of fragmented 10%)
- **Implementation**: Single LLM call integrated into semantic matching
- **Caching**: Database cache for canonical mappings (38+ seed mappings)
- **Performance**: Cache-first approach reduces LLM calls

### Caching Strategy
1. **Skill Extraction**: Cached per job in `jobs.classified_skills`
2. **Canonical Mappings**: Cached in `skill_canonical_cache` table
3. **Analysis Results**: Saved in `analyses.results` JSON

## System Architecture

For backend architecture details, see `MP3/backend/README.md`

For frontend architecture details, see `MP3/Frontend/README.md`
