// API response types

export interface TargetOptionsResponse {
  roles: string[];
  specialties: Record<string, string[]>;
  experience_levels: string[];
}

export interface MarketSkill {
  canonical_name: string;
  tier1: string;
  tier2: string;
  frequency_percentage: number;
  importance: 'Must-have' | 'Nice-to-have' | 'Preferred' | 'Insufficient Data';
  unique_jobs: number;
  total_jobs_in_context: number;
}

export interface GapAnalysis {
  matched: MarketSkill[];
  gaps: MarketSkill[];
}

export interface AnalysisSummary {
  total_skills: number;
  must_have_count: number;
  nice_to_have_count: number;
  preferred_count: number;
  matched_count: number;
}

export interface MarketContext {
  job_count: number;
  role: string;
  specialty: string | null;
  experience_levels: string[];
  description: string;
}

export interface MarketRoleAnalysisResponse {
  analysis_id: string;
  match_score: number;
  market_context: MarketContext;
  dealbreakers: GapAnalysis;
  differentiators: GapAnalysis;
  bonus: GapAnalysis;
  summary: AnalysisSummary;
}

export interface JobClassification {
  role: string;
  specialty: string | null;
  experience: string;
  confidence: number;
}

export interface JobMatch {
  score: number;
  matched_skills: string[];
  missing_skills: string[];
}

export interface MarketMatch {
  score: number;
  dealbreakers: GapAnalysis;
  differentiators: GapAnalysis;
  bonus: GapAnalysis;
}

export interface JobPostingAnalysisResponse {
  analysis_id: string;
  job_classification: JobClassification;
  job_match: JobMatch;
  market_match: MarketMatch;
  insights: {
    unique_to_job: string[];
    unique_to_market: string[];
  };
  market_context: {
    job_count: number;
    role: string;
    specialty: string | null;
    experience: string;
    description: string;
  };
  summary: AnalysisSummary & {
    job_skills_count: number;
    market_skills_count: number;
    resume_skills_count: number;
  };
}

export interface AnalysisStatusResponse {
  status: 'processing' | 'completed' | 'failed';
  progress?: {
    step: string;
    percentage: number;
  };
  error_message?: string;
}

// Request types
export interface AnalyzeMarketRoleRequest {
  role: string;
  specialty: string | null;
  experience_levels: string[];
  resume_file: string; // base64
}

export interface AnalyzeJobPostingRequest {
  job_title: string;
  company?: string;
  job_description: string;
  resume_file: string; // base64
}
