import { useState, useMemo } from 'react';
import { 
  Play, 
  FileText, 
  FolderOpen, 
  CheckCircle, 
  Loader2,
  ArrowRight,
  Briefcase,
  Search
} from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Input } from '@/app/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { 
  useResumes, 
  useJobGroups,
  useJobs,
  useAnalyzeResume
} from '@/hooks/useApi';

interface AnalysisLauncherSimpleProps {
  onAnalysisStarted?: (analysisId: string) => void;
}

export function AnalysisLauncherSimple({ onAnalysisStarted }: AnalysisLauncherSimpleProps) {
  const [selectedResumeId, setSelectedResumeId] = useState<string | null>(null);
  const [selectedGroupIds, setSelectedGroupIds] = useState<string[]>([]);
  const [selectedJobIds, setSelectedJobIds] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<'groups' | 'single'>('groups');
  const [resumeSearchQuery, setResumeSearchQuery] = useState('');
  const [groupSearchQuery, setGroupSearchQuery] = useState('');
  const [jobSearchQuery, setJobSearchQuery] = useState('');

  const { data: resumes, isLoading: resumesLoading } = useResumes();
  const { data: groups, isLoading: groupsLoading } = useJobGroups();
  const { data: jobs, isLoading: jobsLoading } = useJobs();
  const analyzeResumeMutation = useAnalyzeResume();

  // Filter resumes based on search query
  const filteredResumes = useMemo(() => {
    if (!resumes) return [];
    if (!resumeSearchQuery.trim()) return resumes;

    const query = resumeSearchQuery.toLowerCase();
    return resumes.filter(resume => 
      resume.filename.toLowerCase().includes(query) ||
      resume.extracted_skills?.some(skill => skill.toLowerCase().includes(query))
    );
  }, [resumes, resumeSearchQuery]);

  // Filter groups based on search query
  const filteredGroups = useMemo(() => {
    if (!groups) return [];
    if (!groupSearchQuery.trim()) return groups;

    const query = groupSearchQuery.toLowerCase();
    return groups.filter(group => 
      group.name.toLowerCase().includes(query) ||
      group.description?.toLowerCase().includes(query)
    );
  }, [groups, groupSearchQuery]);

  // Filter jobs based on search query
  const filteredJobs = useMemo(() => {
    if (!jobs) return [];
    if (!jobSearchQuery.trim()) return jobs;

    const query = jobSearchQuery.toLowerCase();
    return jobs.filter(job => 
      job.title.toLowerCase().includes(query) ||
      job.company.toLowerCase().includes(query) ||
      job.location?.toLowerCase().includes(query) ||
      job.required_skills?.some(skill => skill.toLowerCase().includes(query))
    );
  }, [jobs, jobSearchQuery]);

  const handleGroupToggle = (groupId: string) => {
    if (selectedGroupIds.includes(groupId)) {
      setSelectedGroupIds(selectedGroupIds.filter(id => id !== groupId));
    } else {
      setSelectedGroupIds([...selectedGroupIds, groupId]);
    }
  };

  const handleJobToggle = (jobId: string) => {
    if (selectedJobIds.includes(jobId)) {
      setSelectedJobIds(selectedJobIds.filter(id => id !== jobId));
    } else {
      setSelectedJobIds([...selectedJobIds, jobId]);
    }
  };

  const handleStartAnalysis = () => {
    if (!selectedResumeId) {
      toast.error('Please select a resume');
      return;
    }

    let jobIds: string[] = [];

    if (activeTab === 'groups') {
      if (selectedGroupIds.length === 0) {
        toast.error('Please select at least one job group');
        return;
      }

      // Get all job IDs from selected groups
      jobIds = groups
        ?.filter(g => selectedGroupIds.includes(g.id))
        .flatMap(g => g.job_ids) || [];

      if (jobIds.length === 0) {
        toast.error('Selected groups have no jobs');
        return;
      }
    } else {
      if (selectedJobIds.length === 0) {
        toast.error('Please select at least one job');
        return;
      }
      jobIds = selectedJobIds;
    }

    analyzeResumeMutation.mutate(
      { 
        resumeId: selectedResumeId, 
        jobIds,
        analysisType: 'comprehensive'
      },
      {
        onSuccess: (response) => {
          toast.success(`Analysis started! Analyzing against ${jobIds.length} jobs`);
          onAnalysisStarted?.(response.analysis_id);
        },
        onError: (error: any) => {
          toast.error(error.response?.data?.detail || 'Failed to start analysis');
        },
      }
    );
  };

  const selectedJobCount = activeTab === 'groups'
    ? groups
        ?.filter(g => selectedGroupIds.includes(g.id))
        .reduce((sum, g) => sum + (g.job_ids?.length || 0), 0) || 0
    : selectedJobIds.length;

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header with Action Button */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h1 className="text-2xl font-semibold">Career Analysis</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Select a resume and jobs to analyze your career fit
              </p>
            </div>
            
            {/* Start Analysis Button */}
            <Button
              size="lg"
              onClick={handleStartAnalysis}
              disabled={
                !selectedResumeId || 
                (activeTab === 'groups' ? selectedGroupIds.length === 0 : selectedJobIds.length === 0) || 
                analyzeResumeMutation.isPending
              }
              className="gap-2"
            >
              {analyzeResumeMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Start Analysis
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </Button>
          </div>
          
          {/* Status Text */}
          {selectedResumeId && selectedJobCount > 0 && (
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Ready to analyze <span className="font-medium text-blue-600">{selectedJobCount} job{selectedJobCount > 1 ? 's' : ''}</span>
              {activeTab === 'groups' && selectedGroupIds.length > 0 && (
                <> from <span className="font-medium text-blue-600">{selectedGroupIds.length} group{selectedGroupIds.length > 1 ? 's' : ''}</span></>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Resume Selection */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="bg-gray-50 dark:bg-gray-900 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold">Select Resume</h2>
            </div>
          </div>

          <div className="p-4">
            {/* Search Bar */}
            <div className="relative mb-3">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search resumes..."
                value={resumeSearchQuery}
                onChange={(e) => setResumeSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {resumesLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
              </div>
            ) : !resumes || resumes.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600 dark:text-gray-300">No resumes available</p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Upload a resume first
                </p>
              </div>
            ) : filteredResumes.length === 0 ? (
              <div className="text-center py-12">
                <Search className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600 dark:text-gray-300">No resumes match your search</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-[calc(100vh-450px)] overflow-y-auto pr-2">
                {filteredResumes.map((resume) => (
                  <div
                    key={resume.id}
                    className={`p-3 border-2 rounded-lg cursor-pointer transition-all ${
                      selectedResumeId === resume.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700'
                    }`}
                    onClick={() => setSelectedResumeId(resume.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="font-medium truncate text-sm">{resume.filename}</p>
                          {selectedResumeId === resume.id && (
                            <CheckCircle className="w-4 h-4 text-blue-600 flex-shrink-0" />
                          )}
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {new Date(resume.upload_date).toLocaleDateString()}
                        </p>
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
                            +{resume.extracted_skills.length - 3}
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Job Selection with Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'groups' | 'single')}>
            <div className="bg-gray-50 dark:bg-gray-900 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
              <TabsList className="w-full grid grid-cols-2">
                <TabsTrigger value="groups" className="gap-2">
                  <FolderOpen className="w-4 h-4" />
                  Job Groups
                  {selectedGroupIds.length > 0 && (
                    <Badge variant="secondary" className="ml-1">{selectedGroupIds.length}</Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger value="single" className="gap-2">
                  <Briefcase className="w-4 h-4" />
                  Single Jobs
                  {selectedJobIds.length > 0 && (
                    <Badge variant="secondary" className="ml-1">{selectedJobIds.length}</Badge>
                  )}
                </TabsTrigger>
              </TabsList>
            </div>

            <div className="p-4">
              {/* Job Groups Tab */}
              <TabsContent value="groups" className="mt-0">
                {/* Search Bar */}
                <div className="relative mb-3">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Search groups..."
                    value={groupSearchQuery}
                    onChange={(e) => setGroupSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>

                {groupsLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
                  </div>
                ) : !groups || groups.length === 0 ? (
                  <div className="text-center py-12">
                    <FolderOpen className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-600 dark:text-gray-300">No job groups available</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      Create job groups first
                    </p>
                  </div>
                ) : filteredGroups.length === 0 ? (
                  <div className="text-center py-12">
                    <Search className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-600 dark:text-gray-300">No groups match your search</p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-[calc(100vh-450px)] overflow-y-auto pr-2">
                    {filteredGroups.map((group) => (
                      <div
                        key={group.id}
                        className={`p-3 border-2 rounded-lg cursor-pointer transition-all ${
                          selectedGroupIds.includes(group.id)
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700'
                        }`}
                        onClick={() => handleGroupToggle(group.id)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <p className="font-medium truncate text-sm">{group.name}</p>
                              {selectedGroupIds.includes(group.id) && (
                                <CheckCircle className="w-4 h-4 text-blue-600 flex-shrink-0" />
                              )}
                            </div>
                            {group.description && (
                              <p className="text-xs text-gray-500 dark:text-gray-400 mb-2 line-clamp-1">
                                {group.description}
                              </p>
                            )}
                            <div className="flex items-center gap-2">
                              <Badge 
                                variant={group.group_type === 'scraped' ? 'secondary' : 'outline'}
                                className="text-xs"
                              >
                                {group.group_type === 'scraped' ? 'Scraped' : 'Custom'}
                              </Badge>
                              <Badge variant="outline" className="text-xs">
                                {group.job_ids?.length || 0} jobs
                              </Badge>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Single Jobs Tab */}
              <TabsContent value="single" className="mt-0">
                {/* Search Bar */}
                <div className="relative mb-3">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Search jobs..."
                    value={jobSearchQuery}
                    onChange={(e) => setJobSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>

                {jobsLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
                  </div>
                ) : !jobs || jobs.length === 0 ? (
                  <div className="text-center py-12">
                    <Briefcase className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-600 dark:text-gray-300">No jobs available</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      Scrape or add jobs first
                    </p>
                  </div>
                ) : filteredJobs.length === 0 ? (
                  <div className="text-center py-12">
                    <Search className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-600 dark:text-gray-300">No jobs match your search</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      Try different keywords
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-[calc(100vh-450px)] overflow-y-auto pr-2">
                    {filteredJobs.map((job) => (
                      <div
                        key={job.id}
                        className={`p-3 border-2 rounded-lg cursor-pointer transition-all ${
                          selectedJobIds.includes(job.id)
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700'
                        }`}
                        onClick={() => handleJobToggle(job.id)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <p className="font-medium truncate text-sm">{job.title}</p>
                              {selectedJobIds.includes(job.id) && (
                                <CheckCircle className="w-4 h-4 text-blue-600 flex-shrink-0" />
                              )}
                            </div>
                            <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                              {job.company}
                            </p>
                            {job.location && (
                              <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                                {job.location}
                              </p>
                            )}
                            <div className="flex items-center gap-2">
                              {job.source && (
                                <Badge variant="outline" className="text-xs">
                                  {job.source}
                                </Badge>
                              )}
                              {job.required_skills && job.required_skills.length > 0 && (
                                <Badge variant="outline" className="text-xs">
                                  {job.required_skills.length} skills
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </div>
        </div>
      </div>
    </div>
  );
}
