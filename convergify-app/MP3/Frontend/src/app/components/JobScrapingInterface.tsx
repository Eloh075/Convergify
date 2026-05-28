import { useState, useEffect, useRef } from 'react';
import { 
  Zap, 
  Play, 
  Pause, 
  Square, 
  Settings, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  X,
  Search,
  MapPin,
  Building2,
  TrendingUp,
  BarChart3,
  Download,
  Eye,
  RefreshCw,
  Loader2,
  Calendar,
  Target,
  Activity,
  Users,
  DollarSign,
  Filter,
  ArrowRight
} from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Textarea } from '@/app/components/ui/textarea';
import { Badge } from '@/app/components/ui/badge';
import { Progress } from '@/app/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { 
  useScrapeJobs, 
  useTaskStatus,
  useJobs 
} from '@/hooks/useApi';
import type { 
  ScrapingConfig, 
  TaskStatus,
  Job 
} from '@/types/api';

interface JobScrapingInterfaceProps {
  onJobsScraped?: (jobIds: string[]) => void;
  onClose?: () => void;
}

interface ScrapingSession {
  id: string;
  taskId: string;
  config: ScrapingConfig;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  startTime: Date;
  endTime?: Date;
  jobsFound: number;
  jobIds: string[];
  error?: string;
  statistics?: {
    companies: Record<string, number>;
    topSkills: string[];
    salaryRanges: any;
    employmentTypes: string[];
  };
}

// Configuration Modal
function ScrapingConfigModal({ 
  onClose, 
  onStart,
  initialConfig 
}: { 
  onClose: () => void; 
  onStart: (config: ScrapingConfig) => void;
  initialConfig?: Partial<ScrapingConfig>;
}) {
  const [config, setConfig] = useState<ScrapingConfig>({
    search_terms: initialConfig?.search_terms || [],
    employment_type: initialConfig?.employment_type || 'full-time',
    max_jobs: initialConfig?.max_jobs || 50,
    location: initialConfig?.location || ''
  });
  const [searchTermsText, setSearchTermsText] = useState(
    initialConfig?.search_terms?.join(', ') || ''
  );

  const handleStart = () => {
    const search_terms = searchTermsText
      .split(',')
      .map(term => term.trim())
      .filter(term => term.length > 0);

    if (search_terms.length === 0) {
      toast.error('Please enter at least one search term');
      return;
    }

    const scrapingConfig: ScrapingConfig = {
      ...config,
      search_terms
    };

    onStart(scrapingConfig);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[600px]">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold dark:text-white flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Configure Job Scraping
          </h2>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Search Terms */}
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Search Terms *
            </label>
            <Input
              placeholder="e.g., software engineer, full stack developer, data scientist"
              value={searchTermsText}
              onChange={(e) => setSearchTermsText(e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">
              Separate multiple terms with commas. Each term will be searched separately.
            </p>
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Location
            </label>
            <Input
              placeholder="e.g., Singapore, Remote, San Francisco"
              value={config.location}
              onChange={(e) => setConfig(prev => ({ ...prev, location: e.target.value }))}
            />
          </div>

          {/* Employment Type and Max Jobs */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
                Employment Type
              </label>
              <Select 
                value={config.employment_type} 
                onValueChange={(value) => setConfig(prev => ({ ...prev, employment_type: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Employment Types</SelectItem>
                  <SelectItem value="permanent">Permanent</SelectItem>
                  <SelectItem value="full-time">Full Time</SelectItem>
                  <SelectItem value="part-time">Part Time</SelectItem>
                  <SelectItem value="contract">Contract</SelectItem>
                  <SelectItem value="temporary">Temporary</SelectItem>
                  <SelectItem value="freelance">Freelance</SelectItem>
                  <SelectItem value="internship">Internship/Attachment</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
                Max Jobs per Term
              </label>
              <Input
                type="number"
                min="1"
                max="200"
                value={config.max_jobs}
                onChange={(e) => setConfig(prev => ({ 
                  ...prev, 
                  max_jobs: parseInt(e.target.value) || 50 
                }))}
              />
            </div>
          </div>

          {/* Advanced Options */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h3 className="font-semibold mb-2 dark:text-white">Advanced Options</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-300">Data validation</span>
                <Badge variant="secondary">Enabled</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-300">Skill extraction</span>
                <Badge variant="secondary">Auto</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-300">Duplicate detection</span>
                <Badge variant="secondary">Enabled</Badge>
              </div>
            </div>
          </div>

          {/* Estimated Results */}
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-4 h-4 text-blue-600" />
              <span className="font-semibold text-blue-800 dark:text-blue-200">Estimated Results</span>
            </div>
            <div className="text-sm text-blue-700 dark:text-blue-300">
              <p>• Expected jobs: {config.search_terms?.length * config.max_jobs} (max)</p>
              <p>• Estimated time: {Math.ceil((config.search_terms?.length * config.max_jobs) / 10)} minutes</p>
              <p>• Source: MyCareersFuture.gov.sg</p>
            </div>
          </div>
        </div>
        
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-750 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleStart} 
            disabled={!searchTermsText.trim()}
            className="gap-2"
          >
            <Zap className="w-4 h-4" />
            Start Scraping
          </Button>
        </div>
      </div>
    </div>
  );
}

// Progress Monitor Component
function ProgressMonitor({ 
  session, 
  taskStatus,
  onCancel,
  onViewResults 
}: { 
  session: ScrapingSession;
  taskStatus?: TaskStatus;
  onCancel: () => void;
  onViewResults: () => void;
}) {
  const getStatusIcon = () => {
    switch (session.status) {
      case 'running':
        return <Loader2 className="w-5 h-5 animate-spin text-blue-600" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'cancelled':
        return <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (session.status) {
      case 'running': return 'text-blue-600';
      case 'completed': return 'text-green-600';
      case 'failed': return 'text-red-600';
      case 'cancelled': return 'text-gray-600 dark:text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const formatDuration = (start: Date, end?: Date) => {
    const endTime = end || new Date();
    const duration = Math.floor((endTime.getTime() - start.getTime()) / 1000);
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getStatusIcon()}
            <div>
              <CardTitle className="text-lg">
                {session.config.search_terms.join(', ')}
              </CardTitle>
              <CardDescription>
                {session.config.employment_type} • {session.config.location || 'Any location'}
              </CardDescription>
            </div>
          </div>
          <div className="text-right">
            <div className={`font-semibold ${getStatusColor()}`}>
              {session.status.charAt(0).toUpperCase() + session.status.slice(1)}
            </div>
            <div className="text-sm text-gray-500">
              {formatDuration(session.startTime, session.endTime)}
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Progress Bar */}
        {session.status === 'running' && (
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Progress</span>
              <span>{session.progress}%</span>
            </div>
            <Progress value={session.progress} className="h-2" />
            {taskStatus?.meta?.status && (
              <p className="text-xs text-gray-500 mt-1">{taskStatus.meta.status}</p>
            )}
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{session.jobsFound}</div>
            <div className="text-xs text-gray-500">Jobs Found</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {session.statistics ? Object.keys(session.statistics.companies).length : 0}
            </div>
            <div className="text-xs text-gray-500">Companies</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {session.statistics?.topSkills?.length || 0}
            </div>
            <div className="text-xs text-gray-500">Skills</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {session.config.max_jobs}
            </div>
            <div className="text-xs text-gray-500">Max/Term</div>
          </div>
        </div>

        {/* Error Message */}
        {session.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center gap-2 text-red-800 text-sm">
              <AlertCircle className="w-4 h-4" />
              <span className="font-semibold">Error:</span>
            </div>
            <p className="text-red-700 text-sm mt-1">{session.error}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-2">
          {session.status === 'running' && (
            <Button variant="outline" size="sm" onClick={onCancel} className="gap-2">
              <Square className="w-4 h-4" />
              Cancel
            </Button>
          )}
          {session.status === 'completed' && session.jobsFound > 0 && (
            <Button size="sm" onClick={onViewResults} className="gap-2">
              <Eye className="w-4 h-4" />
              View Results
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// Session History Component
function SessionHistory({ 
  sessions, 
  onViewSession,
  onRestartSession 
}: { 
  sessions: ScrapingSession[];
  onViewSession: (session: ScrapingSession) => void;
  onRestartSession: (config: ScrapingConfig) => void;
}) {
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSuccessRate = () => {
    if (sessions.length === 0) return 0;
    const completed = sessions.filter(s => s.status === 'completed').length;
    return Math.round((completed / sessions.length) * 100);
  };

  const getTotalJobs = () => {
    return sessions.reduce((total, session) => total + session.jobsFound, 0);
  };

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{sessions.length}</div>
            <div className="text-sm text-gray-500">Total Sessions</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{getTotalJobs()}</div>
            <div className="text-sm text-gray-500">Jobs Scraped</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">{getSuccessRate()}%</div>
            <div className="text-sm text-gray-500">Success Rate</div>
          </CardContent>
        </Card>
      </div>

      {/* Session List */}
      <div className="space-y-3">
        {sessions.length === 0 ? (
          <div className="text-center py-8">
            <Activity className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-600 dark:text-gray-300 mb-2">No scraping sessions yet</h3>
            <p className="text-gray-500 text-sm">
              Start your first scraping session to see the history here
            </p>
          </div>
        ) : (
          sessions.map((session) => (
            <Card key={session.id} className="hover:shadow-sm transition-shadow">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${
                      session.status === 'completed' ? 'bg-green-500' :
                      session.status === 'running' ? 'bg-blue-500' :
                      session.status === 'failed' ? 'bg-red-500' :
                      'bg-gray-400'
                    }`} />
                    <div>
                      <div className="font-semibold">
                        {session.config.search_terms.join(', ')}
                      </div>
                      <div className="text-sm text-gray-500">
                        {formatDate(session.startTime)} • {session.jobsFound} jobs
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Badge variant={
                      session.status === 'completed' ? 'default' :
                      session.status === 'running' ? 'secondary' :
                      session.status === 'failed' ? 'destructive' :
                      'outline'
                    }>
                      {session.status}
                    </Badge>
                    
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => onViewSession(session)}
                      className="gap-1"
                    >
                      <Eye className="w-3 h-3" />
                      View
                    </Button>
                    
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => onRestartSession(session.config)}
                      className="gap-1"
                    >
                      <RefreshCw className="w-3 h-3" />
                      Restart
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

// Results View Component
function ResultsView({ 
  session, 
  jobs,
  onClose 
}: { 
  session: ScrapingSession;
  jobs: Job[];
  onClose: () => void;
}) {
  const [selectedJobs, setSelectedJobs] = useState<string[]>([]);

  const handleSelectAll = () => {
    if (selectedJobs.length === jobs.length) {
      setSelectedJobs([]);
    } else {
      setSelectedJobs(jobs.map(job => job.id));
    }
  };

  const handleExportResults = () => {
    const exportData = {
      session: {
        id: session.id,
        config: session.config,
        statistics: session.statistics,
        startTime: session.startTime,
        endTime: session.endTime
      },
      jobs: jobs
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
      type: 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scraping_results_${session.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast.success('Results exported successfully');
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[1200px] h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold">Scraping Results</h2>
            <p className="text-sm text-gray-500 mt-1">
              {session.config.search_terms.join(', ')} • {jobs.length} jobs found
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={handleExportResults} className="gap-2">
              <Download className="w-4 h-4" />
              Export Results
            </Button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          <Tabs defaultValue="jobs" className="h-full flex flex-col">
            <TabsList className="mx-6 mt-4">
              <TabsTrigger value="jobs">Jobs ({jobs.length})</TabsTrigger>
              <TabsTrigger value="statistics">Statistics</TabsTrigger>
              <TabsTrigger value="insights">Insights</TabsTrigger>
            </TabsList>

            <TabsContent value="jobs" className="flex-1 overflow-hidden mt-4">
              <div className="h-full flex flex-col px-6">
                {/* Job List Controls */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={handleSelectAll}
                    >
                      {selectedJobs.length === jobs.length ? 'Deselect All' : 'Select All'}
                    </Button>
                    {selectedJobs.length > 0 && (
                      <span className="text-sm text-gray-600 dark:text-gray-300">
                        {selectedJobs.length} selected
                      </span>
                    )}
                  </div>
                </div>

                {/* Job List */}
                <div className="flex-1 overflow-y-auto space-y-3">
                  {jobs.map((job) => (
                    <Card key={job.id} className="hover:shadow-sm transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-start gap-4">
                          <input
                            type="checkbox"
                            checked={selectedJobs.includes(job.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedJobs(prev => [...prev, job.id]);
                              } else {
                                setSelectedJobs(prev => prev.filter(id => id !== job.id));
                              }
                            }}
                            className="mt-1"
                          />
                          
                          <div className="flex-1">
                            <h3 className="font-semibold mb-1">{job.title}</h3>
                            <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-300 mb-2">
                              <span className="flex items-center gap-1">
                                <Building2 className="w-3 h-3" />
                                {job.company}
                              </span>
                              {job.location && (
                                <span className="flex items-center gap-1">
                                  <MapPin className="w-3 h-3" />
                                  {job.location}
                                </span>
                              )}
                              {(job.salary_min || job.salary_max) && (
                                <span className="flex items-center gap-1">
                                  <DollarSign className="w-3 h-3" />
                                  {job.salary_min && job.salary_max 
                                    ? `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`
                                    : job.salary_min 
                                    ? `$${job.salary_min.toLocaleString()}+`
                                    : `Up to $${job.salary_max?.toLocaleString()}`
                                  }
                                </span>
                              )}
                            </div>
                            
                            {job.required_skills && job.required_skills.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {job.required_skills.slice(0, 5).map((skill, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs">
                                    {skill}
                                  </Badge>
                                ))}
                                {job.required_skills.length > 5 && (
                                  <Badge variant="outline" className="text-xs">
                                    +{job.required_skills.length - 5} more
                                  </Badge>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="statistics" className="flex-1 overflow-hidden mt-4">
              <div className="h-full overflow-y-auto px-6">
                {session.statistics && (
                  <div className="space-y-6">
                    {/* Company Distribution */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Building2 className="w-5 h-5" />
                          Top Companies
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {Object.entries(session.statistics.companies)
                            .slice(0, 10)
                            .map(([company, count]) => (
                              <div key={company} className="flex justify-between items-center">
                                <span className="text-sm">{company}</span>
                                <Badge variant="secondary">{count} jobs</Badge>
                              </div>
                            ))}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Top Skills */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Target className="w-5 h-5" />
                          Most Demanded Skills
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2">
                          {session.statistics.topSkills.slice(0, 20).map((skill, index) => (
                            <Badge key={index} variant="outline">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Salary Insights */}
                    {session.statistics.salaryRanges?.available && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2">
                            <DollarSign className="w-5 h-5" />
                            Salary Insights
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <div className="text-sm text-gray-600 dark:text-gray-300">Average Salary</div>
                              <div className="text-xl font-bold">
                                ${session.statistics.salaryRanges.average?.toLocaleString()}
                              </div>
                            </div>
                            <div>
                              <div className="text-sm text-gray-600 dark:text-gray-300">Median Salary</div>
                              <div className="text-xl font-bold">
                                ${session.statistics.salaryRanges.median?.toLocaleString()}
                              </div>
                            </div>
                            <div>
                              <div className="text-sm text-gray-600 dark:text-gray-300">Salary Range</div>
                              <div className="text-lg font-semibold">
                                ${session.statistics.salaryRanges.min?.toLocaleString()} - 
                                ${session.statistics.salaryRanges.max?.toLocaleString()}
                              </div>
                            </div>
                            <div>
                              <div className="text-sm text-gray-600 dark:text-gray-300">Jobs with Salary</div>
                              <div className="text-lg font-semibold">
                                {session.statistics.salaryRanges.count} / {jobs.length}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="insights" className="flex-1 overflow-hidden mt-4">
              <div className="h-full overflow-y-auto px-6">
                <div className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="w-5 h-5" />
                        Market Insights
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                        <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">Job Market Activity</h4>
                        <p className="text-blue-700 dark:text-blue-300 text-sm">
                          Found {jobs.length} active positions for "{session.config.search_terms.join(', ')}" 
                          in the current market, indicating {jobs.length > 50 ? 'high' : jobs.length > 20 ? 'moderate' : 'low'} demand.
                        </p>
                      </div>
                      
                      <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                        <h4 className="font-semibold text-green-800 dark:text-green-200 mb-2">Skill Trends</h4>
                        <p className="text-green-700 dark:text-green-300 text-sm">
                          The most in-demand skills include {session.statistics?.topSkills.slice(0, 3).join(', ')}, 
                          suggesting these are key areas for career development.
                        </p>
                      </div>
                      
                      <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                        <h4 className="font-semibold text-purple-800 dark:text-purple-200 mb-2">Company Diversity</h4>
                        <p className="text-purple-700 dark:text-purple-300 text-sm">
                          Jobs are distributed across {Object.keys(session.statistics?.companies || {}).length} different companies, 
                          showing a {Object.keys(session.statistics?.companies || {}).length > 20 ? 'diverse' : 'concentrated'} job market.
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}

// Main Job Scraping Interface Component
export function JobScrapingInterface({ onJobsScraped, onClose }: JobScrapingInterfaceProps) {
  const [activeTab, setActiveTab] = useState<'configure' | 'monitor' | 'history'>('configure');
  const [sessions, setSessions] = useState<ScrapingSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ScrapingSession | null>(null);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showResultsModal, setShowResultsModal] = useState<ScrapingSession | null>(null);
  
  // API hooks
  const scrapeMutation = useScrapeJobs();
  const { data: taskStatus } = useTaskStatus(
    currentSession?.taskId || '', 
    !!currentSession && currentSession.status === 'running'
  );
  const { data: scrapedJobs } = useJobs({
    source: 'scraped',
    limit: 1000
  });

  // Polling for task updates
  useEffect(() => {
    if (currentSession && taskStatus) {
      const updatedSession = { ...currentSession };
      
      if (taskStatus.status === 'SUCCESS') {
        updatedSession.status = 'completed';
        updatedSession.progress = 100;
        updatedSession.endTime = new Date();
        
        if (taskStatus.result) {
          updatedSession.jobsFound = taskStatus.result.jobs_saved || 0;
          updatedSession.jobIds = taskStatus.result.job_ids || [];
          updatedSession.statistics = taskStatus.result.statistics;
        }
        
        setCurrentSession(null);
        toast.success(`Scraping completed! Found ${updatedSession.jobsFound} jobs`);
        
        if (onJobsScraped && updatedSession.jobIds.length > 0) {
          onJobsScraped(updatedSession.jobIds);
        }
      } else if (taskStatus.status === 'FAILURE') {
        updatedSession.status = 'failed';
        updatedSession.error = taskStatus.traceback || 'Scraping failed';
        updatedSession.endTime = new Date();
        setCurrentSession(null);
        toast.error('Scraping failed');
      } else if (taskStatus.status === 'PROGRESS' && taskStatus.meta) {
        updatedSession.progress = Math.round((taskStatus.meta.current / taskStatus.meta.total) * 100);
      }
      
      // Update session in list
      setSessions(prev => prev.map(s => s.id === updatedSession.id ? updatedSession : s));
      
      if (currentSession) {
        setCurrentSession(updatedSession);
      }
    }
  }, [taskStatus, currentSession, onJobsScraped]);

  const handleStartScraping = (config: ScrapingConfig) => {
    scrapeMutation.mutate(config, {
      onSuccess: (response) => {
        const newSession: ScrapingSession = {
          id: `session_${Date.now()}`,
          taskId: response.task_id,
          config,
          status: 'running',
          progress: 0,
          startTime: new Date(),
          jobsFound: 0,
          jobIds: []
        };
        
        setSessions(prev => [newSession, ...prev]);
        setCurrentSession(newSession);
        setActiveTab('monitor');
        
        toast.success('Scraping started successfully');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to start scraping');
      }
    });
  };

  const handleCancelScraping = () => {
    if (currentSession) {
      // In a real implementation, you'd call the cancel API
      const cancelledSession = {
        ...currentSession,
        status: 'cancelled' as const,
        endTime: new Date()
      };
      
      setSessions(prev => prev.map(s => s.id === cancelledSession.id ? cancelledSession : s));
      setCurrentSession(null);
      toast.info('Scraping cancelled');
    }
  };

  const handleViewResults = (session: ScrapingSession) => {
    setShowResultsModal(session);
  };

  const handleViewSession = (session: ScrapingSession) => {
    if (session.status === 'completed' && session.jobsFound > 0) {
      setShowResultsModal(session);
    }
  };

  const handleRestartSession = (config: ScrapingConfig) => {
    setShowConfigModal(true);
    // Pre-fill the config in the modal
  };

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
      <div className="max-w-[1200px] mx-auto p-4 sm:p-6 lg:p-8 xl:p-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-semibold mb-3 dark:text-white flex items-center gap-3">
              <Zap className="w-8 h-8 text-purple-600" />
              Job Scraping Interface
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Discover and collect job opportunities automatically from multiple sources
            </p>
          </div>
          {onClose && (
            <Button variant="outline" onClick={onClose}>
              <X className="w-4 h-4 mr-2" />
              Close
            </Button>
          )}
        </div>

        {/* Quick Start Button */}
        {!currentSession && sessions.length === 0 && (
          <div className="text-center mb-8">
            <Button 
              size="lg" 
              onClick={() => setShowConfigModal(true)}
              className="gap-2"
            >
              <Play className="w-5 h-5" />
              Start New Scraping Session
            </Button>
          </div>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="configure" className="gap-2">
              <Settings className="w-4 h-4" />
              Configure
            </TabsTrigger>
            <TabsTrigger value="monitor" className="gap-2">
              <Activity className="w-4 h-4" />
              Monitor
              {currentSession && (
                <Badge variant="secondary" className="ml-1">
                  Active
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="history" className="gap-2">
              <Clock className="w-4 h-4" />
              History
              {sessions.length > 0 && (
                <Badge variant="outline" className="ml-1">
                  {sessions.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="configure" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Quick Start</CardTitle>
                <CardDescription>
                  Configure and launch a new job scraping session
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => setShowConfigModal(true)} className="gap-2">
                  <Settings className="w-4 h-4" />
                  Configure New Session
                </Button>
              </CardContent>
            </Card>

            {/* Recent Configurations */}
            {sessions.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Recent Configurations</CardTitle>
                  <CardDescription>
                    Quickly restart previous scraping configurations
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {sessions.slice(0, 3).map((session) => (
                      <div key={session.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">
                            {session.config.search_terms.join(', ')}
                          </div>
                          <div className="text-sm text-gray-500">
                            {session.config.employment_type} • Max {session.config.max_jobs} jobs
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleRestartSession(session.config)}
                          className="gap-2"
                        >
                          <RefreshCw className="w-3 h-3" />
                          Restart
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="monitor" className="space-y-6">
            {currentSession ? (
              <ProgressMonitor
                session={currentSession}
                taskStatus={taskStatus}
                onCancel={handleCancelScraping}
                onViewResults={() => handleViewResults(currentSession)}
              />
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="font-semibold text-gray-600 dark:text-gray-300 mb-2">No Active Sessions</h3>
                  <p className="text-gray-500 text-sm mb-4">
                    Start a new scraping session to monitor progress here
                  </p>
                  <Button onClick={() => setShowConfigModal(true)} className="gap-2">
                    <Play className="w-4 h-4" />
                    Start Scraping
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            <SessionHistory
              sessions={sessions}
              onViewSession={handleViewSession}
              onRestartSession={handleRestartSession}
            />
          </TabsContent>
        </Tabs>
      </div>

      {/* Modals */}
      {showConfigModal && (
        <ScrapingConfigModal
          onClose={() => setShowConfigModal(false)}
          onStart={handleStartScraping}
        />
      )}

      {showResultsModal && (
        <ResultsView
          session={showResultsModal}
          jobs={scrapedJobs?.filter(job => 
            showResultsModal.jobIds.includes(job.id)
          ) || []}
          onClose={() => setShowResultsModal(null)}
        />
      )}
    </div>
  );
}