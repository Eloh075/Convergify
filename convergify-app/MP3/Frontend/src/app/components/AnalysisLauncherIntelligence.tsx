import { useState, useMemo } from 'react';
import { 
  FileText, 
  FolderOpen, 
  CheckCircle, 
  Loader2,
  ArrowRight,
  Briefcase,
  Search,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Input } from '@/app/components/ui/input';
import { 
  useResumes, 
  useJobGroups,
  useJobs,
  useCreateAnalysis
} from '@/hooks/useApi';

interface AnalysisLauncherIntelligenceProps {
  onAnalysisStarted?: (analysisId: string) => void;
}

export function AnalysisLauncherIntelligence({ onAnalysisStarted }: AnalysisLauncherIntelligenceProps) {
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
  const createAnalysisMutation = useCreateAnalysis();

  // Filter resumes
  const filteredResumes = useMemo(() => {
    if (!resumes) return [];
    if (!resumeSearchQuery.trim()) return resumes;
    const query = resumeSearchQuery.toLowerCase();
    return resumes.filter(resume => 
      resume.filename.toLowerCase().includes(query) ||
      resume.extracted_skills?.some(skill => skill.toLowerCase().includes(query))
    );
  }, [resumes, resumeSearchQuery]);

  // Filter groups
  const filteredGroups = useMemo(() => {
    if (!groups) return [];
    if (!groupSearchQuery.trim()) return groups;
    const query = groupSearchQuery.toLowerCase();
    return groups.filter(group => 
      group.name.toLowerCase().includes(query) ||
      group.description?.toLowerCase().includes(query)
    );
  }, [groups, groupSearchQuery]);

  // Filter jobs
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
    setSelectedGroupIds(prev => 
      prev.includes(groupId) ? prev.filter(id => id !== groupId) : [...prev, groupId]
    );
  };

  const handleJobToggle = (jobId: string) => {
    setSelectedJobIds(prev => 
      prev.includes(jobId) ? prev.filter(id => id !== jobId) : [...prev, jobId]
    );
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
      jobIds = groups?.filter(g => selectedGroupIds.includes(g.id)).flatMap(g => g.job_ids) || [];
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

    createAnalysisMutation.mutate(
      { 
        resume_id: selectedResumeId, 
        job_ids: jobIds, 
        analysis_type: 'comprehensive' 
      },
      {
        onSuccess: (response) => {
          toast.success(`✨ Analysis initiated for ${jobIds.length} positions`);
          onAnalysisStarted?.(response.id);
        },
        onError: (error: any) => {
          const errorDetail = error.response?.data?.detail;
          const errorMessage = typeof errorDetail === 'string' 
            ? errorDetail 
            : 'Analysis failed to initialize';
          toast.error(errorMessage);
        },
      }
    );
  };

  const selectedJobCount = activeTab === 'groups'
    ? groups?.filter(g => selectedGroupIds.includes(g.id)).reduce((sum, g) => sum + (g.job_ids?.length || 0), 0) || 0
    : selectedJobIds.length;

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
      {/* Intelligence Console Header */}
      <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-800/50 px-6 py-5 shadow-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  Analysis Lab
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Strategic Career Intelligence Platform
                </p>
              </div>
            </div>
            
            {/* Status & Action */}
            <div className="flex items-center gap-4">
              {selectedResumeId && selectedJobCount > 0 && (
                <div className="flex items-center gap-2 px-4 py-2 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-emerald-700 dark:text-emerald-300">
                    System Ready
                  </span>
                </div>
              )}
              
              <Button
                size="lg"
                onClick={handleStartAnalysis}
                disabled={!selectedResumeId || selectedJobCount === 0 || createAnalysisMutation.isPending}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 gap-2"
              >
                {createAnalysisMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Initializing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Analysis
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Mission Control - Two Pillars */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* LEFT PILLAR: The Candidate */}
            <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-2xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-5">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                    <FileText className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">The Candidate</h2>
                    <p className="text-sm text-blue-100">Your resume profile</p>
                  </div>
                </div>
              </div>

              <div className="px-6 pt-6 pb-0">
                <div className="relative mb-4">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Search resumes..."
                    value={resumeSearchQuery}
                    onChange={(e) => setResumeSearchQuery(e.target.value)}
                    className="pl-12 h-12 bg-gray-50 dark:bg-gray-900/50 border-gray-200 dark:border-gray-700 rounded-xl"
                  />
                </div>

                {resumesLoading ? (
                  <div className="flex flex-col items-center justify-center py-20">
                    <Loader2 className="w-10 h-10 animate-spin text-blue-600 mb-4" />
                    <p className="text-sm text-gray-500 font-medium">Loading profiles...</p>
                  </div>
                ) : filteredResumes.length === 0 ? (
                  <div className="text-center py-20">
                    <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <FileText className="w-10 h-10 text-blue-600" />
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 font-semibold mb-2">
                      {resumeSearchQuery ? 'No matches found' : 'No resumes available'}
                    </p>
                    <p className="text-sm text-gray-500">
                      {resumeSearchQuery ? 'Try different keywords' : 'Upload your first resume to begin'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-[calc(100vh-350px)] overflow-y-auto pr-2 custom-scrollbar">
                    {filteredResumes.map((resume) => (
                      <div
                        key={resume.id}
                        className={`group relative p-5 rounded-xl cursor-pointer transition-all duration-300 border-2 ${
                          selectedResumeId === resume.id
                            ? 'bg-gradient-to-br from-blue-100 via-blue-50 to-indigo-50 dark:from-blue-900/60 dark:via-blue-800/50 dark:to-indigo-900/60 border-blue-500 shadow-lg scale-[1.02]'
                            : 'bg-white dark:bg-gray-900/30 border-gray-400 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 hover:shadow-md hover:scale-[1.01]'
                        }`}
                        onClick={() => setSelectedResumeId(resume.id)}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <p className="font-bold text-gray-900 dark:text-white">
                                {resume.filename}
                              </p>
                              {selectedResumeId === resume.id && (
                                <CheckCircle className="w-5 h-5 text-blue-600 animate-in fade-in duration-200" />
                              )}
                            </div>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {new Date(resume.upload_date).toLocaleDateString('en-US', { 
                                month: 'long', 
                                day: 'numeric', 
                                year: 'numeric' 
                              })}
                            </p>
                          </div>
                        </div>
                        
                        {resume.extracted_skills && resume.extracted_skills.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {resume.extracted_skills.slice(0, 3).map((skill, index) => (
                              <span 
                                key={index}
                                className="px-3 py-1 text-xs font-semibold bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm"
                              >
                                {skill}
                              </span>
                            ))}
                            {resume.extracted_skills.length > 3 && (
                              <span className="px-3 py-1 text-xs font-semibold bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-900/40 dark:to-indigo-900/40 text-blue-700 dark:text-blue-300 rounded-lg">
                                +{resume.extracted_skills.length - 3} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* RIGHT PILLAR: The Target */}
            <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-2xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 overflow-hidden">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                      <Briefcase className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-white">The Target</h2>
                      <p className="text-sm text-indigo-100">Market scope definition</p>
                    </div>
                  </div>

                  {/* Compact Toggle with Hover Animation - On Right */}
                  <div className="flex items-center gap-1 bg-white/20 backdrop-blur-sm rounded-lg p-1">
                    <button
                      onClick={() => setActiveTab('groups')}
                      className={`group relative flex items-center gap-1.5 px-2.5 py-2 rounded-md transition-all duration-200 ${
                        activeTab === 'groups'
                          ? 'bg-white text-indigo-600 shadow-md'
                          : 'text-white/70 hover:text-white hover:bg-white/10'
                      }`}
                    >
                      <FolderOpen className="w-4 h-4 flex-shrink-0" />
                      <span className="text-xs font-semibold whitespace-nowrap overflow-hidden transition-all duration-300 max-w-0 opacity-0 group-hover:max-w-[80px] group-hover:opacity-100">
                        Library
                      </span>
                      {selectedGroupIds.length > 0 && activeTab === 'groups' && (
                        <Badge className="ml-0.5 bg-indigo-100 text-indigo-700 text-xs px-1.5 py-0">
                          {selectedGroupIds.length}
                        </Badge>
                      )}
                    </button>
                    <button
                      onClick={() => setActiveTab('single')}
                      className={`group relative flex items-center gap-1.5 px-2.5 py-2 rounded-md transition-all duration-200 ${
                        activeTab === 'single'
                          ? 'bg-white text-purple-600 shadow-md'
                          : 'text-white/70 hover:text-white hover:bg-white/10'
                      }`}
                    >
                      <Briefcase className="w-4 h-4 flex-shrink-0" />
                      <span className="text-xs font-semibold whitespace-nowrap overflow-hidden transition-all duration-300 max-w-0 opacity-0 group-hover:max-w-[80px] group-hover:opacity-100">
                        Manual
                      </span>
                      {selectedJobIds.length > 0 && activeTab === 'single' && (
                        <Badge className="ml-0.5 bg-purple-100 text-purple-700 text-xs px-1.5 py-0">
                          {selectedJobIds.length}
                        </Badge>
                      )}
                    </button>
                  </div>
                </div>
              </div>

              <div className="px-6 pt-6 pb-0">
                {/* Job Groups Content */}
                {activeTab === 'groups' && (
                  <>
                    <div className="relative mb-4">
                      <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <Input
                        type="text"
                        placeholder="Search groups..."
                        value={groupSearchQuery}
                        onChange={(e) => setGroupSearchQuery(e.target.value)}
                        className="pl-12 h-12 bg-gray-50 dark:bg-gray-900/50 border-gray-200 dark:border-gray-700 rounded-xl"
                      />
                    </div>

                    {groupsLoading ? (
                      <div className="flex flex-col items-center justify-center py-20">
                        <Loader2 className="w-10 h-10 animate-spin text-indigo-600 mb-4" />
                        <p className="text-sm text-gray-500 font-medium">Loading groups...</p>
                      </div>
                    ) : filteredGroups.length === 0 ? (
                      <div className="text-center py-20">
                        <div className="w-20 h-20 bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                          <FolderOpen className="w-10 h-10 text-indigo-600" />
                        </div>
                        <p className="text-gray-700 dark:text-gray-300 font-semibold mb-2">
                          {groupSearchQuery ? 'No matches found' : 'No job groups'}
                        </p>
                        <p className="text-sm text-gray-500">
                          {groupSearchQuery ? 'Try different keywords' : 'Create groups in Job Hub'}
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-3 max-h-[calc(100vh-400px)] overflow-y-auto pr-2 custom-scrollbar">
                        {filteredGroups.map((group) => (
                          <div
                            key={group.id}
                            className={`p-5 rounded-xl cursor-pointer transition-all duration-300 border-2 ${
                              selectedGroupIds.includes(group.id)
                                ? 'bg-gradient-to-br from-indigo-100 via-indigo-50 to-purple-50 dark:from-indigo-900/60 dark:via-indigo-800/50 dark:to-purple-900/60 border-indigo-500 shadow-lg scale-[1.02]'
                                : 'bg-white dark:bg-gray-900/30 border-gray-400 dark:border-gray-700 hover:border-indigo-400 dark:hover:border-indigo-600 hover:shadow-md hover:scale-[1.01]'
                            }`}
                            onClick={() => handleGroupToggle(group.id)}
                          >
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <p className="font-bold text-gray-900 dark:text-white">
                                    {group.name}
                                  </p>
                                  {selectedGroupIds.includes(group.id) && (
                                    <CheckCircle className="w-5 h-5 text-indigo-600 dark:text-indigo-400 animate-in fade-in duration-200" />
                                  )}
                                </div>
                                {group.description && (
                                  <p className="text-xs text-gray-700 dark:text-gray-300 line-clamp-1 mb-2">
                                    {group.description}
                                  </p>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge 
                                variant={group.group_type === 'scraped' ? 'secondary' : 'outline'}
                                className="text-xs font-semibold"
                              >
                                {group.group_type === 'scraped' ? 'Scraped' : 'Custom'}
                              </Badge>
                              <Badge variant="outline" className="text-xs font-semibold">
                                {group.job_ids?.length || 0} positions
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}

                {/* Single Jobs Content */}
                {activeTab === 'single' && (
                  <>
                    <div className="relative mb-4">
                      <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <Input
                        type="text"
                        placeholder="Search jobs..."
                        value={jobSearchQuery}
                        onChange={(e) => setJobSearchQuery(e.target.value)}
                        className="pl-12 h-12 bg-gray-50 dark:bg-gray-900/50 border-gray-200 dark:border-gray-700 rounded-xl"
                      />
                    </div>

                    {jobsLoading ? (
                      <div className="flex flex-col items-center justify-center py-20">
                        <Loader2 className="w-10 h-10 animate-spin text-purple-600 mb-4" />
                        <p className="text-sm text-gray-500 font-medium">Loading positions...</p>
                      </div>
                    ) : filteredJobs.length === 0 ? (
                      <div className="text-center py-20">
                        <div className="w-20 h-20 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/20 dark:to-pink-900/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                          <Briefcase className="w-10 h-10 text-purple-600" />
                        </div>
                        <p className="text-gray-700 dark:text-gray-300 font-semibold mb-2">
                          {jobSearchQuery ? 'No matches found' : 'No jobs available'}
                        </p>
                        <p className="text-sm text-gray-500">
                          {jobSearchQuery ? 'Try different keywords' : 'Scrape or add jobs first'}
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-3 max-h-[calc(100vh-400px)] overflow-y-auto pr-2 custom-scrollbar">
                        {filteredJobs.map((job) => (
                          <div
                            key={job.id}
                            className={`p-5 rounded-xl cursor-pointer transition-all duration-300 border-2 ${
                              selectedJobIds.includes(job.id)
                                ? 'bg-gradient-to-br from-purple-100 via-purple-50 to-pink-50 dark:from-purple-900/60 dark:via-purple-800/50 dark:to-pink-900/60 border-purple-500 shadow-lg scale-[1.02]'
                                : 'bg-white dark:bg-gray-900/30 border-gray-400 dark:border-gray-700 hover:border-purple-400 dark:hover:border-purple-600 hover:shadow-md hover:scale-[1.01]'
                            }`}
                            onClick={() => handleJobToggle(job.id)}
                          >
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <p className="font-bold text-gray-900 dark:text-white text-sm">
                                    {job.title}
                                  </p>
                                  {selectedJobIds.includes(job.id) && (
                                    <CheckCircle className="w-5 h-5 text-purple-600 dark:text-purple-400 animate-in fade-in duration-200" />
                                  )}
                                </div>
                                <p className="text-xs text-gray-700 dark:text-gray-300 mb-1">
                                  {job.company}
                                </p>
                                {job.location && (
                                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                                    {job.location}
                                  </p>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              {job.source && (
                                <Badge variant="outline" className="text-xs font-semibold">
                                  {job.source}
                                </Badge>
                              )}
                              {job.required_skills && job.required_skills.length > 0 && (
                                <Badge variant="outline" className="text-xs font-semibold">
                                  {job.required_skills.length} skills
                                </Badge>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom Scrollbar Styles */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(148, 163, 184, 0.3);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(148, 163, 184, 0.5);
        }
      `}</style>
    </div>
  );
}
