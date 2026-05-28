import { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  FolderPlus, 
  Check, 
  MapPin, 
  Calendar, 
  Zap, 
  X, 
  Building2, 
  FileText,
  Eye,
  Trash2,
  ArrowUpDown,
  Filter,
  Grid3X3,
  List,
  Loader2,
  AlertCircle,
  Briefcase,
  ChevronDown,
  ChevronUp,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Textarea } from '@/app/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import { 
  useJobs, 
  useJobGroups, 
  useCreateJob, 
  useCreateJobGroup, 
  useDeleteJob,
  useDeleteJobGroup,
  useScrapeJobs,
  useTaskStatus
} from '@/hooks/useApi';
import type { Job, JobGroup, JobCreateRequest, JobGroupCreateRequest, ScrapingConfig } from '@/types/api';

interface JobHubProps {
  onStartScraper: () => void;
  onRunAnalysis: (jobIds: string[]) => void;
}

type SortBy = 'created_date' | 'company' | 'location';
type ViewMode = 'grid' | 'list';

function ManualJobModal({ onClose }: { onClose: () => void }) {
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [location, setLocation] = useState('');
  const [description, setDescription] = useState('');
  
  const createJobMutation = useCreateJob();

  const handleSave = () => {
    if (!title.trim() || !company.trim() || !description.trim()) {
      toast.error('Please fill in all required fields');
      return;
    }

    const jobData: JobCreateRequest = {
      title: title.trim(),
      company: company.trim(),
      location: location.trim() || undefined,
      description: description.trim(),
    };

    createJobMutation.mutate(jobData, {
      onSuccess: () => {
        onClose();
      }
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8 animate-in fade-in duration-200">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[600px] animate-in zoom-in-95 duration-200">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold dark:text-white">Add Job Manually</h2>
        </div>
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">Job Title</label>
            <Input
              placeholder="e.g., Senior Account Manager"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">Company</label>
            <Input
              placeholder="e.g., Salesforce"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">Location</label>
            <Input
              placeholder="e.g., San Francisco, CA"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">Job Description</label>
            <Textarea
              placeholder="Paste the full job description here..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={6}
            />
          </div>
        </div>
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-750 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleSave} 
            disabled={createJobMutation.isPending || !title.trim() || !company.trim() || !description.trim()}
          >
            {createJobMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Adding...
              </>
            ) : (
              'Add Job'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

function JobCard({
  job,
  isSelected,
  onToggle,
  onClick,
  onDelete,
  showCheckbox = true,
}: {
  job: Job;
  isSelected: boolean;
  onToggle: () => void;
  onClick?: () => void;
  onDelete?: () => void;
  showCheckbox?: boolean;
}) {
  const [isHovered, setIsHovered] = useState(false);

  const handleClick = (e: React.MouseEvent) => {
    if (showCheckbox) {
      onToggle();
    } else if (onClick) {
      onClick();
    }
  };

  const handleQuickView = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onClick) onClick();
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete) onDelete();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  return (
    <div
      className={`bg-white dark:bg-gray-800 border rounded-lg p-4 transition-all cursor-pointer group ${
        isSelected
          ? 'border-blue-500 shadow-sm'
          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-sm'
      }`}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        {showCheckbox && (
          <div
            className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors ${
              isSelected
                ? 'bg-blue-600 border-blue-600'
                : 'border-gray-300 dark:border-gray-600'
            }`}
          >
            {isSelected && <Check className="w-3 h-3 text-white" />}
          </div>
        )}

        {/* Job Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold mb-1 truncate dark:text-white">{job.title}</h3>
          <p className="text-sm text-gray-900 dark:text-gray-300 mb-2">{job.company}</p>
          <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
            {job.location && (
              <span className="flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                {job.location}
              </span>
            )}
            {job.employment_type && (
              <span className="flex items-center gap-1">
                <Briefcase className="w-3 h-3" />
                {job.employment_type}
              </span>
            )}
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {formatDate(job.created_date)}d ago
            </span>
          </div>
        </div>

        {/* Quick Actions (hover only) */}
        {!showCheckbox && isHovered && (
          <div className="flex items-center gap-2 opacity-100 transition-opacity">
            <button
              onClick={handleQuickView}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title="Quick view"
            >
              <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            </button>
            <button
              onClick={handleDelete}
              className="p-2 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors"
              title="Remove"
            >
              <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function ScrapingConfigModal({ onClose, onStart }: { 
  onClose: () => void; 
  onStart: (config: ScrapingConfig) => void; 
}) {
  const [searchTerm, setSearchTerm] = useState('developer');
  const [employmentType, setEmploymentType] = useState('full-time');
  const [maxJobs, setMaxJobs] = useState(10);

  const handleStart = () => {
    if (!searchTerm.trim()) {
      toast.error('Please enter a search term');
      return;
    }

    const config: ScrapingConfig = {
      search_terms: [searchTerm.trim()], // Single search term in array
      employment_type: employmentType,
      max_jobs: maxJobs
    };

    onStart(config);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8 animate-in fade-in duration-200">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[600px] animate-in zoom-in-95 duration-200">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold dark:text-white">Configure Job Discovery</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Set up automatic job scraping from MyCareersFuture
          </p>
        </div>
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Search Term
            </label>
            <Input
              placeholder="e.g., developer, data analyst, marketing manager"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">
              Enter one specific job title or role
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Employment Type
            </label>
            <Select value={employmentType} onValueChange={setEmploymentType}>
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
              Maximum Jobs to Scrape
            </label>
            <Select value={maxJobs.toString()} onValueChange={(value) => setMaxJobs(parseInt(value))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5 jobs</SelectItem>
                <SelectItem value="10">10 jobs</SelectItem>
                <SelectItem value="20">20 jobs</SelectItem>
                <SelectItem value="50">50 jobs</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleStart} className="bg-purple-600 hover:bg-purple-700">
            <Zap className="w-4 h-4 mr-2" />
            Start Discovery
          </Button>
        </div>
      </div>
    </div>
  );
}
function ScrapingProgressCard({ 
  taskId, 
  searchTerms,
  startTime: providedStartTime,
  onComplete 
}: { 
  taskId: string; 
  searchTerms: string[];
  startTime?: number;
  onComplete: () => void;
}) {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('Starting job discovery...');
  const [isComplete, setIsComplete] = useState(false);
  const [jobCount, setJobCount] = useState(0);
  const [initialJobCount, setInitialJobCount] = useState<number | null>(null);

  useEffect(() => {
    let pollInterval: NodeJS.Timeout;
    const startTime = providedStartTime || Date.now();
    const maxDuration = 300000; // 5 minutes max
    
    // Get initial job count
    const getInitialCount = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/jobs/?sort_by=created_date&sort_order=desc');
        const jobs = await response.json();
        setInitialJobCount(jobs.length);
      } catch (error) {
        console.error('Error getting initial job count:', error);
        setInitialJobCount(0);
      }
    };
    
    getInitialCount();
    
    // Poll for new jobs every 3 seconds
    pollInterval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/jobs/?sort_by=created_date&sort_order=desc');
        const jobs = await response.json();
        const currentCount = jobs.length;
        
        if (initialJobCount !== null) {
          const newJobs = currentCount - initialJobCount;
          setJobCount(newJobs);
          
          if (newJobs > 0) {
            setMessage(`Found ${newJobs} new jobs...`);
            // Estimate progress based on time and jobs found
            const timeProgress = Math.min(((Date.now() - startTime) / maxDuration) * 100, 90);
            const jobProgress = Math.min((newJobs / 10) * 100, 90); // Assume max 10 jobs
            setProgress(Math.max(timeProgress, jobProgress));
          } else {
            const elapsed = Date.now() - startTime;
            if (elapsed < 10000) {
              setMessage('Initializing browser...');
              setProgress(10);
            } else if (elapsed < 30000) {
              setMessage('Searching for jobs...');
              setProgress(30);
            } else if (elapsed < 60000) {
              setMessage('Extracting job details...');
              setProgress(50);
            } else {
              setMessage('Processing results...');
              setProgress(70);
            }
          }
          
          // Check if scraping is complete (no new jobs for a while or max time reached)
          if (newJobs > 0 && (Date.now() - startTime) > 120000) {
            setProgress(100);
            setMessage(`Discovery complete! Found ${newJobs} jobs`);
            setIsComplete(true);
            clearInterval(pollInterval);
            setTimeout(() => {
              onComplete();
            }, 2000);
          } else if (Date.now() - startTime > maxDuration) {
            setProgress(100);
            setMessage(newJobs > 0 ? `Discovery complete! Found ${newJobs} jobs` : 'Discovery timed out');
            setIsComplete(true);
            clearInterval(pollInterval);
            setTimeout(() => {
              onComplete();
            }, 2000);
          }
        }
      } catch (error) {
        console.error('Error polling for jobs:', error);
      }
    }, 3000);

    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [taskId, onComplete, initialJobCount]);

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center flex-shrink-0">
          {isComplete ? (
            <Check className="w-5 h-5 text-green-600 dark:text-green-400" />
          ) : (
            <Loader2 className="w-5 h-5 text-purple-600 dark:text-purple-400 animate-spin" />
          )}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold mb-1 dark:text-white">
            Discovering: {searchTerms.join(', ')}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
            {message}
          </p>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
            <div 
              className="bg-purple-600 h-2 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {progress.toFixed(0)}% complete • Task: {taskId.slice(-8)}
          </div>
        </div>
      </div>
    </div>
  );
}

function JobDetailModal({ job, onClose }: { job: Job; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8 animate-in fade-in duration-200" onClick={onClose}>
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[800px] max-h-[90vh] overflow-y-auto animate-in zoom-in-95 duration-200" onClick={(e) => e.stopPropagation()}>
        <div className="sticky top-0 bg-white dark:bg-gray-800 px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-semibold mb-1 dark:text-white">{job.title}</h2>
            <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-300">
              <span className="flex items-center gap-1">
                <Building2 className="w-4 h-4" />
                {job.company}
              </span>
              {job.location && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {job.location}
                </span>
              )}
              {job.employment_type && (
                <span className="flex items-center gap-1">
                  <Briefcase className="w-4 h-4" />
                  {job.employment_type}
                </span>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 dark:text-gray-300" />
          </button>
        </div>
        <div className="p-6">
          <div className="mb-6">
            <h3 className="font-semibold mb-2 dark:text-white">Job Description</h3>
            <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">
              {job.description || 'No description available.'}
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
            <Calendar className="w-4 h-4" />
            <span>Posted {job.postedDays} days ago</span>
          </div>
        </div>
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
          <Button>Apply to Job</Button>
        </div>
      </div>
    </div>
  );
}

function CreateGroupModal({ 
  selectedJobIds, 
  onClose
}: { 
  selectedJobIds: string[]; 
  onClose: () => void;
}) {
  const [groupName, setGroupName] = useState('');
  const [description, setDescription] = useState('');
  
  const createGroupMutation = useCreateJobGroup();

  const handleSave = () => {
    if (!groupName.trim()) {
      toast.error('Please enter a group name');
      return;
    }

    const groupData: JobGroupCreateRequest = {
      name: groupName.trim(),
      description: description.trim() || undefined,
      job_ids: selectedJobIds,
    };

    createGroupMutation.mutate(groupData, {
      onSuccess: () => {
        onClose();
      }
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8 animate-in fade-in duration-200" onClick={onClose}>
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[500px] animate-in zoom-in-95 duration-200" onClick={(e) => e.stopPropagation()}>
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold dark:text-white">Create Group</h2>
        </div>
        <div className="p-6">
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
            Creating group with {selectedJobIds.length} selected job{selectedJobIds.length !== 1 ? 's' : ''}
          </p>
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">Group Name</label>
            <Input
              placeholder="e.g., FAANG Senior Roles"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              autoFocus
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">Description (Optional)</label>
            <Textarea
              placeholder="Brief description of this job group..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>
        </div>
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleSave} 
            disabled={createGroupMutation.isPending || !groupName.trim()}
          >
            {createGroupMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              'Create Group'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

// Empty State Component
function EmptyState({ 
  icon: Icon, 
  title, 
  description, 
  action 
}: { 
  icon: React.ElementType; 
  title: string; 
  description: string; 
  action?: { label: string; onClick: () => void }; 
}) {
  return (
    <div className="text-center py-16">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-100 dark:bg-gray-800 mb-4">
        <Icon className="w-8 h-8 text-gray-400 dark:text-gray-500" />
      </div>
      <h3 className="text-lg font-semibold mb-2 dark:text-white">{title}</h3>
      <p className="text-gray-600 dark:text-gray-300 mb-6 max-w-md mx-auto">{description}</p>
      {action && (
        <Button onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </div>
  );
}

export function JobHub({
  onStartScraper,
  onRunAnalysis,
}: JobHubProps) {
  const [view, setView] = useState<'scraping' | 'groups' | 'all'>('all');
  const [groupFilter, setGroupFilter] = useState<'all' | 'scraped' | 'custom'>('all');
  const [selectedJobIds, setSelectedJobIds] = useState<string[]>([]);
  const [showManualModal, setShowManualModal] = useState(false);
  const [showScrapingModal, setShowScrapingModal] = useState(false);
  const [showJobDetailModal, setShowJobDetailModal] = useState<Job | null>(null);
  const [showCreateGroupModal, setShowCreateGroupModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [allViewMode, setAllViewMode] = useState<'browse' | 'select'>('browse');
  const [sortBy, setSortBy] = useState<SortBy>('created_date');
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(new Set());
  
  // Initialize activeScrapeTask from localStorage
  const [activeScrapeTask, setActiveScrapeTask] = useState<{
    taskId: string;
    searchTerms: string[];
    startTime: number;
  } | null>(() => {
    try {
      const saved = localStorage.getItem('activeScrapeTask');
      if (saved) {
        const task = JSON.parse(saved);
        // Only restore if task is less than 10 minutes old
        if (Date.now() - task.startTime < 600000) {
          return task;
        } else {
          localStorage.removeItem('activeScrapeTask');
        }
      }
    } catch (error) {
      console.error('Error loading scrape task from localStorage:', error);
    }
    return null;
  });

  // Persist activeScrapeTask to localStorage whenever it changes
  useEffect(() => {
    if (activeScrapeTask) {
      localStorage.setItem('activeScrapeTask', JSON.stringify(activeScrapeTask));
    } else {
      localStorage.removeItem('activeScrapeTask');
    }
  }, [activeScrapeTask]);

  // Set view to scraping if there's an active task on mount
  useEffect(() => {
    if (activeScrapeTask) {
      setView('scraping');
    }
  }, []);

  // API hooks
  const { data: jobs = [], isLoading: jobsLoading, error: jobsError, refetch: refetchJobs } = useJobs({
    sort_by: sortBy,
    sort_order: 'desc',
  });
  
  const { data: groups = [], isLoading: groupsLoading, refetch: refetchGroups } = useJobGroups();
  
  const deleteJobMutation = useDeleteJob();
  const deleteJobGroupMutation = useDeleteJobGroup();
  const scrapeJobsMutation = useScrapeJobs();

  // Initialize all groups as collapsed by default
  useEffect(() => {
    if (groups.length > 0) {
      setCollapsedGroups(new Set(groups.map(g => g.id)));
    }
  }, [groups.length]); // Only run when groups count changes

  const handleToggleJob = (jobId: string) => {
    setSelectedJobIds((prev) =>
      prev.includes(jobId) ? prev.filter((id) => id !== jobId) : [...prev, jobId]
    );
  };

  const handleRunAnalysis = () => {
    if (selectedJobIds.length > 0) {
      onRunAnalysis(selectedJobIds);
    }
  };

  const handleDeleteJob = (job: Job) => {
    deleteJobMutation.mutate(job.id);
  };

  const handleStartScraping = () => {
    setShowScrapingModal(true);
  };

  const handleScrapingStart = (config: ScrapingConfig) => {
    scrapeJobsMutation.mutate(config, {
      onSuccess: (response) => {
        setActiveScrapeTask({
          taskId: response.task_id,
          searchTerms: config.search_terms,
          startTime: Date.now()
        });
        setView('scraping');
      }
    });
  };

  const handleScrapingComplete = () => {
    setActiveScrapeTask(null);
    refetchJobs();
    setView('all');
  };

  const toggleGroupCollapse = (groupId: string) => {
    setCollapsedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(groupId)) {
        newSet.delete(groupId);
      } else {
        newSet.add(groupId);
      }
      return newSet;
    });
  };

  const handleSelectAllInGroup = (groupJobIds: string[], event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent collapse toggle
    const allSelected = groupJobIds.every(id => selectedJobIds.includes(id));
    
    if (allSelected) {
      // Deselect all jobs in this group
      setSelectedJobIds(prev => prev.filter(id => !groupJobIds.includes(id)));
    } else {
      // Select all jobs in this group
      setSelectedJobIds(prev => {
        const newIds = [...prev];
        groupJobIds.forEach(id => {
          if (!newIds.includes(id)) {
            newIds.push(id);
          }
        });
        return newIds;
      });
    }
  };

  // Filter jobs based on search query
  const filteredJobs = jobs
    .filter((job) => {
      if (!searchQuery) return true;
      const query = searchQuery.toLowerCase();
      return (
        job.title.toLowerCase().includes(query) ||
        job.company.toLowerCase().includes(query) ||
        (job.location && job.location.toLowerCase().includes(query))
      );
    })
    .sort((a, b) => {
      if (sortBy === 'created_date') return new Date(b.created_date).getTime() - new Date(a.created_date).getTime();
      if (sortBy === 'company') return a.company.localeCompare(b.company);
      if (sortBy === 'location') return (a.location || '').localeCompare(b.location || '');
      return 0;
    });

  const hasJobs = jobs.length > 0;

  return (
    <div className="flex-1 h-full overflow-y-auto transition-colors duration-300 bg-gray-50 dark:bg-gray-900">
      <div className="max-w-[1200px] mx-auto p-4 sm:p-6 lg:p-8 xl:p-12">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-semibold mb-3 dark:text-white">Job Hub</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Build your job library through manual entry or automated discovery
          </p>
        </div>

        {/* Input Header - Two-Way Entry */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <button
            onClick={() => setShowManualModal(true)}
            className="bg-white dark:bg-gray-800 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-6 hover:border-gray-400 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-all"
          >
            <Plus className="w-8 h-8 text-gray-400 dark:text-gray-500 mx-auto mb-3" />
            <p className="font-semibold dark:text-white">Add Job Manually</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Paste job details from any source
            </p>
          </button>

          <button
            onClick={handleStartScraping}
            disabled={scrapeJobsMutation.isPending}
            className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl p-6 hover:from-purple-600 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {scrapeJobsMutation.isPending ? (
              <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin" />
            ) : (
              <Zap className="w-8 h-8 mx-auto mb-3" />
            )}
            <p className="font-semibold">
              {scrapeJobsMutation.isPending ? 'Starting...' : 'Activate Discovery Mode'}
            </p>
            <p className="text-sm text-purple-100 mt-1">
              Auto-scrape matching positions
            </p>
          </button>
        </div>

        {/* View Switcher & Controls */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="inline-flex rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-1">
              <button
                onClick={() => setView('scraping')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  view === 'scraping'
                    ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Discovery
              </button>
              <button
                onClick={() => setView('groups')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  view === 'groups'
                    ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Groups
              </button>
              <button
                onClick={() => setView('all')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  view === 'all'
                    ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                All Jobs
              </button>
            </div>
            
            {/* Refresh Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                refetchJobs();
                refetchGroups();
                toast.success('Refreshed jobs and groups');
              }}
              disabled={jobsLoading || groupsLoading}
              className="gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${(jobsLoading || groupsLoading) ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>

          {selectedJobIds.length > 0 && (
            <div className="flex items-center gap-3 animate-in slide-in-from-right duration-200">
              <span className="text-sm text-gray-600 dark:text-gray-300">
                {selectedJobIds.length} selected
              </span>
              <Button onClick={handleRunAnalysis} className="gap-2">
                <Search className="w-4 h-4" />
                Run Analysis
              </Button>
              <Button variant="outline" className="gap-2" onClick={() => setShowCreateGroupModal(true)}>
                <FolderPlus className="w-4 h-4" />
                Save to Group
              </Button>
            </div>
          )}
        </div>

        {/* Discovery/Scraping View */}
        {view === 'scraping' && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {activeScrapeTask ? (
              <ScrapingProgressCard
                taskId={activeScrapeTask.taskId}
                searchTerms={activeScrapeTask.searchTerms}
                startTime={activeScrapeTask.startTime}
                onComplete={handleScrapingComplete}
              />
            ) : (
              <EmptyState
                icon={Zap}
                title="No Active Discovery Sessions"
                description="Start discovering jobs automatically by activating Discovery Mode"
                action={{ label: 'Activate Discovery Mode', onClick: handleStartScraping }}
              />
            )}
          </div>
        )}

        {/* Groups View */}
        {view === 'groups' && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Group Filter */}
            <div className="flex items-center gap-2 mb-4">
              <Filter className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filter:</span>
              <div className="flex gap-2">
                <button
                  onClick={() => setGroupFilter('all')}
                  className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                    groupFilter === 'all'
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-400 dark:hover:bg-gray-600'
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setGroupFilter('scraped')}
                  className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                    groupFilter === 'scraped'
                      ? 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-400 dark:hover:bg-gray-600'
                  }`}
                >
                  Scraped
                </button>
                <button
                  onClick={() => setGroupFilter('custom')}
                  className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                    groupFilter === 'custom'
                      ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-400 dark:hover:bg-gray-600'
                  }`}
                >
                  Custom
                </button>
              </div>
            </div>

            {groupsLoading ? (
              <div className="text-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">Loading groups...</p>
              </div>
            ) : groups.length === 0 ? (
              <EmptyState
                icon={FolderPlus}
                title="No Groups Yet"
                description="Create groups to organize jobs by company, role type, or any criteria you choose"
                action={{ label: 'Browse All Jobs', onClick: () => setView('all') }}
              />
            ) : (
              groups
                .filter(group => groupFilter === 'all' || group.group_type === groupFilter)
                .map((group) => {
                  const isCollapsed = collapsedGroups.has(group.id);
                  const groupJobs = jobs.filter((j) => group.job_ids.includes(j.id));
                  
                  return (
                    <div key={group.id} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                      <div 
                        className="p-6 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                        onClick={() => toggleGroupCollapse(group.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="flex items-center gap-2">
                              {isCollapsed ? (
                                <ChevronDown className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                              ) : (
                                <ChevronUp className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                              )}
                              <h3 className="font-semibold dark:text-white">
                                {group.name}
                              </h3>
                            </div>
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                              group.group_type === 'scraped' 
                                ? 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300'
                                : 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                            }`}>
                              {group.group_type === 'scraped' ? 'Scraped' : 'Custom'}
                            </span>
                          </div>
                          <div className="flex items-center gap-3">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={(e) => handleSelectAllInGroup(groupJobs.map(j => j.id), e)}
                              className="text-xs"
                            >
                              {groupJobs.every(j => selectedJobIds.includes(j.id)) ? (
                                <>
                                  <X className="w-3 h-3 mr-1" />
                                  Deselect All
                                </>
                              ) : (
                                <>
                                  <Check className="w-3 h-3 mr-1" />
                                  Select All
                                </>
                              )}
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                if (confirm(`Delete group "${group.name}"? Jobs will not be deleted.`)) {
                                  deleteJobGroupMutation.mutate(group.id);
                                }
                              }}
                              className="text-xs text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
                            >
                              <Trash2 className="w-3 h-3 mr-1" />
                              Delete
                            </Button>
                            <span className="text-sm text-gray-500 dark:text-gray-400">
                              {groupJobs.filter(j => selectedJobIds.includes(j.id)).length}/{groupJobs.length} selected
                            </span>
                          </div>
                        </div>
                        {group.description && (
                          <p className="text-sm text-gray-600 dark:text-gray-300 mt-2 ml-7">{group.description}</p>
                        )}
                      </div>
                      
                      {!isCollapsed && groupJobs.length > 0 && (
                        <div className="px-6 pb-6 space-y-2 border-t border-gray-100 dark:border-gray-700 pt-4">
                          {groupJobs.map((job) => (
                            <div onClick={(e) => e.stopPropagation()} key={job.id}>
                              <JobCard
                                job={job}
                                isSelected={selectedJobIds.includes(job.id)}
                                onToggle={() => handleToggleJob(job.id)}
                                onClick={() => setShowJobDetailModal(job)}
                              />
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })
            )}
          </div>
        )}

        {/* All Jobs View */}
        {view === 'all' && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {hasJobs && (
              <div className="flex items-center justify-between gap-4 mb-4">
                <div className="relative flex-1 max-w-[400px]">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
                  <Input
                    placeholder="Search jobs by title, company, or location..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                
                <div className="flex items-center gap-3">
                  <Select value={sortBy} onValueChange={(value) => setSortBy(value as SortBy)}>
                    <SelectTrigger className="w-[160px]">
                      <ArrowUpDown className="w-4 h-4 mr-2" />
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="created_date">Sort by Date</SelectItem>
                      <SelectItem value="company">Sort by Company</SelectItem>
                      <SelectItem value="location">Sort by Location</SelectItem>
                    </SelectContent>
                  </Select>

                  <div className="inline-flex rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-1">
                    <button
                      onClick={() => setAllViewMode('browse')}
                      className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                        allViewMode === 'browse'
                          ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                          : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                      }`}
                    >
                      Browse
                    </button>
                    <button
                      onClick={() => setAllViewMode('select')}
                      className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                        allViewMode === 'select'
                          ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                          : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                      }`}
                    >
                      Select & Group
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Loading State */}
            {jobsLoading && (
              <div className="text-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">Loading jobs...</p>
              </div>
            )}

            {/* Error State */}
            {jobsError && (
              <div className="text-center py-12">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <p className="text-red-600 mb-4">Failed to load jobs</p>
                <Button variant="outline" onClick={() => refetchJobs()}>
                  Try Again
                </Button>
              </div>
            )}

            {/* Empty State */}
            {!jobsLoading && !jobsError && !hasJobs && (
              <EmptyState
                icon={Briefcase}
                title="No Jobs in Your Library"
                description="Get started by adding jobs manually or using Discovery Mode to automatically find opportunities"
                action={{ label: 'Add Your First Job', onClick: () => setShowManualModal(true) }}
              />
            )}

            {/* No Search Results */}
            {!jobsLoading && !jobsError && hasJobs && filteredJobs.length === 0 && (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                <p className="text-gray-500 dark:text-gray-400">No jobs found matching your search.</p>
              </div>
            )}

            {/* Job List */}
            {!jobsLoading && !jobsError && filteredJobs.length > 0 && (
              <div className="grid grid-cols-1 gap-2">
                {filteredJobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    isSelected={selectedJobIds.includes(job.id)}
                    onToggle={() => handleToggleJob(job.id)}
                    onClick={() => setShowJobDetailModal(job)}
                    onDelete={() => handleDeleteJob(job)}
                    showCheckbox={allViewMode === 'select'}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modals */}
      {showManualModal && (
        <ManualJobModal
          onClose={() => setShowManualModal(false)}
        />
      )}
      
      {showScrapingModal && (
        <ScrapingConfigModal
          onClose={() => setShowScrapingModal(false)}
          onStart={handleScrapingStart}
        />
      )}

      {showJobDetailModal && (
        <JobDetailModal
          job={showJobDetailModal}
          onClose={() => setShowJobDetailModal(null)}
        />
      )}

      {showCreateGroupModal && (
        <CreateGroupModal
          selectedJobIds={selectedJobIds}
          onClose={() => setShowCreateGroupModal(false)}
        />
      )}
    </div>
  );
}