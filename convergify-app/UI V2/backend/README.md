# Backend - Supabase Edge Functions

This folder contains the backend API for the Career Strategy Lab application.

## Structure

```
backend/
└── supabase/
    └── functions/
        ├── _shared/              # Shared utilities
        │   ├── types.ts          # TypeScript interfaces
        │   ├── market-skills.ts  # Market data retrieval helper
        │   ├── gap-analysis.ts   # Gap analysis logic
        │   ├── gemini-client.ts  # Gemini API client with key rotation
        │   ├── resume-extractor.ts  # Resume parsing with PDF support
        │   └── job-analyzer.ts   # Job skill extraction and classification
        ├── target-options/       # ✅ GET /target-options
        ├── analyze-market-role/  # ✅ POST /analyze-market-role
        ├── analyze-job-posting/  # ✅ POST /analyze-job-posting
        ├── analysis-status/      # ✅ GET /analysis-status/:id
        └── analysis-result/      # ✅ GET /analysis-result/:id
```

## Current Status

### ✅ Completed
- All 5 API endpoints fully functional
- Gemini API integration with 13-key rotation
- PDF parsing with pako (zlib) decompression for FlateDecode streams
- Resume skill extraction and normalization
- Job skill extraction and classification
- Database storage for analysis results
- Frontend-backend integration complete
- All major bugs fixed (JWT auth, database relationships, PDF parsing, generalist data)

### 🎯 Production Ready
The backend is fully deployed and working in production:
- Edge Functions deployed to Supabase (version 18)
- JWT verification disabled for public access
- All API keys configured and rotating
- Database tables created and indexed

## Quick Start

### Prerequisites
- Node.js and npm installed
- Supabase CLI installed as dev dependency (use `npx supabase`)
- Access to Supabase project: `wpvavxzfbulwrnyrcmnz`

### Deploy All Functions
```bash
cd "UI V2/backend"
chmod +x redeploy.sh
./redeploy.sh
```

Or deploy individually:
```bash
npx supabase functions deploy analyze-market-role --project-ref wpvavxzfbulwrnyrcmnz --no-verify-jwt
npx supabase functions deploy analyze-job-posting --project-ref wpvavxzfbulwrnyrcmnz --no-verify-jwt
npx supabase functions deploy target-options --project-ref wpvavxzfbulwrnyrcmnz
```

## Local Development

1. Start Supabase locally:
```bash
supabase start
```

2. Serve functions:
```bash
supabase functions serve
```

3. Test endpoints:
```bash
# Test target-options
curl http://localhost:54321/functions/v1/target-options

# Test analyze-market-role
curl -X POST http://localhost:54321/functions/v1/analyze-market-role \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Software Engineer",
    "specialty": "Backend",
    "experience_levels": ["Internship", "Entry Level"],
    "resume_file": "base64_encoded_pdf_here"
  }'

# Test analyze-job-posting
curl -X POST http://localhost:54321/functions/v1/analyze-job-posting \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Senior AI Engineer",
    "company": "TechVault AI",
    "job_description": "Build and deploy cutting-edge ML models...",
    "resume_file": "base64_encoded_pdf_here"
  }'

# Test analysis-status
curl http://localhost:54321/functions/v1/analysis-status/test-id-123

# Test analysis-result
curl http://localhost:54321/functions/v1/analysis-result/test-id-123
```

## Environment Variables

### Backend (.env)
All 13 Gemini API keys are configured and rotating automatically:
```env
SUPABASE_URL=https://wpvavxzfbulwrnyrcmnz.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GEMINI_API_KEY=AIzaSyB_Xo3c6TVshURL5F6KljZZeHksH5nIHO4
GEMINI_API_KEY1=AIzaSyDMFhpi4UIQjw-FJhrHYq8OWdg6p9Xpm8o
... (13 keys total)
```

### Frontend (.env)
```env
VITE_API_URL=https://wpvavxzfbulwrnyrcmnz.supabase.co/functions/v1
VITE_ENABLE_DEVTOOLS=true
```

## Key Features

### 1. PDF Parsing ✅
- Proper PDF text extraction using pako (zlib) library
- Handles FlateDecode compression (standard in modern PDFs)
- Decompresses PDF streams and extracts clean text
- Text sanitization to remove control characters
- Fallback to plain text for non-PDF files

### 2. Gemini Integration ✅
- 13 API keys with automatic rotation
- Retry logic with exponential backoff
- Rate limit handling (429 errors)
- Line-by-line format instead of JSON (more reliable)
- Skill normalization against canonical_skills table

### 3. Market Data Aggregation ✅
- Aggregates skill frequencies across experience levels
- Handles "Insufficient Data" by rolling up to parent contexts
- Supports generalist mode (aggregates all specialties)
- Filters out invalid data entries
- Calculates importance based on frequency thresholds

### 4. Gap Analysis ✅
- Match score calculation based on Must-have skills
- Categorizes skills: Dealbreakers / Differentiators / Bonus
- Case-insensitive skill matching
- Detailed breakdown of matched vs gap skills

## Recent Fixes

### PDF Skill Extraction Bug (FIXED) ✅
- **Issue**: PDFs with FlateDecode compression returned garbage text
- **Solution**: Implemented proper PDF parsing with pako decompression
- **Status**: Deployed to production (version 18)
- **Details**: See `PDF_FIX_COMPLETE.md`

### Generalist Data Missing (FIXED) ✅
- **Issue**: Selecting "Generalist" (no specialty) returned "Insufficient market data"
- **Solution**: Aggregate ALL specialties when specialty=null
- **Status**: Deployed and working

### Database Relationship Error (FIXED) ✅
- **Issue**: Query tried to join tables with non-existent foreign key
- **Solution**: Fetch tier1/tier2 separately and merge in aggregation
- **Status**: Deployed and working

### JWT Authentication (FIXED) ✅
- **Issue**: Edge Functions required JWT tokens (401 errors)
- **Solution**: Deployed with `--no-verify-jwt` flag
- **Status**: Public endpoints working correctly

## API Documentation

See `API_DOCUMENTATION.md` for complete API reference including:
- All endpoints with request/response formats
- Database schema
- Frontend integration guide
- Development workflow

See `GEMINI_MODELS.md` for Gemini API reference:
- Available models and their capabilities
- API endpoint structure
- Model selection guidelines

## Testing

### Test All Endpoints
```bash
./test-endpoints.sh
```

### Test Individual Endpoints
```bash
# Test target-options
curl https://wpvavxzfbulwrnyrcmnz.supabase.co/functions/v1/target-options

# Test analyze-market-role
curl -X POST https://wpvavxzfbulwrnyrcmnz.supabase.co/functions/v1/analyze-market-role \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Software Engineer",
    "specialty": "Backend",
    "experience_levels": ["Entry Level"],
    "resume_file": "base64_encoded_resume"
  }'
```

## Known Limitations

1. **Match Score May Be 0%**: Expected if no market data exists for the selected role/specialty/experience combination
2. **PDF Parsing**: Works best with text-based PDFs; may have issues with scanned documents or complex layouts
3. **Specialty Data**: Some roles only have specialty-specific data, not generalist data
4. **Text Extraction Quality**: Depends on PDF structure and formatting

## Database Schema

### Tables
- `canonical_skills` - Master list of normalized skill names
- `skill_market_frequencies` - Skill frequency data for each market context
- `job_skills` - Skill taxonomy (tier1, tier2 categories)
- `analysis_jobs` - Analysis job status tracking
- `analysis_results` - Completed analysis results

## Development Notes

- Always check `GEMINI_MODELS.md` before editing Gemini-related code
- Use `gemini-2.5-flash` (latest model), NOT `gemini-1.5-flash` (deprecated)
- Use `v1` API endpoint, NOT `v1beta`
- Use `npx supabase` to run CLI commands (installed as dev dependency)
- Test the whole process before reporting back

## Support

For issues:
1. Check browser console for errors
2. Check Supabase Edge Function logs
3. Verify environment variables are set correctly
4. Test API endpoints directly with curl

## Project Structure

```
UI V2/
├── backend/
│   ├── supabase/functions/     # Edge Functions
│   ├── .env                    # Environment variables (13 Gemini keys)
│   ├── API_DOCUMENTATION.md    # Complete API reference
│   ├── GEMINI_MODELS.md        # Gemini API reference
│   ├── PDF_FIX_COMPLETE.md     # PDF parsing fix documentation
│   ├── README.md               # This file
│   ├── redeploy.sh             # Deployment script
│   └── test-endpoints.sh       # Testing script
└── frontend/
    └── src/                    # React frontend
```

---

**Last Updated**: 2026-03-06  
**Version**: 2.0.0  
**Status**: Production Ready ✅
