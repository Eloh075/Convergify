/**
 * API client configuration and base functions
 */
import axios from 'axios';

// API base URL - can be configured via environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default configuration
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens (if needed in future)
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common HTTP errors
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      // Could redirect to login page
    } else if (error.response?.status >= 500) {
      // Handle server errors
      console.error('Server error:', error.response.data);
    }
    return Promise.reject(error);
  }
);

// API endpoints configuration
export const API_ENDPOINTS = {
  // Resume endpoints
  RESUMES: '/api/resumes/',
  RESUME_UPLOAD: '/api/resumes/upload',
  RESUME_BY_ID: (id: string) => `/api/resumes/${id}`,
  RESUME_ANALYZE: (id: string) => `/api/resumes/${id}/analyze`,
  RESUME_OPTIMIZE: (id: string) => `/api/resumes/${id}/optimize`,
  RESUME_HISTORY: (id: string) => `/api/resumes/${id}/history`,
  RESUME_COMPARE: (id: string, optimizedId: string) => `/api/resumes/${id}/compare/${optimizedId}`,
  RESUME_DOWNLOAD: (id: string) => `/api/resumes/${id}/download`,
  RESUME_DELETE: (id: string) => `/api/resumes/${id}`,
  
  // Job endpoints
  JOBS: '/api/jobs/',
  JOB_BY_ID: (id: string) => `/api/jobs/${id}`,
  JOB_DELETE: (id: string) => `/api/jobs/${id}`,
  JOB_SCRAPE: '/api/jobs/scrape',
  JOB_GROUPS: '/api/jobs/groups',
  JOB_GROUP_BY_ID: (id: string) => `/api/jobs/groups/${id}`,
  JOB_GROUP_DELETE: (id: string) => `/api/jobs/groups/${id}`,
  JOB_SEARCH: '/api/jobs/search',
  
  // Analysis endpoints
  ANALYSES: '/api/analyses/',
  ANALYSIS_BY_ID: (id: string) => `/api/analyses/${id}`,
  ANALYSIS_DELETE: (id: string) => `/api/analyses/${id}`,
  ANALYSIS_STATUS: (id: string) => `/api/analyses/${id}/status`,
  ANALYSIS_RESULTS: (id: string) => `/api/analyses/${id}/results`,
  ANALYSIS_RECOMMENDATIONS: (id: string) => `/api/analyses/${id}/recommendations`,
  
  // Session endpoints
  SESSIONS: '/api/sessions/',
  SESSION_BY_ID: (id: string) => `/api/sessions/${id}`,
  SESSION_COMPLETE: (id: string) => `/api/sessions/${id}/complete`,
  SESSION_ARCHIVE: (id: string) => `/api/sessions/${id}/archive`,
  SESSION_RESTORE: (id: string) => `/api/sessions/${id}/restore`,
  SESSION_ADD_ITEM: (id: string) => `/api/sessions/${id}/items`,
  SESSION_REMOVE_ITEM: (id: string, itemType: string, itemId: string) => `/api/sessions/${id}/items/${itemType}/${itemId}`,
  SESSION_STATS: '/api/sessions/stats/user',
  SESSION_AUTO_CREATE: (analysisId: string) => `/api/sessions/auto-create/${analysisId}`,
  
  // Health check
  HEALTH: '/health',
} as const;

// Helper function to handle file uploads
export const uploadFile = async (file: File, endpoint: string, additionalData?: Record<string, any>) => {
  const formData = new FormData();
  formData.append('file', file);
  
  // Add additional form data if provided
  if (additionalData) {
    Object.entries(additionalData).forEach(([key, value]) => {
      formData.append(key, value);
    });
  }
  
  return apiClient.post(endpoint, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// Helper function to download files
export const downloadFile = async (url: string, filename?: string) => {
  const response = await apiClient.get(url, {
    responseType: 'blob',
  });
  
  // Create download link
  const blob = new Blob([response.data]);
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = filename || 'download';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);
};

export default apiClient;