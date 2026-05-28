/**
 * React Query hooks for API calls
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiClient, API_ENDPOINTS, uploadFile } from '@/lib/api';
import type {
  Resume,
  Job,
  JobGroup,
  Analysis,
  ResumeUploadRequest,
  JobCreateRequest,
  JobGroupCreateRequest,
  AnalysisCreateRequest,
  ScrapingConfig,
  ResumeFilters,
  JobFilters,
  AnalysisFilters,
  TaskStatus,
  AnalysisStatus,
  ResumeComparison,
  SessionDetails,
  SessionStats,
  SessionCreateRequest,
  SessionUpdateRequest,
  SessionFilters,
} from '@/types/api';

// Query keys
export const QUERY_KEYS = {
  RESUMES: 'resumes',
  RESUME: 'resume',
  RESUME_HISTORY: 'resume-history',
  RESUME_ANALYSES: 'resume-analyses',
  JOBS: 'jobs',
  JOB: 'job',
  JOB_GROUPS: 'job-groups',
  JOB_GROUP: 'job-group',
  ANALYSES: 'analyses',
  ANALYSIS: 'analysis',
  ANALYSIS_STATUS: 'analysis-status',
  ANALYSIS_RESULTS: 'analysis-results',
  TASK_STATUS: 'task-status',
  SESSIONS: 'sessions',
  SESSION: 'session',
} as const;

// Resume hooks
export const useResumes = (filters?: ResumeFilters) => {
  return useQuery({
    queryKey: [QUERY_KEYS.RESUMES, filters],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.RESUMES, { params: filters });
      return response.data as Resume[];
    },
  });
};

export const useResume = (id: string) => {
  return useQuery({
    queryKey: [QUERY_KEYS.RESUME, id],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.RESUME_BY_ID(id));
      return response.data as Resume;
    },
    enabled: !!id,
  });
};

export const useResumeHistory = (id: string) => {
  return useQuery({
    queryKey: [QUERY_KEYS.RESUME_HISTORY, id],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.RESUME_HISTORY(id));
      return response.data;
    },
    enabled: !!id,
  });
};

export const useUploadResume = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: ResumeUploadRequest) => {
      const response = await uploadFile(data.file, API_ENDPOINTS.RESUME_UPLOAD, {
        user_id: data.user_id || 'default-user',
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.RESUMES] });
      toast.success('Resume uploaded successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to upload resume');
    },
  });
};

export const useAnalyzeResume = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ resumeId, jobIds, analysisType }: {
      resumeId: string;
      jobIds?: string[];
      analysisType?: string;
    }) => {
      const response = await apiClient.post(API_ENDPOINTS.RESUME_ANALYZE(resumeId), {
        job_ids: jobIds,
        analysis_type: analysisType || 'comprehensive',
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.ANALYSES] });
      toast.success('Analysis started successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start analysis');
    },
  });
};

export const useOptimizeResume = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ resumeId, analysisId }: {
      resumeId: string;
      analysisId?: string;
    }) => {
      const response = await apiClient.post(API_ENDPOINTS.RESUME_OPTIMIZE(resumeId), {
        analysis_id: analysisId,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.RESUMES] });
      toast.success('Resume optimization started');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start optimization');
    },
  });
};

export const useResumeComparison = (resumeId: string, optimizedId: string) => {
  return useQuery({
    queryKey: ['resume-comparison', resumeId, optimizedId],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.RESUME_COMPARE(resumeId, optimizedId));
      return response.data as ResumeComparison;
    },
    enabled: !!resumeId && !!optimizedId,
  });
};

export const useDeleteResume = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (resumeId: string) => {
      const response = await apiClient.delete(API_ENDPOINTS.RESUME_DELETE(resumeId));
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.RESUMES] });
      toast.success('Resume deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete resume');
    },
  });
};

// Job hooks
export const useJobs = (filters?: JobFilters) => {
  return useQuery({
    queryKey: [QUERY_KEYS.JOBS, filters],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.JOBS, { params: filters });
      return response.data as Job[];
    },
  });
};

export const useJob = (id: string) => {
  return useQuery({
    queryKey: [QUERY_KEYS.JOB, id],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.JOB_BY_ID(id));
      return response.data as Job;
    },
    enabled: !!id,
  });
};

export const useJobGroups = () => {
  return useQuery({
    queryKey: [QUERY_KEYS.JOB_GROUPS],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.JOB_GROUPS);
      return response.data as JobGroup[];
    },
  });
};

export const useCreateJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: JobCreateRequest) => {
      const response = await apiClient.post(API_ENDPOINTS.JOBS, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.JOBS] });
      toast.success('Job created successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create job');
    },
  });
};

export const useCreateJobGroup = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: JobGroupCreateRequest) => {
      const response = await apiClient.post(API_ENDPOINTS.JOB_GROUPS, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.JOB_GROUPS] });
      toast.success('Job group created successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create job group');
    },
  });
};

export const useScrapeJobs = () => {
  return useMutation({
    mutationFn: async (config: ScrapingConfig) => {
      const response = await apiClient.post(API_ENDPOINTS.JOB_SCRAPE, config);
      return response.data;
    },
    onSuccess: () => {
      toast.success('Job scraping started successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start job scraping');
    },
  });
};

export const useDeleteJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (jobId: string) => {
      const response = await apiClient.delete(API_ENDPOINTS.JOB_DELETE(jobId));
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.JOBS] });
      toast.success('Job deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete job');
    },
  });
};

export const useDeleteJobGroup = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (groupId: string) => {
      const response = await apiClient.delete(API_ENDPOINTS.JOB_GROUP_DELETE(groupId));
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.JOB_GROUPS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.JOBS] });
      toast.success('Group deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete group');
    },
  });
};

// Analysis hooks
export const useAnalyses = (filters?: AnalysisFilters) => {
  return useQuery({
    queryKey: [QUERY_KEYS.ANALYSES, filters],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.ANALYSES, { params: filters });
      return response.data as Analysis[];
    },
  });
};

export const useAnalysis = (id: string) => {
  return useQuery({
    queryKey: [QUERY_KEYS.ANALYSIS, id],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.ANALYSIS_BY_ID(id));
      return response.data as Analysis;
    },
    enabled: !!id,
  });
};

export const useAnalysisStatus = (id: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [QUERY_KEYS.ANALYSIS_STATUS, id],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.ANALYSIS_STATUS(id));
      return response.data as AnalysisStatus;
    },
    enabled: !!id && enabled,
    refetchInterval: (data) => {
      // Refetch every 2 seconds if analysis is still running
      if (data?.state?.data?.status === 'running' || data?.state?.data?.status === 'pending') {
        return 2000;
      }
      return false;
    },
  });
};

export const useAnalysisResults = (id: string) => {
  return useQuery({
    queryKey: [QUERY_KEYS.ANALYSIS_RESULTS, id],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.ANALYSIS_RESULTS(id));
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateAnalysis = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: AnalysisCreateRequest) => {
      const response = await apiClient.post(API_ENDPOINTS.ANALYSES, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.ANALYSES] });
      toast.success('Analysis started successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start analysis');
    },
  });
};

export const useDeleteAnalysis = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (analysisId: string) => {
      const response = await apiClient.delete(API_ENDPOINTS.ANALYSIS_DELETE(analysisId));
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.ANALYSES] });
      toast.success('Analysis deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete analysis');
    },
  });
};

// Task status hook for monitoring background tasks
export const useTaskStatus = (taskId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [QUERY_KEYS.TASK_STATUS, taskId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/tasks/${taskId}/status`);
      return response.data as TaskStatus;
    },
    enabled: !!taskId && enabled,
    refetchInterval: (data) => {
      // Refetch every 2 seconds if task is still running
      if (data?.state?.data?.status === 'PENDING' || data?.state?.data?.status === 'PROGRESS') {
        return 2000;
      }
      return false;
    },
  });
};

// Health check hook
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.HEALTH);
      return response.data;
    },
    refetchInterval: 30000, // Check every 30 seconds
  });
};

// Session hooks
export const useSessions = (filters?: SessionFilters) => {
  return useQuery({
    queryKey: [QUERY_KEYS.SESSIONS, filters],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.SESSIONS, { params: filters });
      return response.data;
    },
  });
};

export const useSession = (id: string) => {
  return useQuery({
    queryKey: [QUERY_KEYS.SESSION, id],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.SESSION_BY_ID(id));
      return response.data as SessionDetails;
    },
    enabled: !!id,
  });
};

export const useCreateSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: SessionCreateRequest) => {
      const response = await apiClient.post(API_ENDPOINTS.SESSIONS, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SESSIONS] });
      toast.success('Session created successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create session');
    },
  });
};

export const useUpdateSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: SessionUpdateRequest }) => {
      const response = await apiClient.put(API_ENDPOINTS.SESSION_BY_ID(id), data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SESSIONS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SESSION, id] });
      toast.success('Session updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update session');
    },
  });
};

export const useDeleteSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(API_ENDPOINTS.SESSION_BY_ID(id));
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SESSIONS] });
      toast.success('Session deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete session');
    },
  });
};

export const useCompleteSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, overallScore }: { id: string; overallScore?: number }) => {
      const params = overallScore ? { overall_score: overallScore } : {};
      const response = await apiClient.post(API_ENDPOINTS.SESSION_COMPLETE(id), null, { params });
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SESSIONS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SESSION, id] });
      toast.success('Session completed successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to complete session');
    },
  });
};

export const useArchiveSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post(API_ENDPOINTS.SESSION_ARCHIVE(id));
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SESSIONS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SESSION, id] });
      toast.success('Session archived successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to archive session');
    },
  });
};

export const useRestoreSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post(API_ENDPOINTS.SESSION_RESTORE(id));
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SESSIONS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SESSION, id] });
      toast.success('Session restored successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to restore session');
    },
  });
};

export const useSessionStats = () => {
  return useQuery({
    queryKey: ['session-stats'],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.SESSION_STATS);
      return response.data as SessionStats;
    },
  });
};

// Export structured API object
export const useApi = {
  resumes: {
    list: useResumes,
    get: useResume,
    history: useResumeHistory,
    upload: useUploadResume,
    analyze: useAnalyzeResume,
    optimize: useOptimizeResume,
    compare: useResumeComparison,
    delete: useDeleteResume,
  },
  jobs: {
    list: useJobs,
    get: useJob,
    groups: useJobGroups,
    create: useCreateJob,
    createGroup: useCreateJobGroup,
    scrape: useScrapeJobs,
    delete: useDeleteJob,
  },
  analyses: {
    list: useAnalyses,
    get: useAnalysis,
    status: useAnalysisStatus,
    results: useAnalysisResults,
    create: useCreateAnalysis,
    delete: useDeleteAnalysis,
  },
  sessions: {
    list: useSessions,
    get: useSession,
    getDetails: async (id: string) => {
      const response = await apiClient.get(API_ENDPOINTS.SESSION_BY_ID(id));
      return response.data as SessionDetails;
    },
    getStats: useSessionStats,
    create: useCreateSession,
    update: useUpdateSession,
    delete: useDeleteSession,
    complete: useCompleteSession,
    archive: useArchiveSession,
    restore: useRestoreSession,
  },
  tasks: {
    status: useTaskStatus,
  },
  health: useHealthCheck,
};