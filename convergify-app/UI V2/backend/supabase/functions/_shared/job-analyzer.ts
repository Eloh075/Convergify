import { createClient } from 'jsr:@supabase/supabase-js@2';
import { extractJSON } from './gemini-client.ts';

export interface JobClassification {
  role: string;
  specialty: string | null;
  experience: string;
  confidence: number;
}

export async function extractJobSkills(
  jobDescription: string,
  supabaseUrl: string,
  supabaseKey: string
): Promise<string[]> {
  const prompt = `Extract all required skills from this job description. Return ONLY a JSON array of skill names, nothing else.

Job Description:
${jobDescription}

Return format: ["Python", "AWS", "Machine Learning", ...]

Focus on:
- Programming languages
- Frameworks and libraries
- Tools and platforms
- Databases
- Cloud services
- Soft skills mentioned
- Domain knowledge required

Return ONLY the JSON array, no explanations.`;

  const extractedSkills = await extractJSON<string[]>(prompt);
  
  // Normalize against canonical skills
  const supabase = createClient(supabaseUrl, supabaseKey);
  const { data: canonicalSkills } = await supabase
    .from('canonical_skills')
    .select('canonical_name');
  
  if (!canonicalSkills) {
    return extractedSkills;
  }
  
  const canonicalMap = new Map<string, string>();
  canonicalSkills.forEach(s => {
    canonicalMap.set(s.canonical_name.toLowerCase(), s.canonical_name);
  });
  
  // Normalize extracted skills
  const normalizedSkills = extractedSkills
    .map(skill => {
      const lowerSkill = skill.toLowerCase().trim();
      
      // Exact match
      if (canonicalMap.has(lowerSkill)) {
        return canonicalMap.get(lowerSkill)!;
      }
      
      // Fuzzy match
      for (const [canonical, originalName] of canonicalMap.entries()) {
        if (canonical.includes(lowerSkill) || lowerSkill.includes(canonical)) {
          return originalName;
        }
      }
      
      return skill;
    })
    .filter((skill, index, self) => self.indexOf(skill) === index);
  
  return normalizedSkills;
}

export async function classifyJob(
  jobTitle: string,
  jobDescription: string,
  supabaseUrl: string,
  supabaseKey: string
): Promise<JobClassification> {
  // Get available roles and specialties from database
  const supabase = createClient(supabaseUrl, supabaseKey);
  const { data: contexts } = await supabase
    .from('skill_market_frequencies')
    .select('job_role, role_sub_cluster, experience_level')
    .eq('cluster_type', 'specific');
  
  if (!contexts || contexts.length === 0) {
    throw new Error('No market data available for classification');
  }
  
  // Extract unique roles, specialties, and experience levels
  const roles = [...new Set(contexts.map(c => c.job_role))];
  const specialtiesByRole = new Map<string, Set<string>>();
  const experienceLevels = [...new Set(contexts.map(c => c.experience_level))];
  
  contexts.forEach(c => {
    if (!specialtiesByRole.has(c.job_role)) {
      specialtiesByRole.set(c.job_role, new Set());
    }
    if (c.role_sub_cluster) {
      specialtiesByRole.get(c.job_role)!.add(c.role_sub_cluster);
    }
  });
  
  const specialtiesMap: Record<string, string[]> = {};
  specialtiesByRole.forEach((subs, role) => {
    specialtiesMap[role] = Array.from(subs);
  });
  
  const prompt = `Classify this job posting into the appropriate role, specialty, and experience level. Return ONLY a JSON object, nothing else.

Job Title: ${jobTitle}

Job Description:
${jobDescription}

Available Roles:
${roles.join(', ')}

Available Specialties by Role:
${JSON.stringify(specialtiesMap, null, 2)}

Available Experience Levels:
${experienceLevels.join(', ')}

Return format:
{
  "role": "exact role name from available roles",
  "specialty": "exact specialty name from available specialties or null if generalist",
  "experience": "exact experience level from available levels",
  "confidence": 0.95
}

Rules:
- role MUST be one of the available roles
- specialty MUST be one of the available specialties for that role, or null
- experience MUST be one of the available experience levels
- confidence should be between 0 and 1

Return ONLY the JSON object, no explanations.`;

  const classification = await extractJSON<JobClassification>(prompt);
  
  // Validate classification
  if (!roles.includes(classification.role)) {
    throw new Error(`Invalid role classification: ${classification.role}`);
  }
  
  if (!experienceLevels.includes(classification.experience)) {
    throw new Error(`Invalid experience level classification: ${classification.experience}`);
  }
  
  if (classification.specialty) {
    const validSpecialties = specialtiesMap[classification.role] || [];
    if (!validSpecialties.includes(classification.specialty)) {
      console.warn(`Invalid specialty classification: ${classification.specialty}, setting to null`);
      classification.specialty = null;
    }
  }
  
  return classification;
}
