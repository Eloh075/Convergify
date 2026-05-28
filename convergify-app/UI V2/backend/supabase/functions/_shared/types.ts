// Shared types for all Edge Functions

export interface MarketSkill {
  canonical_name: string;
  tier1: string;
  tier2: string;
  frequency_percentage: number;
  importance: 'Must-have' | 'Nice-to-have' | 'Preferred' | 'Insufficient Data';
  unique_jobs: number;
  total_jobs_in_context: number;
}

export interface AnalysisContext {
  role: string;
  specialty: string | null;
  experience_level: string;
}

export interface GapAnalysisResult {
  match_score: number;
  dealbreakers: {
    matched: MarketSkill[];
    gaps: MarketSkill[];
  };
  differentiators: {
    matched: MarketSkill[];
    gaps: MarketSkill[];
  };
  bonus: {
    matched: MarketSkill[];
    gaps: MarketSkill[];
  };
  summary: {
    total_skills: number;
    must_have_count: number;
    nice_to_have_count: number;
    preferred_count: number;
    matched_count: number;
  };
}

export interface AnalysisJob {
  id: string;
  status: 'processing' | 'completed' | 'failed';
  progress_step: string;
  progress_percentage: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface AnalysisResult extends GapAnalysisResult {
  analysis_id: string;
  market_context: {
    job_count: number;
    role: string;
    specialty: string | null;
    experience_levels: string[];
    description: string;
  };
}
