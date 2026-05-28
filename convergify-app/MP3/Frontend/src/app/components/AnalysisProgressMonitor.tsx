/**
 * Analysis Progress Monitor
 * Shows simple loading state while analysis runs in background
 */
import { useEffect } from 'react';
import { Loader2, CheckCircle, AlertCircle, Sparkles, Coffee } from 'lucide-react';
import { Card, CardContent } from '@/app/components/ui/card';
import { useAnalysisStatus } from '@/hooks/useApi';

interface AnalysisProgressMonitorProps {
  analysisId: string;
  onComplete?: () => void;
  onError?: (error: string) => void;
}

export function AnalysisProgressMonitor({ 
  analysisId, 
  onComplete, 
  onError 
}: AnalysisProgressMonitorProps) {
  const { data: analysisStatus } = useAnalysisStatus(analysisId, true);

  useEffect(() => {
    if (!analysisStatus) return;

    // Check if analysis is complete
    if (analysisStatus.status === 'completed') {
      onComplete?.();
      return;
    }

    // Check if analysis failed
    if (analysisStatus.status === 'failed') {
      onError?.(analysisStatus.error_message || 'Analysis failed');
      return;
    }
  }, [analysisStatus, onComplete, onError]);

  const isComplete = analysisStatus?.status === 'completed';
  const isError = analysisStatus?.status === 'failed';
  const isRunning = analysisStatus?.status === 'running';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 p-6">
      <Card className="w-full max-w-2xl shadow-2xl">
        <CardContent className="p-12">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
              <Sparkles className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent mb-3">
              Strategic Career Analysis
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Analyzing your resume against market intelligence
            </p>
          </div>

          {/* Status Display */}
          <div className="text-center">
            {isError ? (
              <>
                <div className="flex items-center justify-center mb-6">
                  <AlertCircle className="w-16 h-16 text-red-600 animate-in fade-in" />
                </div>
                <div className="p-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <p className="text-lg font-semibold text-red-700 dark:text-red-300 mb-2">
                    Analysis Failed
                  </p>
                  <p className="text-sm text-red-600 dark:text-red-400">
                    {analysisStatus?.error_message || 'An error occurred during analysis'}
                  </p>
                </div>
              </>
            ) : isComplete ? (
              <>
                <div className="flex items-center justify-center mb-6">
                  <CheckCircle className="w-16 h-16 text-green-600 animate-in fade-in" />
                </div>
                <div className="p-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <p className="text-lg font-semibold text-green-700 dark:text-green-300 mb-2">
                    ✨ Analysis Complete!
                  </p>
                  <p className="text-sm text-green-600 dark:text-green-400">
                    Redirecting to results...
                  </p>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center justify-center mb-6">
                  <Loader2 className="w-16 h-16 text-blue-600 animate-spin" />
                </div>
                <div className="space-y-4">
                  <p className="text-xl font-semibold text-gray-900 dark:text-white">
                    Analysis in Progress
                  </p>
                  <p className="text-gray-600 dark:text-gray-400">
                    This may take a few minutes...
                  </p>
                  
                  {/* Friendly message */}
                  <div className="mt-8 p-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <div className="flex items-center justify-center gap-3 mb-3">
                      <Coffee className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      <p className="text-sm font-medium text-blue-700 dark:text-blue-300">
                        Feel free to grab a coffee!
                      </p>
                    </div>
                    <p className="text-xs text-blue-600 dark:text-blue-400">
                      You can switch to other tabs and come back later. We'll keep your analysis running in the background.
                    </p>
                  </div>

                  {/* What's happening */}
                  <div className="mt-6 text-left">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      What we're doing:
                    </p>
                    <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                      <li className="flex items-start gap-2">
                        <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                        <span>Extracting skills from your resume</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                        <span>Analyzing job market requirements</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                        <span>Matching your skills with market demand</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                        <span>Generating personalized recommendations</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
