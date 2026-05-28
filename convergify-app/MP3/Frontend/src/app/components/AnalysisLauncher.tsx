import { useState, useEffect } from 'react';
import { 
  Play, 
  Settings, 
  FileText, 
  Briefcase, 
  Target, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  Search,
  ArrowRight,
  BarChart3,
  TrendingUp,
  Users
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
import { Badge } from '@/app/components/ui/badge';
import { Checkbox } from '@/app/components/ui/checkbox';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { 
  useResumes, 
  useJobs, 
  useJobGroups,
  useCreateAnalysis,
  useAnalysisStatus
} from '@/hooks/useApi';
import { ProgressMonitor } from '@/app/components/ProgressMonitor';
import type { 
  AnalysisCreateRequest 
} from '@/types/api';

interface AnalysisLauncherProps {
  onAnalysisStarted?: (analysisId: string) => void;
  onViewResults?: (analysisId: string) => void;
}

type AnalysisType = 'comprehensive' | 'single_job' | 'market_analysis';
type SelectionMode = 'individual' | 'group' | 'all';

// Resume Selection Component
function ResumeSelector({
  selectedResumeId,
  onSelectResume,
}: {
  selectedResumeId: string | null;
  onSelectResume: (resumeId: string | null) => void;
}) {
  const { data: resumes, isLoading } = useResumes();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600 dark:text-gray-300">Loading resumes...</span>
      </div>
    );
  }

  if (!resumes || resumes.length === 0) {
    return (
      <div className="text-center py-8">
        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 dark:text-gray-300 mb-4">No resumes available</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">Upload a resume first to start analysis</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Select Resume</h3>
        <Badge variant="secondary">{resumes.length} available</Badge>
      </div>
      
      <div className="space-y-2 max-h-60 overflow-y-auto">
        {resumes.map((resume) => (
          <div
            key={resume.id}
            className={`p-3 border rounded-lg cursor-pointer transition-all ${
              selectedResumeId === resume.id
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            }`}
            onClick={() => onSelectResume(resume.id)}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{resume.filename}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Uploaded {new Date(resume.upload_date).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Badge 
                  variant={resume.analysis_status === 'completed' ? 'default' : 'secondary'}
                  className="text-xs"
                >
                  {resume.analysis_status}
                </Badge>
                {selectedResumeId === resume.id && (
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                )}
              </div>
            </div>
            {resume.extracted_skills && resume.extracted_skills.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {resume.extracted_skills.slice(0, 3).map((skill, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {skill}
                  </Badge>
                ))}
                {resume.extracted_skills.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{resume.extracted_skills.length - 3} more
                  </Badge>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Job Selection Component
function JobSelector({
  selectedJobIds,
  onSelectJobs,
  selectionMode,
  onSelectionModeChange,
}: {
  selectedJobIds: string[];
  onSelectJobs: (jobIds: string[]) => void;
  selectionMode: SelectionMode;
  onSelectionModeChange: (mode: SelectionMode) => void;
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGroupId, setSelectedGroupId] = useState<string>('');
  
  const { data: jobs, isLoading: jobsLoading } = useJobs();
  const { data: groups, isLoading: groupsLoading } = useJobGroups();

  const filteredJobs = jobs?.filter(job =>
    job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    job.company.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const handleJobToggle = (jobId: string) => {
    if (selectedJobIds.includes(jobId)) {
      onSelectJobs(selectedJobIds.filter(id => id !== jobId));
    } else {
      onSelectJobs([...selectedJobIds, jobId]);
    }
  };

  const handleGroupSelect = (groupId: string) => {
    setSelectedGroupId(groupId);
    const group = groups?.find(g => g.id === groupId);
    if (group) {
      onSelectJobs(group.job_ids);
    }
  };

  const handleSelectAll = () => {
    if (selectedJobIds.length === filteredJobs.length) {
      onSelectJobs([]);
    } else {
      onSelectJobs(filteredJobs.map(job => job.id));
    }
  };

  if (jobsLoading || groupsLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600 dark:text-gray-300">Loading jobs...</span>
      </div>
    );
  }

  if (!jobs || jobs.length === 0) {
    return (
      <div className="text-center py-8">
        <Briefcase className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 dark:text-gray-300 mb-4">No jobs available</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">Add some jobs first to start analysis</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Select Jobs</h3>
        <Badge variant="secondary">{jobs.length} available</Badge>
      </div>

      {/* Selection Mode */}
      <Tabs value={selectionMode} onValueChange={(value) => onSelectionModeChange(value as SelectionMode)}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="individual">Individual</TabsTrigger>
          <TabsTrigger value="group">By Group</TabsTrigger>
          <TabsTrigger value="all">All Jobs</TabsTrigger>
        </TabsList>

        <TabsContent value="individual" className="space-y-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              placeholder="Search jobs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Select All */}
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSelectAll}
              className="gap-2"
            >
              <CheckCircle className="w-4 h-4" />
              {selectedJobIds.length === filteredJobs.length ? 'Deselect All' : 'Select All'}
            </Button>
            {selectedJobIds.length > 0 && (
              <span className="text-sm text-gray-600 dark:text-gray-300">
                {selectedJobIds.length} selected
              </span>
            )}
          </div>

          {/* Job List */}
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {filteredJobs.map((job) => (
              <div
                key={job.id}
                className={`p-3 border rounded-lg cursor-pointer transition-all ${
                  selectedJobIds.includes(job.id)
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
                onClick={() => handleJobToggle(job.id)}
              >
                <div className="flex items-start gap-3">
                  <Checkbox
                    checked={selectedJobIds.includes(job.id)}
                    onChange={() => handleJobToggle(job.id)}
                    className="mt-1"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{job.title}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-300">{job.company}</p>
                    {job.location && (
                      <p className="text-xs text-gray-500 dark:text-gray-400">{job.location}</p>
                    )}
                    {job.required_skills && job.required_skills.length > 0 && (
                      <div className="mt-1 flex flex-wrap gap-1">
                        {job.required_skills.slice(0, 2).map((skill, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                        {job.required_skills.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{job.required_skills.length - 2}
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="group" className="space-y-3">
          {groups && groups.length > 0 ? (
            <div className="space-y-2">
              {groups.map((group) => (
                <div
                  key={group.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-all ${
                    selectedGroupId === group.id
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                  onClick={() => handleGroupSelect(group.id)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{group.name}</p>
                      {group.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-300">{group.description}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{group.job_count} jobs</Badge>
                      {selectedGroupId === group.id && (
                        <CheckCircle className="w-4 h-4 text-blue-600" />
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Users className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600 dark:text-gray-300">No job groups available</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Create job groups first</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="all" className="space-y-3">
          <div className="text-center py-8">
            <Target className="w-12 h-12 text-blue-600 mx-auto mb-4" />
            <p className="font-medium text-gray-900 dark:text-white">Analyze All Jobs</p>
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
              This will analyze your resume against all {jobs.length} jobs in the system
            </p>
            <Button
              className="mt-4"
              onClick={() => onSelectJobs(jobs.map(job => job.id))}
            >
              Select All {jobs.length} Jobs
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Analysis Configuration Component
function AnalysisConfig({
  analysisType,
  onAnalysisTypeChange,
  config,
  onConfigChange,
}: {
  analysisType: AnalysisType;
  onAnalysisTypeChange: (type: AnalysisType) => void;
  config: Record<string, any>;
  onConfigChange: (config: Record<string, any>) => void;
}) {
  const analysisTypes = [
    {
      id: 'comprehensive' as AnalysisType,
      name: 'Comprehensive Analysis',
      description: 'Full analysis including skill gaps, market insights, and optimization recommendations',
      icon: BarChart3,
      features: ['Skill Gap Analysis', 'Market Insights', 'Resume Optimization', 'Career Recommendations']
    },
    {
      id: 'single_job' as AnalysisType,
      name: 'Single Job Analysis',
      description: 'Focus on analyzing fit for specific job opportunities',
      icon: Target,
      features: ['Job Matching', 'Skill Alignment', 'Gap Identification', 'Targeted Recommendations']
    },
    {
      id: 'market_analysis' as AnalysisType,
      name: 'Market Analysis',
      description: 'Analyze market demand and salary insights for your skills',
      icon: TrendingUp,
      features: ['Market Demand', 'Salary Insights', 'Industry Trends', 'Competition Analysis']
    }
  ];

  return (
    <div className="space-y-4">
      <h3 className="font-semibold">Analysis Type</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {analysisTypes.map((type) => {
          const Icon = type.icon;
          return (
            <Card
              key={type.id}
              className={`cursor-pointer transition-all ${
                analysisType === type.id
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'hover:border-gray-300'
              }`}
              onClick={() => onAnalysisTypeChange(type.id)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <Icon className={`w-5 h-5 ${
                    analysisType === type.id ? 'text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400'
                  }`} />
                  <CardTitle className="text-base">{type.name}</CardTitle>
                  {analysisType === type.id && (
                    <CheckCircle className="w-4 h-4 text-blue-600 ml-auto" />
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">{type.description}</p>
                <div className="space-y-1">
                  {type.features.map((feature, index) => (
                    <div key={index} className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                      <div className="w-1 h-1 bg-gray-400 rounded-full" />
                      {feature}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Additional Configuration */}
      {analysisType && (
        <div className="space-y-3 pt-4 border-t">
          <h4 className="font-medium">Additional Options</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Priority Focus</label>
              <Select
                value={config.priority || 'balanced'}
                onValueChange={(value) => onConfigChange({ ...config, priority: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="balanced">Balanced Analysis</SelectItem>
                  <SelectItem value="skills">Skills-Focused</SelectItem>
                  <SelectItem value="salary">Salary-Focused</SelectItem>
                  <SelectItem value="growth">Growth-Focused</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Experience Level</label>
              <Select
                value={config.experience_level || 'auto'}
                onValueChange={(value) => onConfigChange({ ...config, experience_level: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">Auto-Detect</SelectItem>
                  <SelectItem value="entry">Entry Level</SelectItem>
                  <SelectItem value="mid">Mid Level</SelectItem>
                  <SelectItem value="senior">Senior Level</SelectItem>
                  <SelectItem value="executive">Executive</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="include_salary"
              checked={config.include_salary || false}
              onCheckedChange={(checked) => onConfigChange({ ...config, include_salary: checked })}
            />
            <label htmlFor="include_salary" className="text-sm">
              Include salary analysis and recommendations
            </label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="generate_optimized"
              checked={config.generate_optimized || false}
              onCheckedChange={(checked) => onConfigChange({ ...config, generate_optimized: checked })}
            />
            <label htmlFor="generate_optimized" className="text-sm">
              Generate optimized resume version
            </label>
          </div>
        </div>
      )}
    </div>
  );
}
// Analysis Progress Monitor Component
function AnalysisProgress({
  analysisId,
  onComplete,
  onError,
}: {
  analysisId: string;
  onComplete: () => void;
  onError: (error: string) => void;
}) {
  const { data: status, error } = useAnalysisStatus(analysisId, true);

  useEffect(() => {
    if (status?.status === 'completed') {
      onComplete();
    } else if (status?.status === 'failed') {
      onError(status.error_message || 'Analysis failed');
    }
  }, [status, onComplete, onError]);

  if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-red-600 font-medium">Failed to get analysis status</p>
        <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">Please try again later</p>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="text-center py-8">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
        <p className="text-gray-600 dark:text-gray-300">Initializing analysis...</p>
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case 'pending':
        return <Clock className="w-6 h-6 text-yellow-500" />;
      case 'running':
        return <Loader2 className="w-6 h-6 animate-spin text-blue-600" />;
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'failed':
        return <AlertCircle className="w-6 h-6 text-red-500" />;
      default:
        return <Clock className="w-6 h-6 text-gray-400" />;
    }
  };

  const getStatusText = () => {
    switch (status.status) {
      case 'pending':
        return 'Analysis queued';
      case 'running':
        return 'Analysis in progress';
      case 'completed':
        return 'Analysis completed';
      case 'failed':
        return 'Analysis failed';
      default:
        return 'Unknown status';
    }
  };

  const progressPercentage = status.progress_percentage || 0;

  return (
    <div className="space-y-6">
      <div className="text-center">
        {getStatusIcon()}
        <h3 className="text-lg font-semibold mt-2">{getStatusText()}</h3>
        {status.status === 'running' && (
          <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
            This may take a few minutes...
          </p>
        )}
      </div>

      {/* Progress Bar */}
      {status.status === 'running' && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress</span>
            <span>{progressPercentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      )}

      {/* Analysis Steps */}
      <div className="space-y-3">
        <h4 className="font-medium">Analysis Steps</h4>
        <div className="space-y-2">
          {[
            { step: 'Extracting skills from resume', completed: progressPercentage > 20 },
            { step: 'Processing job requirements', completed: progressPercentage > 40 },
            { step: 'Analyzing skill gaps', completed: progressPercentage > 60 },
            { step: 'Generating market insights', completed: progressPercentage > 80 },
            { step: 'Creating recommendations', completed: progressPercentage >= 100 },
          ].map((item, index) => (
            <div key={index} className="flex items-center gap-3">
              {item.completed ? (
                <CheckCircle className="w-4 h-4 text-green-600" />
              ) : progressPercentage > (index + 1) * 20 - 20 ? (
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
              ) : (
                <div className="w-4 h-4 border-2 border-gray-300 rounded-full" />
              )}
              <span className={`text-sm ${
                item.completed ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-gray-400'
              }`}>
                {item.step}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Task Details */}
      {status.task_status && (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          <h4 className="font-medium mb-2">Task Details</h4>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span>Task ID:</span>
              <span className="font-mono text-xs">{status.task_id}</span>
            </div>
            <div className="flex justify-between">
              <span>Started:</span>
              <span>{status.started_at ? new Date(status.started_at).toLocaleTimeString() : 'N/A'}</span>
            </div>
            {status.completed_at && (
              <div className="flex justify-between">
                <span>Completed:</span>
                <span>{new Date(status.completed_at).toLocaleTimeString()}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error Details */}
      {status.status === 'failed' && status.error_message && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <h4 className="font-medium text-red-800 dark:text-red-200 mb-2">Error Details</h4>
          <p className="text-sm text-red-700 dark:text-red-300">{status.error_message}</p>
        </div>
      )}
    </div>
  );
}

// Main Analysis Launcher Component
export function AnalysisLauncher({ onAnalysisStarted, onViewResults }: AnalysisLauncherProps) {
  const [currentStep, setCurrentStep] = useState<'configure' | 'select' | 'launch' | 'progress'>('configure');
  const [selectedResumeId, setSelectedResumeId] = useState<string | null>(null);
  const [selectedJobIds, setSelectedJobIds] = useState<string[]>([]);
  const [selectionMode, setSelectionMode] = useState<SelectionMode>('individual');
  const [analysisType, setAnalysisType] = useState<AnalysisType>('comprehensive');
  const [config, setConfig] = useState<Record<string, any>>({
    priority: 'balanced',
    experience_level: 'auto',
    include_salary: true,
    generate_optimized: true,
  });
  const [currentAnalysisId, setCurrentAnalysisId] = useState<string | null>(null);

  const createAnalysisMutation = useCreateAnalysis();

  const canProceedToNext = () => {
    switch (currentStep) {
      case 'configure':
        return analysisType !== null;
      case 'select':
        return selectedResumeId && selectedJobIds.length > 0;
      case 'launch':
        return true;
      default:
        return false;
    }
  };

  const handleNext = () => {
    switch (currentStep) {
      case 'configure':
        setCurrentStep('select');
        break;
      case 'select':
        setCurrentStep('launch');
        break;
      case 'launch':
        handleStartAnalysis();
        break;
    }
  };

  const handleBack = () => {
    switch (currentStep) {
      case 'select':
        setCurrentStep('configure');
        break;
      case 'launch':
        setCurrentStep('select');
        break;
      case 'progress':
        setCurrentStep('launch');
        break;
    }
  };

  const handleStartAnalysis = () => {
    if (!selectedResumeId || selectedJobIds.length === 0) {
      toast.error('Please select a resume and at least one job');
      return;
    }

    const analysisRequest: AnalysisCreateRequest = {
      resume_id: selectedResumeId,
      job_ids: selectedJobIds,
      analysis_type: analysisType,
      ...config,
    };

    createAnalysisMutation.mutate(analysisRequest, {
      onSuccess: (response) => {
        setCurrentAnalysisId(response.id);
        setCurrentStep('progress');
        onAnalysisStarted?.(response.id);
        toast.success('Analysis started successfully');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to start analysis');
      },
    });
  };

  const handleAnalysisComplete = () => {
    if (currentAnalysisId) {
      onViewResults?.(currentAnalysisId);
    }
    toast.success('Analysis completed successfully!');
  };

  const handleAnalysisError = (error: string) => {
    toast.error(`Analysis failed: ${error}`);
    setCurrentStep('launch');
  };

  const handleReset = () => {
    setCurrentStep('configure');
    setSelectedResumeId(null);
    setSelectedJobIds([]);
    setCurrentAnalysisId(null);
    setAnalysisType('comprehensive');
    setConfig({
      priority: 'balanced',
      experience_level: 'auto',
      include_salary: true,
      generate_optimized: true,
    });
  };

  const getStepTitle = () => {
    switch (currentStep) {
      case 'configure':
        return 'Configure Analysis';
      case 'select':
        return 'Select Data';
      case 'launch':
        return 'Review & Launch';
      case 'progress':
        return 'Analysis in Progress';
      default:
        return 'Analysis Launcher';
    }
  };

  const getStepDescription = () => {
    switch (currentStep) {
      case 'configure':
        return 'Choose the type of analysis and configure options';
      case 'select':
        return 'Select the resume and jobs to analyze';
      case 'launch':
        return 'Review your selections and start the analysis';
      case 'progress':
        return 'Your analysis is being processed';
      default:
        return '';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-semibold mb-3">{getStepTitle()}</h1>
        <p className="text-gray-600 dark:text-gray-400">{getStepDescription()}</p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {['configure', 'select', 'launch', 'progress'].map((step, index) => (
            <div key={step} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  currentStep === step
                    ? 'bg-blue-600 text-white'
                    : index < ['configure', 'select', 'launch', 'progress'].indexOf(currentStep)
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                }`}
              >
                {index < ['configure', 'select', 'launch', 'progress'].indexOf(currentStep) ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  index + 1
                )}
              </div>
              {index < 3 && (
                <div
                  className={`w-16 h-1 mx-2 ${
                    index < ['configure', 'select', 'launch', 'progress'].indexOf(currentStep)
                      ? 'bg-green-600'
                      : 'bg-gray-200 dark:bg-gray-700'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between mt-2">
          <span className="text-xs text-gray-500 dark:text-gray-400">Configure</span>
          <span className="text-xs text-gray-500 dark:text-gray-400">Select</span>
          <span className="text-xs text-gray-500 dark:text-gray-400">Launch</span>
          <span className="text-xs text-gray-500 dark:text-gray-400">Progress</span>
        </div>
      </div>

      {/* Content */}
      <Card className="mb-6">
        <CardContent className="p-6">
          {currentStep === 'configure' && (
            <AnalysisConfig
              analysisType={analysisType}
              onAnalysisTypeChange={setAnalysisType}
              config={config}
              onConfigChange={setConfig}
            />
          )}

          {currentStep === 'select' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <ResumeSelector
                selectedResumeId={selectedResumeId}
                onSelectResume={setSelectedResumeId}
              />
              <JobSelector
                selectedJobIds={selectedJobIds}
                onSelectJobs={setSelectedJobIds}
                selectionMode={selectionMode}
                onSelectionModeChange={setSelectionMode}
              />
            </div>
          )}

          {currentStep === 'launch' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold">Review Your Analysis Configuration</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Analysis Type */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Settings className="w-4 h-4" />
                      Analysis Type
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="font-medium capitalize">{analysisType.replace('_', ' ')}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                      Priority: {config.priority || 'Balanced'}
                    </p>
                  </CardContent>
                </Card>

                {/* Resume */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Resume
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="font-medium">Selected</p>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                      Ready for analysis
                    </p>
                  </CardContent>
                </Card>

                {/* Jobs */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Briefcase className="w-4 h-4" />
                      Jobs
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="font-medium">{selectedJobIds.length} selected</p>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                      Mode: {selectionMode}
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Options Summary */}
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <h4 className="font-medium mb-3">Analysis Options</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span>Experience Level:</span>
                    <span className="capitalize">{config.experience_level || 'Auto'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Include Salary:</span>
                    <span>{config.include_salary ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Generate Optimized Resume:</span>
                    <span>{config.generate_optimized ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Priority Focus:</span>
                    <span className="capitalize">{config.priority || 'Balanced'}</span>
                  </div>
                </div>
              </div>

              {/* Estimated Time */}
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                <Clock className="w-4 h-4" />
                <span>Estimated completion time: 3-5 minutes</span>
              </div>
            </div>
          )}

          {currentStep === 'progress' && currentAnalysisId && (
            <ProgressMonitor
              taskId={currentAnalysisId}
              onTaskComplete={handleAnalysisComplete}
              onTaskError={handleAnalysisError}
              showDetails={true}
            />
          )}
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex items-center justify-between">
        <div>
          {currentStep !== 'configure' && currentStep !== 'progress' && (
            <Button variant="outline" onClick={handleBack}>
              Back
            </Button>
          )}
        </div>

        <div className="flex items-center gap-3">
          {currentStep !== 'progress' && (
            <Button variant="outline" onClick={handleReset}>
              Reset
            </Button>
          )}
          
          {currentStep !== 'progress' && (
            <Button
              onClick={handleNext}
              disabled={!canProceedToNext() || createAnalysisMutation.isPending}
              className="gap-2"
            >
              {createAnalysisMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Starting...
                </>
              ) : currentStep === 'launch' ? (
                <>
                  <Play className="w-4 h-4" />
                  Start Analysis
                </>
              ) : (
                <>
                  Next
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}