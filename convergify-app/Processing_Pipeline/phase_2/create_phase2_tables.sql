-- Phase 2 Database Setup
-- Uses existing job_skills columns: canonical_name, tier1, tier2, skill_type, experience_context
-- Only creates canonical_skills table for reference and skill_market_frequencies for aggregated data

-- Canonical skills table already exists, just add index
CREATE INDEX IF NOT EXISTS idx_canonical_skills_name ON canonical_skills(canonical_name);

-- skill_market_frequencies table already exists, just add indexes
CREATE INDEX IF NOT EXISTS idx_skill_market_freq_role ON skill_market_frequencies(job_role);
CREATE INDEX IF NOT EXISTS idx_skill_market_freq_canonical ON skill_market_frequencies(canonical_skill_id);

-- Add indexes to job_skills for faster queries
CREATE INDEX IF NOT EXISTS idx_job_skills_canonical_name ON job_skills(canonical_name);
CREATE INDEX IF NOT EXISTS idx_job_skills_canonical_id ON job_skills(canonical_skill_id);
CREATE INDEX IF NOT EXISTS idx_job_skills_job_role ON job_skills(job_role);
CREATE INDEX IF NOT EXISTS idx_job_skills_tier1 ON job_skills(tier1);
CREATE INDEX IF NOT EXISTS idx_job_skills_tier2 ON job_skills(tier2);
