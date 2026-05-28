import { createClient } from 'jsr:@supabase/supabase-js@2';
import type { MarketSkill, AnalysisContext } from './types.ts';

export async function getMarketSkills(
  supabaseUrl: string,
  supabaseKey: string,
  role: string,
  specialty: string | null,
  experienceLevels: string[]
): Promise<{ skills: MarketSkill[]; job_count: number; contexts: AnalysisContext[] }> {
  const supabase = createClient(supabaseUrl, supabaseKey);

  // Query for each experience level
  const queries = experienceLevels.map(level => {
    let query = supabase
      .from('skill_market_frequencies')
      .select(`
        canonical_skill_id,
        normalized_frequency,
        importance,
        unique_jobs,
        total_jobs_in_context,
        canonical_skills!inner(canonical_name)
      `)
      .eq('job_role', role)
      .eq('experience_level', level)
      .eq('cluster_type', 'specific');

    if (specialty) {
      // If specialty is specified, filter by it
      query = query.eq('role_sub_cluster', specialty);
    }
    // If specialty is null, get ALL specialties (don't filter by role_sub_cluster)

    return query;
  });

  const results = await Promise.all(queries);

  // Check for errors
  const errors = results.filter(r => r.error);
  if (errors.length > 0) {
    throw new Error(`Failed to fetch market skills: ${errors[0].error?.message}`);
  }

  // Flatten all results and filter out "Insufficient Data" entries
  const allSkills = results.flatMap(r => r.data || []);
  const validSkills = allSkills.filter((s: any) => s.importance !== 'Insufficient Data');
  
  if (validSkills.length === 0) {
    // If we already tried without specialty filter, return empty
    if (!specialty) {
      return {
        skills: [],
        job_count: 0,
        contexts: []
      };
    }
    // Otherwise, try rolling up to all specialties
    return rollUpToParent(supabaseUrl, supabaseKey, role, specialty, experienceLevels);
  }

  // Group valid skills back by level for aggregation
  const skillsByLevel = [validSkills];

  // Aggregate frequencies across levels
  const aggregated = await aggregateSkillFrequencies(skillsByLevel, supabase);

  const totalJobs = validSkills.reduce((sum, skill: any) => {
    return Math.max(sum, skill.total_jobs_in_context || 0);
  }, 0);

  return {
    skills: aggregated,
    job_count: totalJobs,
    contexts: experienceLevels.map(level => ({ role, specialty, experience_level: level }))
  };
}

async function aggregateSkillFrequencies(skillsByLevel: any[][], supabase: any): Promise<MarketSkill[]> {
  const skillMap = new Map<string, any>();
  const canonicalSkillIds = new Set<number>();

  skillsByLevel.forEach(skills => {
    skills.forEach((skill: any) => {
      const canonicalName = skill.canonical_skills?.canonical_name;
      const canonicalSkillId = skill.canonical_skill_id;
      if (!canonicalName || !canonicalSkillId) return;

      canonicalSkillIds.add(canonicalSkillId);

      if (!skillMap.has(canonicalName)) {
        skillMap.set(canonicalName, {
          canonical_name: canonicalName,
          canonical_skill_id: canonicalSkillId,
          frequency_sum: 0,
          unique_jobs_sum: 0,
          total_jobs_sum: 0,
          level_count: 0
        });
      }

      const existing = skillMap.get(canonicalName);
      existing.frequency_sum += skill.normalized_frequency || 0;
      existing.unique_jobs_sum += skill.unique_jobs || 0;
      existing.total_jobs_sum += skill.total_jobs_in_context || 0;
      existing.level_count += 1;
    });
  });

  // Fetch tier1/tier2 for all canonical skills
  const { data: tierData } = await supabase
    .from('job_skills')
    .select('canonical_skill_id, tier1, tier2')
    .in('canonical_skill_id', Array.from(canonicalSkillIds));

  const tierMap = new Map<number, { tier1: string; tier2: string }>();
  if (tierData) {
    tierData.forEach((t: any) => {
      if (!tierMap.has(t.canonical_skill_id)) {
        tierMap.set(t.canonical_skill_id, { tier1: t.tier1, tier2: t.tier2 });
      }
    });
  }

  // Calculate averages and determine importance
  return Array.from(skillMap.values()).map(skill => {
    const avgFrequency = skill.frequency_sum / skill.level_count;
    const tiers = tierMap.get(skill.canonical_skill_id) || { tier1: 'Unknown', tier2: 'Unknown' };
    
    return {
      canonical_name: skill.canonical_name,
      tier1: tiers.tier1,
      tier2: tiers.tier2,
      frequency_percentage: avgFrequency,
      importance: 
        avgFrequency > 60 ? 'Must-have' :
        avgFrequency >= 30 ? 'Nice-to-have' : 'Preferred',
      unique_jobs: Math.round(skill.unique_jobs_sum / skill.level_count),
      total_jobs_in_context: Math.round(skill.total_jobs_sum / skill.level_count)
    } as MarketSkill;
  }).sort((a, b) => b.frequency_percentage - a.frequency_percentage);
}

async function rollUpToParent(
  supabaseUrl: string,
  supabaseKey: string,
  role: string,
  specialty: string | null,
  experienceLevels: string[]
): Promise<{ skills: MarketSkill[]; job_count: number; contexts: AnalysisContext[] }> {
  const supabase = createClient(supabaseUrl, supabaseKey);

  // Try removing specialty filter first
  if (specialty) {
    const { data, error } = await supabase
      .from('skill_market_frequencies')
      .select(`
        canonical_skill_id,
        normalized_frequency,
        importance,
        unique_jobs,
        total_jobs_in_context,
        canonical_skills!inner(canonical_name)
      `)
      .eq('job_role', role)
      .is('role_sub_cluster', null)
      .in('experience_level', experienceLevels)
      .eq('cluster_type', 'specific');

    if (!error && data && data.length > 0) {
      const aggregated = await aggregateSkillFrequencies([data], supabase);
      return {
        skills: aggregated,
        job_count: data[0]?.total_jobs_in_context || 0,
        contexts: experienceLevels.map(level => ({ role, specialty: null, experience_level: level }))
      };
    }
  }

  // If still insufficient, return empty with warning
  return {
    skills: [],
    job_count: 0,
    contexts: []
  };
}
