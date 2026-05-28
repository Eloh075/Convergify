/**
 * Transform API responses to UI types
 */
import type { 
  MarketRoleAnalysisResponse, 
  JobPostingAnalysisResponse,
  MarketSkill,
  GapAnalysis
} from '../types/api';
import type { Analysis, SkillItem } from '../app/components/AppContext';

/**
 * Transform market skill to UI skill item
 */
function transformMarketSkill(
  skill: MarketSkill, 
  status: 'match' | 'gap' | 'partial',
  resumeEvidence?: string
): SkillItem {
  return {
    id: `skill-${skill.canonical_name.toLowerCase().replace(/\s+/g, '-')}`,
    name: skill.canonical_name,
    status,
    category: skill.tier1,
    marketDemand: Math.round(skill.frequency_percentage),
    resumeEvidence,
    recommendation: status === 'gap' 
      ? `Consider adding ${skill.canonical_name} to your resume. This skill appears in ${skill.frequency_percentage.toFixed(1)}% of similar roles.`
      : undefined
  };
}

/**
 * Transform gap analysis to skill items
 */
function transformGapAnalysis(gapAnalysis: GapAnalysis, status: 'match' | 'gap'): SkillItem[] {
  const matched = gapAnalysis.matched.map(skill => 
    transformMarketSkill(skill, status, `Found in resume`)
  );
  
  const gaps = gapAnalysis.gaps.map(skill => 
    transformMarketSkill(skill, 'gap')
  );
  
  return [...matched, ...gaps];
}

/**
 * Transform market role analysis response to UI Analysis
 */
export function transformMarketRoleAnalysis(
  response: MarketRoleAnalysisResponse,
  resumeText: string,
  jobTitle: string,
  company: string
): Analysis {
  // Combine all skills from dealbreakers, differentiators, and bonus
  const dealbreakers = transformGapAnalysis(response.dealbreakers, 'match');
  const differentiators = transformGapAnalysis(response.differentiators, 'match');
  const bonus = transformGapAnalysis(response.bonus, 'match');
  
  const allSkills = [...dealbreakers, ...differentiators, ...bonus];
  
  // Generate strategic summary
  const matchedCount = response.summary.matched_count;
  const totalCount = response.summary.total_skills;
  const matchPercentage = Math.round((matchedCount / totalCount) * 100);
  const hasCriticalGaps = response.dealbreakers.gaps.length > 0;
  const hasDifferentiatorGaps = response.differentiators.gaps.length > 0;
  
  let profileAssessment = '';
  if (response.match_score === 0) {
    profileAssessment = 'Focus on building foundational skills for this role.';
  } else if (response.match_score < 30) {
    profileAssessment = 'Significant skill development needed.';
  } else if (hasCriticalGaps) {
    profileAssessment = 'Address critical gaps to improve competitiveness.';
  } else if (hasDifferentiatorGaps) {
    profileAssessment = 'Strong foundation. Consider adding differentiators.';
  } else {
    profileAssessment = 'Excellent match. Strong competitive profile.';
  }
  
  const strategicSummary = `Based on ${response.market_context.job_count} jobs in the market, you match ${matchedCount} out of ${totalCount} key skills (${matchPercentage}%). ${
    hasCriticalGaps
      ? `Critical gaps: ${response.dealbreakers.gaps.slice(0, 3).map(s => s.canonical_name).join(', ')}. `
      : ''
  }${profileAssessment}`;
  
  return {
    id: response.analysis_id,
    jobTitle,
    company,
    matchScore: response.match_score,
    date: new Date().toISOString().split('T')[0],
    skills: allSkills,
    strategicSummary,
    originalResume: resumeText,
    optimizedResume: resumeText, // TODO: Generate optimized version
    jobDescription: response.market_context.description,
    marketBenchmarking: true,
    strategicOptimization: false
  };
}

/**
 * Transform job posting analysis response to UI Analysis
 */
export function transformJobPostingAnalysis(
  response: JobPostingAnalysisResponse,
  resumeText: string,
  jobTitle: string,
  company: string,
  jobDescription: string
): Analysis {
  // Combine skills from job match and market match
  const jobMatchedSkills: SkillItem[] = response.job_match.matched_skills.map((skillName, idx) => ({
    id: `job-match-${idx}`,
    name: skillName,
    status: 'match' as const,
    category: 'Job Requirement',
    marketDemand: 100,
    resumeEvidence: 'Found in resume'
  }));
  
  const jobMissingSkills: SkillItem[] = response.job_match.missing_skills.map((skillName, idx) => ({
    id: `job-gap-${idx}`,
    name: skillName,
    status: 'gap' as const,
    category: 'Job Requirement',
    marketDemand: 100,
    recommendation: `This skill is required by the job posting. Consider adding it to your resume.`
  }));
  
  // Add market context skills
  const marketDealbreakers = transformGapAnalysis(response.market_match.dealbreakers, 'match');
  const marketDifferentiators = transformGapAnalysis(response.market_match.differentiators, 'match');
  const marketBonus = transformGapAnalysis(response.market_match.bonus, 'match');
  
  const allSkills = [
    ...jobMatchedSkills,
    ...jobMissingSkills,
    ...marketDealbreakers,
    ...marketDifferentiators,
    ...marketBonus
  ];
  
  // Generate strategic summary
  const jobMatchScore = response.job_match.score;
  const marketMatchScore = response.market_match.score;
  
  const strategicSummary = `Job Match: ${jobMatchScore}% (${response.job_match.matched_skills.length}/${response.summary.job_skills_count} skills). Market Match: ${marketMatchScore}%. ${
    response.job_match.missing_skills.length > 0
      ? `Missing from job: ${response.job_match.missing_skills.slice(0, 3).join(', ')}. `
      : 'You meet all job requirements. '
  }${
    response.insights.unique_to_job.length > 0
      ? `Unique to this job: ${response.insights.unique_to_job.slice(0, 2).join(', ')}.`
      : ''
  }`;
  
  return {
    id: response.analysis_id,
    jobTitle,
    company,
    matchScore: Math.round((jobMatchScore + marketMatchScore) / 2),
    date: new Date().toISOString().split('T')[0],
    skills: allSkills,
    strategicSummary,
    originalResume: resumeText,
    optimizedResume: resumeText, // TODO: Generate optimized version
    jobDescription,
    marketBenchmarking: true,
    strategicOptimization: false
  };
}
