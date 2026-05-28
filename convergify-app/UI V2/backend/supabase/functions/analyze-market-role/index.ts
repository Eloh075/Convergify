import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from 'jsr:@supabase/supabase-js@2';
import { getMarketSkills } from '../_shared/market-skills.ts';
import { calculateGapAnalysis } from '../_shared/gap-analysis.ts';
import { extractResumeSkills } from '../_shared/resume-extractor.ts';

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

    const { role, specialty, experience_levels, resume_file } = await req.json();

    // Validate input
    if (!role || !experience_levels || !Array.isArray(experience_levels) || experience_levels.length === 0) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields: role, experience_levels' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    if (!resume_file) {
      return new Response(
        JSON.stringify({ error: 'Missing resume_file' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Check file size (base64 encoded)
    const fileSizeMB = (resume_file.length * 0.75) / (1024 * 1024); // base64 is ~33% larger
    console.log(`Resume file size: ${fileSizeMB.toFixed(2)} MB`);
    
    if (fileSizeMB > 5) {
      return new Response(
        JSON.stringify({ error: 'Resume file too large. Maximum size is 5MB.' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Generate analysis ID
    const analysisId = crypto.randomUUID();

    // Step 1: Extract skills from resume using Gemini
    const resumeSkills = await extractResumeSkills(resume_file, supabaseUrl, supabaseKey);

    // Step 2: Get market skills for selected contexts
    const marketData = await getMarketSkills(
      supabaseUrl,
      supabaseKey,
      role,
      specialty || null,
      experience_levels
    );

    if (marketData.skills.length === 0) {
      return new Response(
        JSON.stringify({ 
          error: 'Insufficient market data for selected role/specialty/experience levels',
          suggestion: 'Try selecting different experience levels or a more general specialty'
        }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Step 3: Calculate gap analysis
    const gapAnalysis = calculateGapAnalysis(resumeSkills, marketData.skills);

    // Build response
    const result = {
      analysis_id: analysisId,
      match_score: gapAnalysis.match_score,
      market_context: {
        job_count: marketData.job_count,
        role,
        specialty: specialty || null,
        experience_levels,
        description: buildContextDescription(role, specialty, experience_levels)
      },
      dealbreakers: gapAnalysis.dealbreakers,
      differentiators: gapAnalysis.differentiators,
      bonus: gapAnalysis.bonus,
      summary: gapAnalysis.summary
    };

    // Store result in database
    await storeAnalysisResult(supabase, analysisId, result);

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error in analyze-market-role:', error);
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

function buildContextDescription(
  role: string,
  specialty: string | null,
  experienceLevels: string[]
): string {
  const parts = [role];
  
  if (specialty) {
    parts.push(specialty);
  }
  
  if (experienceLevels.length === 1) {
    parts.push(experienceLevels[0]);
  } else {
    parts.push(experienceLevels.join(' + '));
  }
  
  return parts.join(' / ');
}
