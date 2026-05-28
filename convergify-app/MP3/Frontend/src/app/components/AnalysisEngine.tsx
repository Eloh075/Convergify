import { useState, useEffect } from 'react';
import { 
  Sparkles, 
  CheckCircle2, 
  Loader2, 
  FileText, 
  Zap, 
  Target,
  Upload,
  Building2,
  Download,
  Save,
  X,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import { IntelligenceDashboard } from '@/app/components/IntelligenceDashboard';
import { 
  useResumes, 
  useCreateAnalysis, 
  useAnalysisStatus, 
  useAnalysisResults,
  useOptimizeResume,
  useTaskStatus
} from '@/hooks/useApi';
import type { AnalysisCreateRequest } from '@/types/api';

interface AnalysisEngineProps {
  preSelectedJobIds: string[];
  onOptimize: () => void;
  onBackToJobs: () => void;
}

type Phase = 'entry' | 'resume-selection' | 'processing' | 'report' | 'optimization' | 'comparison';

interface ProcessingStep {
  id: number;
  label: string;
  status: 'pending' | 'active' | 'complete';
}

// Resume Selection Component
function ResumeSelection({ 
  onSelect, 
  onBack 
}: { 
  onSelect: (resumeId: string) => void;
  onBack: () => void;
}) {
  const { data: resumes = [], isLoading, error } = useResumes();

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading resumes...</p>
        </div>
      </div>
    );
  }

  if (error || resumes.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2 dark:text-white">No Resumes Found</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            You need to upload a resume before running analysis
          </p>
          <Button variant="outline" onClick={onBack}>
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex items-center justify-center p-4 sm:p-8 lg:p-12 bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-[700px]">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4" 
            style={{ backgroundColor: 'var(--primary-blue)' }}>
            <FileText className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-semibold mb-2 dark:text-white">Select Resume</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Choose which resume to analyze against the selected jobs
          </p>
        </div>

        <div className="space-y-3">
          {resumes.map((resume) => (
            <button
              key={resume.id}
              onClick={() => onSelect(resume.id)}
              className="w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-sm transition-all text-left"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold mb-1 dark:text-white">{resume.filename}</h3>
                  <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <span>Uploaded {new Date(resume.upload_date).toLocaleDateString()}</span>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      resume.analysis_status === 'completed' 
                        ? 'bg-green-100 text-green-700' 
                        : resume.analysis_status === 'processing'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {resume.analysis_status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
                <div className="text-gray-400">
                  <Building2 className="w-5 h-5" />
                </div>
              </div>
            </button>
          ))}
        </div>

        <div className="mt-6 text-center">
          <Button variant="outline" onClick={onBack}>
            Back to Jobs
          </Button>
        </div>
      </div>
    </div>
  );
}

// Phase 1A: Pre-selected Jobs (Ready to Launch)
function PreSelectedEntry({ 
  jobCount, 
  onStart 
}: { 
  jobCount: number; 
  onStart: () => void;
}) {
  return (
    <div className="flex-1 flex items-center justify-center p-4 sm:p-8 lg:p-12 bg-gray-50 dark:bg-gray-900 transition-colors">
      <div className="w-full max-w-[600px]">
        {/* Ready Card */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center shadow-sm">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-6" 
            style={{ backgroundColor: 'var(--primary-blue)' }}>
            <Target className="w-8 h-8 text-white" />
          </div>
          
          <h2 className="text-2xl font-semibold mb-3 dark:text-white">
            Targeting {jobCount} {jobCount === 1 ? 'Role' : 'Roles'}
          </h2>
          
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            Ready to analyze market fit across your selected positions
          </p>

          {/* Visual Job Stack */}
          <div className="flex items-center justify-center gap-2 mb-8">
            {[...Array(Math.min(jobCount, 5))].map((_, i) => (
              <div 
                key={i}
                className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-sm"
                style={{ 
                  transform: `translateX(${i * -4}px)`,
                  zIndex: 5 - i 
                }}
              >
                <Building2 className="w-6 h-6 text-white" />
              </div>
            ))}
            {jobCount > 5 && (
              <div className="text-sm font-medium text-gray-500 dark:text-gray-400 ml-2">
                +{jobCount - 5} more
              </div>
            )}
          </div>

          <Button
            size="lg"
            onClick={onStart}
            className="w-full h-14 text-base"
            style={{ backgroundColor: 'var(--primary-blue)' }}
          >
            <Sparkles className="w-5 h-5 mr-2" />
            Start Fit Analysis
          </Button>
        </div>
      </div>
    </div>
  );
}

// Phase 1B: Fresh Start (Scraper Input)
function FreshStartEntry({ 
  onStart 
}: { 
  onStart: (params: { jobTitle: string; jobLevel: string; targetCount: number }) => void;
}) {
  const [jobTitle, setJobTitle] = useState('');
  const [jobLevel, setJobLevel] = useState('');
  const [targetCount, setTargetCount] = useState(10);

  const canStart = jobTitle.trim() && jobLevel;

  const handleSubmit = () => {
    if (canStart) {
      onStart({
        jobTitle: jobTitle.trim(),
        jobLevel,
        targetCount,
      });
    }
  };

  return (
    <div className="flex-1 flex items-center justify-center p-4 sm:p-8 lg:p-12 bg-gray-50 dark:bg-gray-900 transition-colors">
      <div className="w-full max-w-[700px] space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4" 
            style={{ backgroundColor: 'var(--primary-blue)' }}>
            <Zap className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-semibold mb-2 dark:text-white">Market Discovery</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Define your target market and we'll find the best opportunities
          </p>
        </div>

        {/* Input Card */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 space-y-6">
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Job / Sector
            </label>
            <Input
              placeholder="e.g., Business Development, Product Manager"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              className="h-12"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Type
            </label>
            <Select value={jobLevel} onValueChange={setJobLevel}>
              <SelectTrigger className="h-12">
                <SelectValue placeholder="Select job type..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="intern">Intern</SelectItem>
                <SelectItem value="full-time">Full-Time</SelectItem>
                <SelectItem value="senior">Senior</SelectItem>
                <SelectItem value="lead">Lead/Principal</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Target Count
            </label>
            <Input
              type="number"
              min={5}
              max={50}
              value={targetCount}
              onChange={(e) => setTargetCount(Math.min(50, Math.max(5, Number(e.target.value))))}
              className="h-12"
              placeholder="e.g., 10"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Maximum 50 jobs
            </p>
          </div>
        </div>

        {/* CTA */}
        <Button
          size="lg"
          disabled={!canStart}
          onClick={handleSubmit}
          className="w-full h-14 text-base"
          style={{
            backgroundColor: canStart ? 'var(--primary-blue)' : undefined,
          }}
        >
          <Sparkles className="w-5 h-5 mr-2" />
          Discover & Analyze Market
        </Button>
      </div>
    </div>
  );
}

// Phase 2: Processing with Real API Integration
function ProcessingView({ 
  analysisId,
  onComplete,
  onError
}: { 
  analysisId: string;
  onComplete: (results: any) => void;
  onError: (error: string) => void;
}) {
  const [steps, setSteps] = useState<ProcessingStep[]>([
    { id: 1, label: 'Extracting Skills from Resume', status: 'active' },
    { id: 2, label: 'Analyzing Job Requirements', status: 'pending' },
    { id: 3, label: 'Computing Market Intelligence', status: 'pending' },
    { id: 4, label: 'Generating Recommendations', status: 'pending' },
  ]);

  const { data: analysisStatus, error } = useAnalysisStatus(analysisId, true);
  const { data: analysisResults } = useAnalysisResults(analysisId);

  useEffect(() => {
    if (error) {
      onError('Analysis failed to start');
      return;
    }

    if (!analysisStatus) return;

    // Update steps based on analysis progress
    if (analysisStatus.status === 'running') {
      const progress = analysisStatus.progress_percentage || 0;
      
      if (progress >= 25) {
        setSteps(prev => prev.map(s => 
          s.id === 1 ? { ...s, status: 'complete' } : 
          s.id === 2 ? { ...s, status: 'active' } : s
        ));
      }
      if (progress >= 50) {
        setSteps(prev => prev.map(s => 
          s.id === 2 ? { ...s, status: 'complete' } : 
          s.id === 3 ? { ...s, status: 'active' } : s
        ));
      }
      if (progress >= 75) {
        setSteps(prev => prev.map(s => 
          s.id === 3 ? { ...s, status: 'complete' } : 
          s.id === 4 ? { ...s, status: 'active' } : s
        ));
      }
    } else if (analysisStatus.status === 'completed') {
      setSteps(prev => prev.map(s => ({ ...s, status: 'complete' })));
      
      if (analysisResults) {
        setTimeout(() => onComplete(analysisResults), 1000);
      }
    } else if (analysisStatus.status === 'failed') {
      onError(analysisStatus.error_message || 'Analysis failed');
    }
  }, [analysisStatus, analysisResults, onComplete, onError]);

  return (
    <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-[600px] space-y-8">
        {/* Header */}
        <div className="text-center">
          <div
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4"
            style={{ backgroundColor: 'var(--primary-blue)' }}
          >
            <Loader2 className="w-8 h-8 text-white animate-spin" />
          </div>
          <h1 className="text-2xl font-semibold dark:text-white">Analyzing Career Intelligence...</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Processing your analysis ({analysisStatus?.progress_percentage || 0}% complete)
          </p>
        </div>

        {/* Checklist */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8">
          <div className="space-y-6">
            {steps.map((step) => (
              <div key={step.id} className="flex items-center gap-4">
                {/* Status Icon */}
                <div className="flex-shrink-0">
                  {step.status === 'complete' ? (
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center"
                      style={{ backgroundColor: 'var(--success-green)' }}
                    >
                      <CheckCircle2 className="w-5 h-5 text-white" />
                    </div>
                  ) : step.status === 'active' ? (
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center"
                      style={{ backgroundColor: 'var(--primary-blue)' }}
                    >
                      <Loader2 className="w-5 h-5 text-white animate-spin" />
                    </div>
                  ) : (
                    <div className="w-8 h-8 rounded-full border-2 border-gray-300 dark:border-gray-600" />
                  )}
                </div>

                {/* Label */}
                <p
                  className={`text-base ${
                    step.status === 'pending'
                      ? 'text-gray-400 dark:text-gray-500'
                      : 'font-semibold text-gray-900 dark:text-white'
                  }`}
                >
                  {step.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Phase 4: Side-by-Side Comparison
function ComparisonView({ 
  onSave, 
  onDiscard 
}: { 
  onSave: () => void; 
  onDiscard: () => void;
}) {
  return (
    <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Split Panes */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Original Resume (30%) */}
        <div className="w-[30%] border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 overflow-y-auto">
          <div className="mb-4">
            <h3 className="font-semibold text-sm text-gray-500 dark:text-gray-400 uppercase">Original Resume</h3>
          </div>
          <div className="bg-gray-100 dark:bg-gray-750 rounded-lg p-6 text-sm text-gray-700 dark:text-gray-300 space-y-4">
            <div>
              <h4 className="font-semibold mb-2 dark:text-white">Senior Account Manager</h4>
              <p className="text-xs text-gray-600 dark:text-gray-400">Original version</p>
            </div>
            <div className="space-y-2 text-xs">
              <p>• Managed client relationships across enterprise accounts</p>
              <p>• Led cross-functional teams to deliver solutions</p>
              <p>• Achieved 120% quota attainment in FY2023</p>
            </div>
          </div>
        </div>

        {/* Right: Optimized Resume (70%) */}
        <div className="flex-1 p-6 overflow-y-auto bg-gray-50 dark:bg-gray-900">
          <div className="max-w-[800px]">
            <div className="mb-4">
              <h3 className="font-semibold text-sm text-gray-500 dark:text-gray-400 uppercase">Optimized Resume</h3>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8 space-y-6">
              <div>
                <h4 className="font-semibold text-lg mb-2 dark:text-white">Senior Account Manager</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">Optimized for Market Fit: 88.2%</p>
              </div>
              
              <div className="space-y-3">
                <p className="text-sm dark:text-gray-300">
                  • Managed client relationships across enterprise accounts
                </p>
                <p className="text-sm dark:text-gray-300">
                  • Led cross-functional teams to deliver solutions
                </p>
                <p className="text-sm dark:text-gray-300" style={{ 
                  backgroundColor: '#FFF7ED',
                  borderLeft: '3px solid var(--warning-amber)',
                  paddingLeft: '12px',
                  marginLeft: '-12px',
                  paddingTop: '8px',
                  paddingBottom: '8px'
                }}>
                  • Achieved 120% quota attainment in FY2023 through strategic account planning and consultative selling methodologies
                </p>
                <p className="text-sm dark:text-gray-300" style={{ 
                  backgroundColor: '#FFF7ED',
                  borderLeft: '3px solid var(--warning-amber)',
                  paddingLeft: '12px',
                  marginLeft: '-12px',
                  paddingTop: '8px',
                  paddingBottom: '8px'
                }}>
                  • Leveraged Salesforce CRM and data analytics to optimize pipeline management and forecast accuracy
                </p>
                <p className="text-sm dark:text-gray-300" style={{ 
                  backgroundColor: '#FFF7ED',
                  borderLeft: '3px solid var(--warning-amber)',
                  paddingLeft: '12px',
                  marginLeft: '-12px',
                  paddingTop: '8px',
                  paddingBottom: '8px'
                }}>
                  • Built executive-level relationships with C-suite stakeholders to drive business development initiatives
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Report Below */}
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="max-w-[1200px] mx-auto p-6">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="text-center">
                <div className="text-3xl font-bold" style={{ color: 'var(--primary-blue)' }}>
                  88.2%
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Fit Score</div>
              </div>
            </div>
            <div className="flex-1 text-sm text-gray-600 dark:text-gray-400">
              Resume optimized for market requirements with enhanced skill alignment
            </div>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-4">
        <div className="max-w-[1200px] mx-auto flex items-center justify-end gap-3">
          <Button variant="outline" onClick={onDiscard} className="gap-2">
            <X className="w-4 h-4" />
            Discard Changes
          </Button>
          <Button variant="outline" className="gap-2">
            <Download className="w-4 h-4" />
            Export to PDF
          </Button>
          <Button onClick={onSave} className="gap-2" style={{ backgroundColor: 'var(--primary-blue)' }}>
            <Save className="w-4 h-4" />
            Save to Resume Vault
          </Button>
        </div>
      </div>
    </div>
  );
}

export function AnalysisEngine({
  preSelectedJobIds,
  onOptimize,
  onBackToJobs,
}: AnalysisEngineProps) {
  const [phase, setPhase] = useState<Phase>(
    preSelectedJobIds.length > 0 ? 'resume-selection' : 'entry'
  );
  const [currentStep, setCurrentStep] = useState<string>('Resume Selection');
  const [selectedResumeId, setSelectedResumeId] = useState<string>('');
  const [analysisId, setAnalysisId] = useState<string>('');
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [optimizationTaskId, setOptimizationTaskId] = useState<string>('');

  const createAnalysisMutation = useCreateAnalysis();
  const optimizeResumeMutation = useOptimizeResume();
  const { data: optimizationStatus } = useTaskStatus(optimizationTaskId, !!optimizationTaskId);

  const hasPreSelected = preSelectedJobIds.length > 0;

  const handleResumeSelect = (resumeId: string) => {
    setSelectedResumeId(resumeId);
    
    // Create analysis
    const analysisData: AnalysisCreateRequest = {
      resume_id: resumeId,
      job_ids: preSelectedJobIds,
      analysis_type: 'comprehensive'
    };

    createAnalysisMutation.mutate(analysisData, {
      onSuccess: (response) => {
        setAnalysisId(response.id);
        setCurrentStep('Market Analysis');
        setPhase('processing');
      },
      onError: (error) => {
        toast.error('Failed to start analysis');
        console.error('Analysis creation failed:', error);
      }
    });
  };

  const handleStartFromFresh = (params: { jobTitle: string; jobLevel: string; targetCount: number }) => {
    // This would trigger job scraping first, then analysis
    // For now, we'll show an error since we need jobs first
    toast.error('Please add jobs to your library first, then run analysis');
    onBackToJobs();
  };

  const handleProcessingComplete = (results: any) => {
    setAnalysisResults(results);
    setCurrentStep('Intelligence Report');
    setPhase('report');
  };

  const handleProcessingError = (error: string) => {
    toast.error(error);
    onBackToJobs();
  };

  const handleOptimizeClick = () => {
    if (!selectedResumeId || !analysisId) {
      toast.error('Missing analysis data');
      return;
    }

    setCurrentStep('Optimization');
    setPhase('optimization');

    optimizeResumeMutation.mutate(
      { resumeId: selectedResumeId, analysisId },
      {
        onSuccess: (response) => {
          setOptimizationTaskId(response.task_id);
        },
        onError: (error) => {
          toast.error('Failed to start optimization');
          setPhase('report');
        }
      }
    );
  };

  const handleOptimizationComplete = () => {
    setCurrentStep('Resume Comparison');
    setPhase('comparison');
  };

  const handleSaveToVault = () => {
    onOptimize();
    toast.success('Optimized resume saved to vault');
  };

  const handleDiscard = () => {
    setPhase('report');
    setCurrentStep('Intelligence Report');
  };

  // Monitor optimization progress
  useEffect(() => {
    if (phase === 'optimization' && optimizationStatus?.status === 'SUCCESS') {
      setTimeout(() => {
        handleOptimizationComplete();
      }, 1000);
    } else if (phase === 'optimization' && optimizationStatus?.status === 'FAILURE') {
      toast.error('Optimization failed');
      setPhase('report');
    }
  }, [phase, optimizationStatus]);

  return (
    <div className="flex-1 h-full flex flex-col">
      {/* Status Bar */}
      {phase !== 'entry' && phase !== 'resume-selection' && (
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3 flex-shrink-0">
          <div className="max-w-[1200px] mx-auto">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Market Analysis → {currentStep}
            </p>
          </div>
        </div>
      )}

      {/* Phase Content */}
      {phase === 'entry' && !hasPreSelected && (
        <FreshStartEntry onStart={handleStartFromFresh} />
      )}

      {phase === 'resume-selection' && (
        <ResumeSelection 
          onSelect={handleResumeSelect}
          onBack={onBackToJobs}
        />
      )}

      {phase === 'processing' && analysisId && (
        <ProcessingView 
          analysisId={analysisId}
          onComplete={handleProcessingComplete}
          onError={handleProcessingError}
        />
      )}

      {phase === 'report' && analysisResults && (
        <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-900">
          <IntelligenceDashboard data={analysisResults} onBack={onBackToJobs} />
          
          {/* Floating Action Bar */}
          <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 shadow-lg z-40 lg:ml-60">
            <div className="max-w-[1200px] mx-auto px-4 sm:px-6 py-4 flex items-center justify-center">
              <Button
                size="lg"
                onClick={handleOptimizeClick}
                className="gap-2 h-14 px-8"
                style={{ backgroundColor: 'var(--primary-blue)' }}
              >
                <Sparkles className="w-5 h-5" />
                Optimize Resume for this Analysis
              </Button>
            </div>
          </div>
        </div>
      )}

      {phase === 'optimization' && (
        <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
          <div className="text-center">
            <div
              className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 animate-pulse"
              style={{ backgroundColor: 'var(--primary-blue)' }}
            >
              <Loader2 className="w-8 h-8 text-white animate-spin" />
            </div>
            <h2 className="text-xl font-semibold mb-2 dark:text-white">Optimizing Resume...</h2>
            <p className="text-gray-600 dark:text-gray-400">Tailoring your experience for maximum market fit</p>
            {optimizationStatus?.meta && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                Progress: {optimizationStatus.meta.current || 0} / {optimizationStatus.meta.total || 0}
              </p>
            )}
          </div>
        </div>
      )}

      {phase === 'comparison' && (
        <ComparisonView onSave={handleSaveToVault} onDiscard={handleDiscard} />
      )}
    </div>
  );
}