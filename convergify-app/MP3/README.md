# Mentor Project - Career Analysis Platform

A full-stack career analysis platform that helps users optimize their resumes based on job market analysis.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 22+
- SQLite

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python init_db.py  # Initialize database
python main.py     # Start server on http://localhost:8000
```

### Frontend Setup
```bash
cd Frontend
npm install
npm run dev  # Start server on http://localhost:5173
```

## 📋 Features

### Core Functionality
- **Resume Upload & Processing** - Upload PDF/TXT resumes
- **Job Scraping** - Scrape jobs from MyCareersFuture
- **Career Analysis** - Match resume against jobs with skill gap analysis
- **Resume Optimization** - Generate improved resume based on analysis
- **Analysis History** - View and reuse past analyses

### Analysis Results Include
- Overall match score percentage
- Skill gaps with importance ratings
- Skill matches with relevance scores
- Market insights and trends
- Actionable recommendations
- Career path suggestions

## 🏗️ Architecture

### Backend (FastAPI)
- **API**: FastAPI REST endpoints
- **Database**: SQLite with SQLAlchemy ORM
- **Analysis**: Subprocess-based skill extraction and matching
- **Scraping**: Selenium-based job scraper

### Frontend (React + TypeScript)
- **UI**: React with Tailwind CSS
- **State**: TanStack Query for API state management
- **Components**: Custom UI components with dark mode support

## 📊 Usage Flow

1. **Upload Resume** → Resume Vault → Upload PDF/TXT
2. **Add Jobs** → Job Hub → Scrape or load jobs
3. **Run Analysis** → Analysis Lab → Select resume + jobs → Generate
4. **View Results** → See comprehensive analysis with all metrics
5. **Optimize Resume** → Click "Optimize Resume" → View comparison

## 🔧 Configuration

### Optional: LLM Integration
Add to `backend/.env`:
```bash
GEMINI_API_KEY=your_api_key_here
```

Without API key, system uses rule-based classification (still works well).

## 📝 Recent Fixes

### Analysis Data Structure (Feb 7, 2026)
- Fixed skill matches to show proper percentages (was showing "NaN%")
- Fixed skill gaps to use numeric importance (0-1) instead of strings
- Added proper market insights with top skills data
- Fixed recommendations tab crash when type field is null

### Subprocess Issues
- Changed from `python3` to `sys.executable` for cross-platform compatibility
- Fixed import paths for scraper and analysis scripts
- Created simplified analysis script without external dependencies

### Database Schema
- Added missing columns (employment_type, skills_processed, etc.)
- Fixed alembic configuration for proper migrations
- Added sample jobs for testing

## 🐛 Troubleshooting

### Analysis shows "NaN%" or missing data
- Click the Refresh button in Analysis Results
- Or close and reopen the analysis from Resume Vault

### Backend errors
- Check both servers are running
- Verify database exists: `backend/career_analysis.db`
- Check backend logs for detailed errors

### Frontend not loading data
- Verify backend is running: http://localhost:8000/health
- Check browser console for errors
- Ensure API returns data: http://localhost:8000/api/jobs/

## 📚 API Documentation

Interactive API docs available at: http://localhost:8000/docs

Key endpoints:
- `POST /api/analyses/` - Create analysis
- `GET /api/analyses/{id}/status` - Check progress
- `GET /api/analyses/{id}/results` - Get results
- `GET /api/jobs/` - List jobs
- `POST /api/resumes/` - Upload resume

## 🎯 Project Status

✅ **Production Ready**
- All core features implemented and working
- Database schema complete
- Frontend UI polished with dark mode
- Analysis engine functional
- Resume optimization working

## 📄 License

This project is for educational purposes.

---

**Ready to analyze careers and optimize resumes!** 🚀
