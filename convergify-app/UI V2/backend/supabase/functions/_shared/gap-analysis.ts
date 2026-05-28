import type { MarketSkill, GapAnalysisResult } from './types.ts';

export function calculateGapAnalysis(
  resumeSkills: string[],
  marketSkills: MarketSkill[]
): GapAnalysisResult {
  // Normalize to lowercase for matching
  const resumeSet = new Set(resumeSkills.map(s => s.toLowerCase().trim()));

  // Categorize market skills by importance
  const mustHave = marketSkills.filter(s => s.importance === 'Must-have');
  const niceToHave = marketSkills.filter(s => s.importance === 'Nice-to-have');
  const preferred = marketSkills.filter(s => s.importance === 'Preferred');

  // Calculate matches and gaps for each category
  const mustHaveMatches = mustHave.filter(s => 
    resumeSet.has(s.canonical_name.toLowerCase().trim())
  );
  const mustHaveGaps = mustHave.filter(s => 
    !resumeSet.has(s.canonical_name.toLowerCase().trim())
  );

  const niceToHaveMatches = niceToHave.filter(s => 
    resumeSet.has(s.canonical_name.toLowerCase().trim())
  );
  const niceToHaveGaps = niceToHave.filter(s => 
    !resumeSet.has(s.canonical_name.toLowerCase().trim())
  );

  const preferredMatches = preferred.filter(s => 
    resumeSet.has(s.canonical_name.toLowerCase().trim())
  );
  const preferredGaps = preferred.filter(s => 
    !resumeSet.has(s.canonical_name.toLowerCase().trim())
  );

  // Calculate base match score (based on Must-have skills only)
  const baseMatchScore = mustHave.length > 0
    ? (mustHaveMatches.length / mustHave.length) * 100
    : 0;

  // Apply Differentiator Multiplier: +2% for each Nice-to-have skill possessed
  const differentiatorBonus = niceToHaveMatches.length * 2;
  
  // Final score capped at 95% (no resume is perfect)
  const finalMatchScore = Math.min(95, Math.round(baseMatchScore + differentiatorBonus));

  return {
    match_score: finalMatchScore,
    dealbreakers: {
      matched: mustHaveMatches,
      gaps: mustHaveGaps
    },
    differentiators: {
      matched: niceToHaveMatches,
      gaps: niceToHaveGaps
    },
    bonus: {
      matched: preferredMatches,
      gaps: preferredGaps
    },
    summary: {
      total_skills: marketSkills.length,
      must_have_count: mustHave.length,
      nice_to_have_count: niceToHave.length,
      preferred_count: preferred.length,
      matched_count: mustHaveMatches.length + niceToHaveMatches.length + preferredMatches.length
    }
  };
}
