import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    // Extract analysis ID from URL path
    const url = new URL(req.url);
    const pathParts = url.pathname.split('/');
    const analysisId = pathParts[pathParts.length - 1];

    if (!analysisId || analysisId === 'analysis-status') {
      return new Response(
        JSON.stringify({ error: 'Missing analysis ID in URL path' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // TODO: In production, query database for actual job status
    // For now, return mock progress data
    
    // Simulate different stages of processing
    const mockStages = [
      { step: 'Parsing resume...', percentage: 20 },
      { step: 'Extracting skills from resume...', percentage: 40 },
      { step: 'Querying market data...', percentage: 60 },
      { step: 'Calculating gap analysis...', percentage: 80 },
      { step: 'Finalizing results...', percentage: 95 }
    ];

    // Randomly select a stage for demo purposes
    const randomStage = mockStages[Math.floor(Math.random() * mockStages.length)];

    // Simulate completion after a few polls (in production, check actual job status)
    const shouldComplete = Math.random() > 0.7;

    const response = shouldComplete
      ? {
          status: 'completed',
          progress: {
            step: 'Analysis complete!',
            percentage: 100
          }
        }
      : {
          status: 'processing',
          progress: randomStage
        };

    return new Response(JSON.stringify(response), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error in analysis-status:', error);
    return new Response(
      JSON.stringify({ error: error.message || 'Internal server error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
