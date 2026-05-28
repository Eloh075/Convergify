import { useState } from 'react';
import { toast } from 'sonner';
import { 
  Upload, 
  Calendar, 
  FileText, 
  Download, 
  X, 
  ChevronRight, 
  Search,
  Filter,
  ArrowUpDown,
  Eye,
  Trash2,
  MoreHorizontal,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  BarChart3
} from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/app/components/ui/dropdown-menu';
import { ResumeUpload } from '@/app/components/ResumeUpload';
import { ResumeComparison } from '@/app/components/ResumeComparison';
import { AnalysisResults } from '@/app/components/AnalysisResults';
import { ConfirmationDialog } from '@/app/components/ui/confirmation-dialog';
import { useResumes, useDeleteResume, useAnalyses, useDeleteAnalysis } from '@/hooks/useApi';
import { AnalysisSession } from '@/app/data/sessionData';
import type { Resume, ResumeFilters, Analysis } from '@/types/api';

interface ResumeVaultProps {
  sessions: AnalysisSession[];
  onUploadNew: () => void;
}

type ViewMode = 'vault' | 'upload';
type SortBy = 'upload_date' | 'filename' | 'file_size' | 'analysis_status';
type SortOrder = 'asc' | 'desc';

function SessionCard({
  session,
  onSelect,
}: {
  session: AnalysisSession;
  onSelect: () => void;
}) {
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <button
      onClick={onSelect}
      className="w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-sm transition-all text-left group"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm mb-1 truncate dark:text-white">{session.title}</h3>
          <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {formatDate(session.createdAt)}
            </span>
            <span>{session.jobCount} jobs</span>
            {session.optimizedResume && (
              <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded-full font-medium">
                Optimized
              </span>
            )}
          </div>
          <div className="mt-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-gray-600 dark:text-gray-300">Match Score:</span>
              <span className="text-sm font-bold" style={{ color: 'var(--primary-blue)' }}>
                {session.analysisResult.overallScore}%
              </span>
            </div>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 flex-shrink-0" />
      </div>
    </button>
  );
}

function ResumeCard({
  resume,
  onView,
  onAnalyze,
  onDelete,
  onCompare,
}: {
  resume: Resume;
  onView: () => void;
  onAnalyze: () => void;
  onDelete: () => void;
  onCompare?: () => void;
}) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'processing':
        return <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'processing':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'failed':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'skills_extracted':
        return 'bg-purple-100 text-purple-700 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-sm transition-all group">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <div className="flex-shrink-0 mt-1">
            <FileText className="w-8 h-8 text-blue-600" />
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-sm mb-1 truncate dark:text-white">
              {resume.filename}
            </h3>
            
            <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 mb-2">
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {formatDate(resume.upload_date)}
              </span>
              <span>{formatFileSize(resume.file_size)}</span>
            </div>

            <div className="flex items-center gap-2">
              {getStatusIcon(resume.analysis_status)}
              <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(resume.analysis_status)}`}>
                {resume.analysis_status.replace('_', ' ')}
              </span>
              {resume.optimized_version_id && (
                <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700 border border-green-200">
                  Optimized
                </span>
              )}
            </div>
          </div>
        </div>

        <div className={`flex items-center gap-2 transition-opacity ${
          isDropdownOpen ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
        }`}>
          <Button variant="outline" size="sm" onClick={onView}>
            <Eye className="w-4 h-4" />
          </Button>
          
          <DropdownMenu onOpenChange={setIsDropdownOpen}>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <MoreHorizontal className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={onView}>
                <Eye className="w-4 h-4 mr-2" />
                View Details
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onAnalyze}>
                <Search className="w-4 h-4 mr-2" />
                Run Analysis
              </DropdownMenuItem>
              {resume.optimized_version_id && onCompare && (
                <DropdownMenuItem onClick={onCompare}>
                  <Eye className="w-4 h-4 mr-2" />
                  Compare Versions
                </DropdownMenuItem>
              )}
              <DropdownMenuItem onClick={onDelete} className="text-red-600">
                <Trash2 className="w-4 h-4 mr-2" />
                Delete Resume
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>
  );
}

function ResumeDetailModal({
  resume,
  onClose,
  onAnalyze,
}: {
  resume: Resume;
  onClose: () => void;
  onAnalyze: () => void;
}) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8 animate-in fade-in duration-200" onClick={onClose}>
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[800px] max-h-[90vh] overflow-y-auto animate-in zoom-in-95 duration-200" onClick={(e) => e.stopPropagation()}>
        <div className="sticky top-0 bg-white dark:bg-gray-800 px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-semibold mb-1 dark:text-white">{resume.filename}</h2>
            <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
              <span>Uploaded {formatDate(resume.upload_date)}</span>
              <span>•</span>
              <span>{formatFileSize(resume.file_size)}</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="font-semibold mb-2 dark:text-white">File Information</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">File Size:</span>
                  <span className="dark:text-white">{formatFileSize(resume.file_size)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Upload Date:</span>
                  <span className="dark:text-white">{formatDate(resume.upload_date)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Status:</span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
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
            </div>
            
            <div>
              <h3 className="font-semibold mb-2 dark:text-white">Analysis</h3>
              <div className="space-y-2 text-sm">
                {resume.extracted_skills && resume.extracted_skills.length > 0 ? (
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Skills Found:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {resume.extracted_skills.slice(0, 5).map((skill, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                          {skill}
                        </span>
                      ))}
                      {resume.extracted_skills.length > 5 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                          +{resume.extracted_skills.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500 dark:text-gray-400">No skills extracted yet</p>
                )}
                
                {resume.optimized_version_id && (
                  <div className="flex items-center gap-2 text-green-600">
                    <CheckCircle className="w-4 h-4" />
                    <span className="text-sm">Optimized version available</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <h3 className="font-semibold mb-3 dark:text-white">Actions</h3>
            <div className="flex gap-3">
              <Button onClick={onAnalyze} className="gap-2">
                <Search className="w-4 h-4" />
                Run Analysis
              </Button>
              <Button variant="outline" className="gap-2">
                <Download className="w-4 h-4" />
                Download
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ComparisonView({
  session,
  onClose,
}: {
  session: AnalysisSession;
  onClose: () => void;
}) {
  const handleExportPDF = () => {
    // Mock export functionality
    toast.info('PDF export functionality coming soon');
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[1400px] h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-xl font-semibold dark:text-white">{session.title}</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {session.optimizedResume
                ? `Version: ${session.optimizedResume.versionTag}`
                : 'Original resume only'}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {session.optimizedResume && (
              <Button onClick={handleExportPDF} className="gap-2">
                <Download className="w-4 h-4" />
                Export PDF
              </Button>
            )}
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 dark:text-gray-300" />
            </button>
          </div>
        </div>

        {/* Side-by-Side Comparison */}
        <div className="flex-1 flex overflow-hidden">
          {/* Original Resume */}
          <div className="flex-1 border-r border-gray-200 dark:border-gray-700 flex flex-col">
            <div className="px-6 py-3 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200">Original Resume</h3>
            </div>
            <div className="flex-1 overflow-y-auto p-6">
              <div className="prose prose-sm max-w-none">
                <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-6 text-center">
                  <FileText className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-3" />
                  <p className="text-sm text-gray-600 dark:text-gray-300">PDF Viewer</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Original resume would be displayed here
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Optimized Resume */}
          <div className="flex-1 flex flex-col">
            <div className="px-6 py-3 bg-green-50 dark:bg-green-900/20 border-b border-green-200 dark:border-green-800">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-green-700 dark:text-green-200">
                  Optimized Resume
                  {session.optimizedResume && (
                    <span className="ml-2 text-xs font-normal text-green-600 dark:text-green-300">
                      ({session.optimizedResume.versionTag})
                    </span>
                  )}
                </h3>
                {session.optimizedResume && (
                  <span className="text-xs text-green-600 dark:text-green-300">
                    {session.optimizedResume.createdAt.toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-6">
              {session.optimizedResume ? (
                <div className="prose prose-sm max-w-none">
                  {/* Render markdown with highlighting */}
                  <div className="space-y-4">
                    <h1 className="text-2xl font-bold dark:text-white">John Doe</h1>
                    <p className="text-lg text-gray-600 dark:text-gray-300">Strategic Account Executive</p>
                    
                    <h2 className="text-xl font-semibold mt-6 dark:text-white">Professional Summary</h2>
                    <p className="text-gray-700 dark:text-gray-300">
                      Results-driven Account Executive with{' '}
                      <span className="bg-orange-100 dark:bg-orange-900/30 px-1 rounded">8+ years of proven success</span>{' '}
                      in managing{' '}
                      <span className="bg-orange-100 dark:bg-orange-900/30 px-1 rounded">enterprise-level SaaS accounts</span>{' '}
                      and driving revenue growth through strategic relationship building.
                    </p>

                    <h2 className="text-xl font-semibold mt-6 dark:text-white">Key Skills</h2>
                    <ul className="list-disc pl-5 space-y-1 dark:text-gray-300">
                      <li>
                        <span className="bg-orange-100 dark:bg-orange-900/30 px-1 rounded">Strategic Account Management</span>
                      </li>
                      <li>Cross-functional Leadership</li>
                      <li>
                        <span className="bg-orange-100 dark:bg-orange-900/30 px-1 rounded">B2B SaaS Sales</span>
                      </li>
                      <li>Revenue Growth & Upselling</li>
                    </ul>

                    <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500 dark:border-blue-400 rounded">
                      <p className="text-sm text-blue-800 dark:text-blue-200">
                        <strong>Changes highlighted in orange</strong> - These modifications
                        optimize your resume for the target market based on AI analysis.
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-gray-500 dark:text-gray-400 mb-4">No optimized version yet</p>
                    <Button variant="outline">Generate Optimization</Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Analysis Footer */}
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
          <div className="flex items-center gap-8">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Overall Match</p>
              <p className="text-xl font-bold" style={{ color: 'var(--primary-blue)' }}>
                {session.analysisResult.overallScore}%
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Must-Haves</p>
              <p className="text-xl font-bold" style={{ color: 'var(--success-green)' }}>
                {session.analysisResult.mustHaveScore}%
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Nice-to-Haves</p>
              <p className="text-xl font-bold text-gray-600 dark:text-gray-300">
                {session.analysisResult.niceToHaveScore}%
              </p>
            </div>
            <div className="ml-auto">
              <p className="text-xs text-gray-500 dark:text-gray-400">Jobs Analyzed</p>
              <p className="text-xl font-bold text-gray-700 dark:text-gray-200">{session.jobCount}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function ResumeVault({ sessions, onUploadNew }: ResumeVaultProps) {
  const [selectedSession, setSelectedSession] = useState<AnalysisSession | null>(null);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);
  const [comparisonResume, setComparisonResume] = useState<Resume | null>(null);
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('vault');
  const [deleteConfirmation, setDeleteConfirmation] = useState<{
    open: boolean;
    resume: Resume | null;
  }>({ open: false, resume: null });
  
  const [deleteAnalysisConfirmation, setDeleteAnalysisConfirmation] = useState<{
    open: boolean;
    analysis: Analysis | null;
  }>({ open: false, analysis: null });
  
  // Filtering and sorting state
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<SortBy>('upload_date');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Build filters for API call
  const filters: ResumeFilters = {
    status: statusFilter === 'all' ? undefined : statusFilter,
    sort_by: sortBy,
    sort_order: sortOrder,
    skip: (currentPage - 1) * itemsPerPage,
    limit: itemsPerPage,
  };

  // Fetch real resumes from backend
  const { data: resumes, isLoading, error, refetch } = useResumes(filters);
  
  // Fetch analyses for the resumes (only completed ones)
  const { data: analyses } = useAnalyses({
    status: 'completed',
    sort_by: 'created_at',
    sort_order: 'desc',
    limit: 50
  });
  
  // Delete mutation
  const deleteResumeMutation = useDeleteResume();
  const deleteAnalysisMutation = useDeleteAnalysis();

  // Filter resumes by search query (client-side for now)
  const filteredResumes = resumes?.filter(resume =>
    resume.filename.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const totalPages = Math.ceil((filteredResumes.length || 0) / itemsPerPage);

  const handleUploadClick = () => {
    setViewMode('upload');
  };

  const handleUploadComplete = (resumeId: string) => {
    console.log('Resume uploaded successfully:', resumeId);
    setViewMode('vault');
    refetch(); // Refresh the resume list
  };

  const handleUploadCancel = () => {
    setViewMode('vault');
  };

  const handleResumeView = (resume: Resume) => {
    setSelectedResume(resume);
  };

  const handleResumeAnalyze = (resume: Resume) => {
    console.log('Starting analysis for resume:', resume.id);
    // This would trigger the analysis workflow
  };

  const handleResumeDelete = (resume: Resume) => {
    setDeleteConfirmation({ open: true, resume });
  };

  const handleDeleteSingleAnalysis = (analysis: Analysis) => {
    setDeleteAnalysisConfirmation({ open: true, analysis });
  };

  const confirmDeleteAnalysis = () => {
    if (deleteAnalysisConfirmation.analysis) {
      deleteAnalysisMutation.mutate(deleteAnalysisConfirmation.analysis.id);
      setDeleteAnalysisConfirmation({ open: false, analysis: null });
    }
  };

  const confirmDelete = () => {
    if (deleteConfirmation.resume) {
      deleteResumeMutation.mutate(deleteConfirmation.resume.id);
    }
  };

  const handleResumeCompare = (resume: Resume) => {
    if (resume.optimized_version_id) {
      setComparisonResume(resume);
    }
  };

  const handleSortChange = (newSortBy: SortBy) => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('desc');
    }
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  if (viewMode === 'upload') {
    return (
      <div className="flex-1 h-full overflow-y-auto bg-gray-50 dark:bg-gray-900">
        <div className="max-w-[1000px] mx-auto p-4 sm:p-8 lg:p-12">
          <ResumeUpload 
            onUploadComplete={handleUploadComplete}
            onCancel={handleUploadCancel}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 h-full overflow-y-auto bg-gray-50 dark:bg-gray-900">
      <div className="max-w-[1200px] mx-auto p-4 sm:p-8 lg:p-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-6 bg-gradient-to-br from-blue-500 to-blue-600">
            <FileText className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-semibold mb-3 dark:text-white">Resume Vault</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Manage your resumes and track analysis history
          </p>
          <Button size="lg" onClick={handleUploadClick} className="gap-2">
            <Upload className="w-4 h-4" />
            Upload New Resume
          </Button>
        </div>

        {/* Filters and Search */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                placeholder="Search resumes by filename..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Status Filter */}
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="processing">Processing</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
                <SelectItem value="skills_extracted">Skills Extracted</SelectItem>
              </SelectContent>
            </Select>

            {/* Sort */}
            <Select value={`${sortBy}_${sortOrder}`} onValueChange={(value) => {
              const [field, order] = value.split('_') as [SortBy, SortOrder];
              setSortBy(field);
              setSortOrder(order);
              setCurrentPage(1);
            }}>
              <SelectTrigger className="w-[200px]">
                <ArrowUpDown className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="upload_date_desc">Newest First</SelectItem>
                <SelectItem value="upload_date_asc">Oldest First</SelectItem>
                <SelectItem value="filename_asc">Name A-Z</SelectItem>
                <SelectItem value="filename_desc">Name Z-A</SelectItem>
                <SelectItem value="file_size_desc">Largest First</SelectItem>
                <SelectItem value="file_size_asc">Smallest First</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Resume List */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold dark:text-white">
              Your Resumes {filteredResumes.length > 0 && `(${filteredResumes.length})`}
            </h2>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="text-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">Loading resumes...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="text-center py-12">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <p className="text-red-600 mb-4">Failed to load resumes</p>
              <Button variant="outline" onClick={() => refetch()}>
                Try Again
              </Button>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !error && filteredResumes.length === 0 && (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2 dark:text-white">
                {searchQuery || statusFilter !== 'all' ? 'No matching resumes' : 'No resumes yet'}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                {searchQuery || statusFilter !== 'all' 
                  ? 'Try adjusting your search or filters'
                  : 'Upload your first resume to get started with AI-powered career analysis'
                }
              </p>
              {!searchQuery && statusFilter === 'all' && (
                <Button onClick={handleUploadClick} className="gap-2">
                  <Upload className="w-4 h-4" />
                  Upload Your First Resume
                </Button>
              )}
            </div>
          )}

          {/* Resume Cards */}
          {!isLoading && !error && filteredResumes.length > 0 && (
            <div className="space-y-4">
              {filteredResumes.map((resume) => (
                <ResumeCard
                  key={resume.id}
                  resume={resume}
                  onView={() => handleResumeView(resume)}
                  onAnalyze={() => handleResumeAnalyze(resume)}
                  onDelete={() => handleResumeDelete(resume)}
                  onCompare={() => handleResumeCompare(resume)}
                />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <Button
                  key={page}
                  variant={currentPage === page ? "default" : "outline"}
                  size="sm"
                  onClick={() => handlePageChange(page)}
                  className="w-10"
                >
                  {page}
                </Button>
              ))}
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </div>
          )}
        </div>

        {/* Real Analysis History */}
        {analyses && analyses.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold mb-4 dark:text-white">Analysis History</h2>
            <div className="space-y-3">
              {analyses.map((analysis) => {
                const resume = resumes?.find(r => r.id === analysis.resume_id);
                return (
                  <div
                    key={analysis.id}
                    className="w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-blue-500 dark:hover:border-blue-400 hover:shadow-sm transition-all group"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <button
                        onClick={() => setSelectedAnalysisId(analysis.id)}
                        className="flex items-start gap-3 flex-1 text-left"
                      >
                        <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                          <BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold mb-1 dark:text-white truncate">
                            {resume?.filename || 'Resume Analysis'}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                            {analysis.job_count} jobs analyzed • {analysis.status}
                          </p>
                          <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                            <Clock className="w-3 h-3" />
                            {new Date(analysis.start_date).toLocaleDateString()}
                          </div>
                        </div>
                      </button>
                      <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedAnalysisId(analysis.id)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteSingleAnalysis(analysis);
                          }}
                          className="text-red-600 hover:text-red-700 hover:border-red-300"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Analysis Results Modal */}
      {selectedAnalysisId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-y-auto animate-in zoom-in-95 duration-200">
            <div className="sticky top-0 bg-white dark:bg-gray-800 px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between z-10">
              <h2 className="text-xl font-semibold dark:text-white">Analysis Results</h2>
              <button
                onClick={() => setSelectedAnalysisId(null)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6">
              <AnalysisResults 
                analysisId={selectedAnalysisId}
                onExport={(format) => {
                  console.log(`Exporting as ${format}`);
                  toast.success(`Exporting analysis as ${format.toUpperCase()}`);
                }}
                onOptimizeResume={() => {
                  console.log('Optimizing resume');
                  toast.success('Resume optimization started');
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Resume Detail Modal */}
      {selectedResume && (
        <ResumeDetailModal
          resume={selectedResume}
          onClose={() => setSelectedResume(null)}
          onAnalyze={() => handleResumeAnalyze(selectedResume)}
        />
      )}

      {/* Comparison Modal */}
      {selectedSession && (
        <ComparisonView
          session={selectedSession}
          onClose={() => setSelectedSession(null)}
        />
      )}

      {/* Resume Comparison Modal */}
      {comparisonResume && comparisonResume.optimized_version_id && (
        <ResumeComparison
          originalResume={comparisonResume}
          optimizedResumeId={comparisonResume.optimized_version_id}
          onClose={() => setComparisonResume(null)}
          onExport={(format) => {
            console.log(`Exporting comparison as ${format}`);
            // Handle export functionality
          }}
        />
      )}

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        open={deleteConfirmation.open}
        onOpenChange={(open) => setDeleteConfirmation({ open, resume: null })}
        title="Delete Resume"
        description={
          deleteConfirmation.resume
            ? `Are you sure you want to delete "${deleteConfirmation.resume.filename}"? This action cannot be undone and will remove all associated analyses.`
            : ''
        }
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
        onConfirm={confirmDelete}
      />

      {/* Delete Analysis Confirmation Dialog */}
      <ConfirmationDialog
        open={deleteAnalysisConfirmation.open}
        onOpenChange={(open) => setDeleteAnalysisConfirmation({ open, analysis: null })}
        title="Delete Analysis"
        description={
          deleteAnalysisConfirmation.analysis
            ? (() => {
                const resume = resumes?.find(r => r.id === deleteAnalysisConfirmation.analysis?.resume_id);
                const resumeName = resume?.filename || 'this resume';
                const jobCount = deleteAnalysisConfirmation.analysis.job_count;
                const date = new Date(deleteAnalysisConfirmation.analysis.start_date).toLocaleDateString();
                return `Delete this analysis for "${resumeName}"?\n\nAnalyzed ${jobCount} jobs on ${date}\n\nThis action cannot be undone.`;
              })()
            : ''
        }
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
        onConfirm={confirmDeleteAnalysis}
      />
    </div>
  );
}