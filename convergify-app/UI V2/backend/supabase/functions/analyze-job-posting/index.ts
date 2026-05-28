import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from 'jsr:@supabase/supabase-js@2';
import { getMarketSkills } from '../_shared/market-skills.ts';
import { calculateGapAnalysis } from '../_shared/gap-analysis.ts';
import { extractResumeSkills } from '../_shared/resume-extractor.ts';
import { extractJobSkills, classifyJob } from '../_shared/job-analyzer.ts';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL') ?? '';
    const supabaseKey = Deno.env.get('SUPABASE_ANON_KEY') ?? '';
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { job_title, company, job_description, resume_file } = await req.json();

    // Validate input
    if (!job_title || !job_description) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields: job_title, job_description' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    if (!resume_file) {
      return new Response(
        JSON.stringify({ error: 'Missing resume_file' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Generate analysis ID
    const analysisId = crypto.randomUUID();

    // Step 1: Extract skills from job description using Gemini
    const jobSkills = await extractJobSkills(job_description, supabaseUrl, supabaseKey);

    // Step 2: Classify job into role/specialty/experience using Gemini
    const classification = await classifyJob(job_title, job_description, supabaseUrl, supabaseKey);

    // Step 3: Extract skills from resume using Gemini
    const resumeSkills = await extractResumeSkills(resume_file, supabaseUrl, supabaseKey);

    // Step 4: Get market skills for classified context
    const marketData = await getMarketSkills(
      supabaseUrl,
      supabaseKey,
      classification.role,
      classification.specialty,
      [classification.experience]
    );

    if (marketData.skills.length === 0) {
      return new Response(
        JSON.stringify({ 
          error: 'Insufficient market data for classified job context',
          classification,
          suggestion: 'The job classification may be too specific. Try a more general role.'
        }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Step 5: Calculate dual analysis (job match + market match)
    const jobMatch = calculateJobMatch(resumeSkills, jobSkills);
    const marketMatch = calculateGapAnalysis(resumeSkills, marketData.skills);

    // Identify unique skills
    const uniqueToJob = jobSkills.filter(
      skill => !marketData.skills.find(m => m.canonical_name.toLowerCase() === skill.toLowerCase())
    );
    const uniqueToMarket = marketData.skills
      .filter(m => !jobSkills.find(j => j.toLowerCase() === m.canonical_name.toLowerCase()))
      .slice(0, 10); // Limit to top 10

    // Build response
    const result = {
      analysis_id: analysisId,
      job_classification: classification,
      job_match: {
        score: jobMatch.score,
        matched_skills: jobMatch.matched,
        missing_skills: jobMatch.gaps
      },
      market_match: {
        score: marketMatch.match_score,
        dealbreakers: marketMatch.dealbreakers,
        differentiators: marketMatch.differentiators,
        bonus: marketMatch.bonus
      },
      insights: {
        unique_to_job: uniqueToJob,
        unique_to_market: uniqueToMarket.map(s => s.canonical_name)
      },
      market_context: {
        job_count: marketData.job_count,
        role: classification.role,
        specialty: classification.specialty,
        experience: classification.experience,
        description: buildContextDescription(classification)
      },
      summary: {
        job_skills_count: jobSkills.length,
        market_skills_count: marketData.skills.length,
        resume_skills_count: resumeSkills.length,
        ...marketMatch.summary
      }
    };

    // Store result in database
    await storeAnalysisResult(supabase, analysisId, result);

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error in analyze-job-posting:', error);
    return new Response(
      JSON.stringify({ error: error.message || 'Internal server error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

async function storeAnalysisResult(supabase: any, analysisId: string, result: any) {
  try {
    // Create analysis job
    const { data: job, error: jobError } = await supabase
      .from('analysis_jobs')
      .insert({
        id: analysisId,
        status: 'completed',
        progress_step: 'Analysis complete',
        progress_percentage: 100
      })
      .select()
      .single();

    if (jobError) {
      console.error('Failed to create analysis job:', jobError);
      return;
    }

    // Store result
    const { error: resultError } = await supabase
      .from('analysis_results')
      .insert({
        analysis_job_id: analysisId,
        result_data: result
      });

    if (resultError) {
      console.error('Failed to store analysis result:', resultError);
    }
  } catch (error) {
    console.error('Error storing analysis result:', error);
  }
}

function calculateJobMatch(
  resumeSkills: string[],
  jobSkills: string[]
): { score: number; matched: string[]; gaps: string[] } {
  const resumeSet = new Set(resumeSkills.map(s => s.toLowerCase().trim()));
  
  const matched = jobSkills.filter(skill => 
    resumeSet.has(skill.toLowerCase().trim())
  );
  
  const gaps = jobSkills.filter(skill => 
    !resumeSet.has(skill.toLowerCase().trim())
  );
  
  const score = jobSkills.length > 0
    ? Math.round((matched.length / jobSkills.length) * 100)
    : 0;
  
  return { score, matched, gaps };
}

function buildContextDescription(classification: {
  role: string;
  specialty: string | null;
  experience: string;
}): string {
  const parts = [classification.role];
  if (classification.specialty) {
    parts.push(classification.specialty);
  }
  parts.push(classification.experience);
  return parts.join(' / ');
}
