/**
 * TypeScript types for API requests and responses
 */

// Common types
export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

// Resume types
export interface Resume {
  id: string;
  user_id: string;
  filename: string;
  file_size: number;
  upload_date: string;
  analysis_status: 'pending' | 'processing' | 'completed' | 'failed' | 'skills_extracted';
  extracted_skills?: string[];
  optimized_version_id?: string;
}

export interface OptimizedResume {
  id: string;
  original_resume_id: string;
  optimized_text: string;
  changes: ResumeChange[];
  improvement_score?: number;
  target_job_ids: string[];
  generated_date: string;
  file_path?: string;
}

export interface ResumeChange {
  type: string;
  description: string;
  skills_added?: string[];
  recommendations?: string[];
}

export interface ResumeComparison {
  original: {
    id: string;
    filename: string;
    text: string;
    text_length: number;
    skills: string[];
  };
  optimized: {
    id: string;
    text: string;
    text_length: number;
    improvement_score: number;
    changes: ResumeChange[];
  };
  comparison: {
    text_length_change: number;
    changes_count: number;
    improvement_score: number;
  };
}

export interface ResumeUploadRequest {
  file: File;
  user_id?: string;
}

// Job types
export interface Job {
  id: string;
  title: string;
  company: string;
  description: string;
  requirements?: string[];
  location?: string;
  employment_type?: string;
  salary_min?: number;
  salary_max?: number;
  source: string;
  scraped_date?: string;
  required_skills?: string[];
  skills_processed?: boolean;
  group_id?: string;
  created_date: string;
  salary_range: string;
}

export interface JobGroup {
  id: string;
  name: string;
  description?: string;
  group_type: string;
  job_ids: string[];
  created_date: string;
  analysis_results?: any[];
  job_count: number;
}

export interface JobCreateRequest {
  title: string;
  company: string;
  description: string;
  requirements?: string[];
  location?: string;
  employment_type?: string;
  salary_min?: number;
  salary_max?: number;
  skills?: string[];
}

export interface JobGroupCreateRequest {
  name: string;
  description?: string;
  job_ids?: string[];
}

export interface ScrapingConfig {
  search_terms: string[];
  employment_type?: string;
  max_jobs?: number;
}

export interface ScrapingStatus {
  task_id: string;
  status: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE' | 'REVOKED';
  progress?: number;
  message?: string;
  result?: any;
  error?: string;
}

// Analysis types
export interface Analysis {
  id: string;
  resume_id: string;
  job_ids: string[];
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  start_date: string;
  completion_date?: string;
  results?: AnalysisResults;
  optimized_resume_id?: string;
  duration?: string;
  job_count: number;
}

export interface AnalysisResults {
  skill_gaps: SkillGap[];
  skill_overlaps: SkillOverlap[];
  market_insights: MarketInsights;
  recommendations: Recommendation[];
  career_path_suggestions: CareerPathSuggestion[];
  salary_insights?: SalaryInsights;
  match_score?: number;
}

// New interfaces for redesigned dashboard (analysis-results-dashboard-redesign spec)
export interface AnalysisResultsResponse {
  analysis_id: string;
  resume_id: string;
  resume_filename: string;
  job_count: number;
  job_titles: string[];
  analysis_type: string;
  status: string;
  results: {
    overall_match_score: number;
    skill_matches: SkillMatch[];
    skill_gaps: SkillGap[];
    market_insights: MarketInsights;
    match_breakdown: MatchBreakdown;
    top_strengths: string[];
    top_gaps: string[];
    analyzed_jobs: JobMatchScore[];
  };
  created_at: string;
  completed_at: string;
}

export interface SkillMatch {
  skill: string;
  canonical_group: string;
  match_percentage: number;
  confidence_score: number;
  importance_level: 'Must-have' | 'Nice-to-have' | 'Preferred';
  market_demand: number;
  category: string;
  relevance_score: number;
  resume_mentions: number;
  job_mentions: number;
  match_type: 'Exact' | 'Semantic' | 'Substitution' | 'None';
  evidence: {
    found: boolean;
    text_snippets: string[];
    origin_locations: string[];
    timeline: string;
    confidence: number;
  };
}

export interface SkillGap {
  skill: string;
  importance: number;
  importance_level: 'Must-have' | 'Nice-to-have' | 'Preferred';
  market_demand: number;
  category: string;
  why_matters: string;
  jobs_requiring: string[];
  learning_resources: LearningResource[];
}

export interface MatchBreakdown {
  must_have: { matched: number; total: number };
  nice_to_have: { matched: number; total: number };
  preferred: { matched: number; total: number };
}

export interface JobMatchScore {
  job_id: string;
  title: string;
  company: string;
  location: string;
  match_score: number;
  required_skills: string[];
}

export interface SkillOverlap {
  skill: string;
  resume_mentions: number;
  job_mentions: number;
  relevance_score: number;
}

export interface MarketInsights {
  top_skills: SkillDemand[];
  industry_trends: IndustryTrend[];
  competition_level: string;
  average_salary?: SalaryRange;
}

export interface SkillDemand {
  skill: string;
  demand_score: number;
  growth_trend: 'increasing' | 'stable' | 'decreasing';
  job_count: number;
}

export interface IndustryTrend {
  trend: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
}

export interface Recommendation {
  type: 'immediate' | 'short_term' | 'long_term';
  category: 'skills' | 'experience' | 'education' | 'networking';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  estimated_time?: string;
}

export interface CareerPathSuggestion {
  role: string;
  company_type: string;
  required_skills: string[];
  timeline: string;
  probability: number;
  salary_range?: SalaryRange;
}

export interface SalaryInsights {
  current_market_range: SalaryRange;
  potential_with_skills: SalaryRange;
  location_factor: number;
  experience_factor: number;
}

export interface SalaryRange {
  min: number;
  max: number;
  currency: string;
  period: 'annual' | 'monthly' | 'hourly';
}

export interface LearningResource {
  title: string;
  type: 'course' | 'certification' | 'book' | 'tutorial';
  provider: string;
  url?: string;
  duration?: string;
  cost?: string;
}

export interface AnalysisCreateRequest {
  resume_id: string;
  job_ids?: string[];
  analysis_type?: 'comprehensive' | 'single_job' | 'market_analysis';
}

export interface AnalysisStatus {
  analysis_id: string;
  status: string;
  analysis_type: string;
  task_id?: string;
  created_at?: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  progress_percentage: number;
  has_results: boolean;
  task_status?: {
    task_id: string;
    status: string;
    result?: any;
    traceback?: string;
    date_done?: string;
  };
}

// Task/Background job types
export interface TaskStatus {
  task_id: string;
  status: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE' | 'REVOKED';
  result?: any;
  traceback?: string;
  date_done?: string;
  meta?: {
    current: number;
    total: number;
    status: string;
  };
}

// Error types
export interface ApiError {
  message: string;
  detail?: string;
  status_code?: number;
}

// Filter and search types
export interface ResumeFilters {
  status?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  skip?: number;
  limit?: number;
}

export interface JobFilters {
  company?: string;
  location?: string;
  source?: string;
  group_id?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  skip?: number;
  limit?: number;
}

export interface AnalysisFilters {
  resume_id?: string;
  status?: string;
  analysis_type?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  skip?: number;
  limit?: number;
}

// Session types
export interface AnalysisSession {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  status: 'active' | 'completed' | 'archived';
  session_type: 'comprehensive' | 'single_job' | 'market_analysis';
  resume_ids: string[];
  job_ids: string[];
  analysis_ids: string[];
  configuration?: Record<string, any>;
  tags: string[];
  total_jobs: number;
  total_resumes: number;
  total_analyses: number;
  overall_match_score?: number;
}

export interface SessionSummary {
  id: string;
  title: string;
  status: string;
  session_type: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  duration?: string;
  total_resumes: number;
  total_jobs: number;
  total_analyses: number;
  overall_match_score?: number;
  tags: string[];
}

export interface SessionDetails {
  session: SessionSummary;
  resumes: Array<{
    id: string;
    filename: string;
    upload_date?: string;
    analysis_status: string;
  }>;
  jobs: Array<{
    id: string;
    title: string;
    company: string;
    location?: string;
    created_date?: string;
  }>;
  analyses: Array<{
    id: string;
    status: string;
    start_date?: string;
    completion_date?: string;
    job_count: number;
  }>;
}

export interface SessionStats {
  total_sessions: number;
  active_sessions: number;
  completed_sessions: number;
  archived_sessions: number;
  session_types: Record<string, number>;
}

export interface SessionCreateRequest {
  title: string;
  session_type?: 'comprehensive' | 'single_job' | 'market_analysis';
  description?: string;
  configuration?: Record<string, any>;
  tags?: string[];
}

export interface SessionUpdateRequest {
  title?: string;
  description?: string;
  status?: 'active' | 'completed' | 'archived';
  session_type?: 'comprehensive' | 'single_job' | 'market_analysis';
  configuration?: Record<string, any>;
  tags?: string[];
}

export interface SessionFilters {
  status?: string;
  session_type?: string;
  tags?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  skip?: number;
  limit?: number;
}