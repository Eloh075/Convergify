const API_URL = import.meta.env.VITE_API_URL;

export interface MarketSkill {
  canonical_name: string;
  frequency_percentage: number;
  unique_jobs: number;
  total_jobs_in_context: number;
  importance: string;
  tier1: string;
  tier2: string;
}

export interface AnalyzeMarketRoleRequest {
  role: string;
  specialty: string | null;
  experience_levels: string[];
  resume_file: string; // base64 encoded
}

export interface AnalyzeJobPostingRequest {
  job_title: string;
  company: string;
  job_description: string;
  resume_file: string; // base64 encoded
}

export interface AnalysisResponse {
  analysis_id: string;
  match_score: number;
  market_context: {
    job_count: number;
    role: string;
    specialty: string | null;
    experience_levels: string[];
    description: string;
  };
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

/**
 * Analyze resume against market role
 */
export async function analyzeMarketRole(request: AnalyzeMarketRoleRequest): Promise<AnalysisResponse> {
  const response = await fetch(`${API_URL}/analyze-market-role`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error: ${response.status} - ${error}`);
  }

  return response.json();
}

/**
 * Analyze resume against job posting
 */
export async function analyzeJobPosting(request: AnalyzeJobPostingRequest): Promise<AnalysisResponse> {
  const response = await fetch(`${API_URL}/analyze-job-posting`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error: ${response.status} - ${error}`);
  }

  return response.json();
}

/**
 * Get analysis result by ID
 */
export async function getAnalysisResult(analysisId: string): Promise<AnalysisResponse> {
  const response = await fetch(`${API_URL}/analysis-result/${analysisId}`);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error: ${response.status} - ${error}`);
  }

  return response.json();
}

/**
 * Get target options (roles, specialties, experience levels)
 */
export async function getTargetOptions() {
  const response = await fetch(`${API_URL}/target-options`);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error: ${response.status} - ${error}`);
  }

  return response.json();
}

/**
 * Convert file to base64
 */
export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        resolve(reader.result);
      } else {
        reject(new Error('Failed to convert file to base64'));
      }
    };
    reader.onerror = error => reject(error);
  });
}
