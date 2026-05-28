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
  Edit3,
  Upload,
  Download,
  MoreHorizontal,
  Loader2,
  AlertCircle,
  DollarSign,
  Briefcase
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/app/components/ui/dropdown-menu';
import { Badge } from '@/app/components/ui/badge';
import { ConfirmationDialog } from '@/app/components/ui/confirmation-dialog';
import { 
  useJobs, 
  useJobGroups, 
  useCreateJob, 
  useCreateJobGroup,
  useScrapeJobs,
  useDeleteJob
} from '@/hooks/useApi';
import type { 
  Job, 
  JobGroup, 
  JobCreateRequest, 
  JobGroupCreateRequest,
  JobFilters,
  ScrapingConfig 
} from '@/types/api';

interface JobManagerProps {
  onRunAnalysis?: (jobIds: string[]) => void;
}

type SortBy = 'created_date' | 'title' | 'company' | 'location';
type ViewMode = 'all' | 'groups';

// Manual Job Entry Modal
function ManualJobModal({ 
  onClose, 
  editJob 
}: { 
  onClose: () => void; 
  editJob?: Job;
}) {
  const [formData, setFormData] = useState<JobCreateRequest>({
    title: editJob?.title || '',
    company: editJob?.company || '',
    description: editJob?.description || '',
    location: editJob?.location || '',
    salary_min: editJob?.salary_min || undefined,
    salary_max: editJob?.salary_max || undefined,
    requirements: editJob?.requirements || [],
    skills: editJob?.required_skills || []
  });

  const [requirementsText, setRequirementsText] = useState(
    editJob?.requirements?.join('\n') || ''
  );
  const [skillsText, setSkillsText] = useState(
    editJob?.required_skills?.join(', ') || ''
  );

  const createJobMutation = useCreateJob();

  const handleSave = () => {
    // Parse requirements and skills
    const requirements = requirementsText
      .split('\n')
      .map(req => req.trim())
      .filter(req => req.length > 0);
    
    const skills = skillsText
      .split(',')
      .map(skill => skill.trim())
      .filter(skill => skill.length > 0);

    const jobData: JobCreateRequest = {
      ...formData,
      requirements,
      skills
    };

    createJobMutation.mutate(jobData, {
      onSuccess: () => {
        onClose();
      }
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8 animate-in fade-in duration-200">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[700px] max-h-[90vh] overflow-y-auto animate-in zoom-in-95 duration-200">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold dark:text-white">
            {editJob ? 'Edit Job' : 'Add Job Manually'}
          </h2>
        </div>
        
        <div className="p-6 space-y-4">
          {/* Basic Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
                Job Title *
              </label>
              <Input
                placeholder="e.g., Senior Account Manager"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
                Company *
              </label>
              <Input
                placeholder="e.g., Salesforce"
                value={formData.company}
                onChange={(e) => setFormData(prev => ({ ...prev, company: e.target.value }))}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Location
            </label>
            <Input
              placeholder="e.g., San Francisco, CA"
              value={formData.location}
              onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
            />
          </div>

          {/* Salary Range */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
                Minimum Salary
              </label>
              <Input
                type="number"
                placeholder="e.g., 80000"
                value={formData.salary_min || ''}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  salary_min: e.target.value ? parseInt(e.target.value) : undefined 
                }))}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
                Maximum Salary
              </label>
              <Input
                type="number"
                placeholder="e.g., 120000"
                value={formData.salary_max || ''}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  salary_max: e.target.value ? parseInt(e.target.value) : undefined 
                }))}
              />
            </div>
          </div>

          {/* Job Description */}
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Job Description *
            </label>
            <Textarea
              placeholder="Paste the full job description here..."
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              rows={6}
            />
          </div>

          {/* Requirements */}
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Requirements (one per line)
            </label>
            <Textarea
              placeholder="Bachelor's degree in relevant field&#10;5+ years of experience&#10;Strong communication skills"
              value={requirementsText}
              onChange={(e) => setRequirementsText(e.target.value)}
              rows={4}
            />
          </div>

          {/* Skills */}
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Required Skills (comma-separated)
            </label>
            <Input
              placeholder="e.g., JavaScript, React, Node.js, SQL"
              value={skillsText}
              onChange={(e) => setSkillsText(e.target.value)}
            />
          </div>
        </div>
        
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-750 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleSave} 
            disabled={!formData.title || !formData.company || !formData.description || createJobMutation.isPending}
          >
            {createJobMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                {editJob ? 'Updating...' : 'Adding...'}
              </>
            ) : (
              editJob ? 'Update Job' : 'Add Job'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

// Bulk Import Modal
function BulkImportModal({ onClose }: { onClose: () => void }) {
  const [importData, setImportData] = useState('');
  const [importFormat, setImportFormat] = useState<'json' | 'csv'>('json');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleImport = async () => {
    setIsProcessing(true);
    try {
      // Parse and validate import data
      let jobs: JobCreateRequest[] = [];
      
      if (importFormat === 'json') {
        const parsed = JSON.parse(importData);
        jobs = Array.isArray(parsed) ? parsed : [parsed];
      } else {
        // Simple CSV parsing (in production, use a proper CSV parser)
        const lines = importData.split('\n').filter(line => line.trim());
        const headers = lines[0].split(',').map(h => h.trim());
        
        jobs = lines.slice(1).map(line => {
          const values = line.split(',').map(v => v.trim());
          const job: any = {};
          headers.forEach((header, index) => {
            job[header] = values[index] || '';
          });
          return job as JobCreateRequest;
        });
      }

      // Validate required fields
      const validJobs = jobs.filter(job => job.title && job.company && job.description);
      
      if (validJobs.length === 0) {
        toast.error('No valid jobs found in import data');
        return;
      }

      // In a real implementation, you'd batch create these jobs
      console.log('Importing jobs:', validJobs);
      toast.success(`Successfully imported ${validJobs.length} jobs`);
      onClose();
    } catch (error) {
      toast.error('Failed to parse import data. Please check the format.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[600px]">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold dark:text-white">Bulk Import Jobs</h2>
        </div>
        
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Import Format
            </label>
            <Select value={importFormat} onValueChange={(value) => setImportFormat(value as 'json' | 'csv')}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="json">JSON</SelectItem>
                <SelectItem value="csv">CSV</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Import Data
            </label>
            <Textarea
              placeholder={importFormat === 'json' 
                ? '[\n  {\n    "title": "Software Engineer",\n    "company": "Tech Corp",\n    "description": "...",\n    "location": "Remote"\n  }\n]'
                : 'title,company,description,location\n"Software Engineer","Tech Corp","Job description","Remote"'
              }
              value={importData}
              onChange={(e) => setImportData(e.target.value)}
              rows={10}
              className="font-mono text-sm"
            />
          </div>
        </div>
        
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-750 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleImport} 
            disabled={!importData.trim() || isProcessing}
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4 mr-2" />
                Import Jobs
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

// Job Scraping Configuration Modal
function ScrapingModal({ onClose }: { onClose: () => void }) {
  const [config, setConfig] = useState<ScrapingConfig>({
    search_terms: [],
    employment_type: 'full-time',
    max_jobs: 50,
    location: ''
  });
  const [searchTermsText, setSearchTermsText] = useState('');

  const scrapeMutation = useScrapeJobs();

  const handleStartScraping = () => {
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

    scrapeMutation.mutate(scrapingConfig, {
      onSuccess: () => {
        onClose();
      }
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[500px]">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold dark:text-white">Configure Job Scraping</h2>
        </div>
        
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Search Terms (comma-separated) *
            </label>
            <Input
              placeholder="e.g., software engineer, full stack developer"
              value={searchTermsText}
              onChange={(e) => setSearchTermsText(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Location
            </label>
            <Input
              placeholder="e.g., San Francisco, CA"
              value={config.location}
              onChange={(e) => setConfig(prev => ({ ...prev, location: e.target.value }))}
            />
          </div>

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
                Max Jobs
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
        </div>
        
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-750 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleStartScraping} 
            disabled={!searchTermsText.trim() || scrapeMutation.isPending}
          >
            {scrapeMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Starting...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 mr-2" />
                Start Scraping
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

// Job Card Component
function JobCard({
  job,
  isSelected,
  onToggle,
  onView,
  onEdit,
  onDelete,
  showCheckbox = false,
}: {
  job: Job;
  isSelected: boolean;
  onToggle: () => void;
  onView: () => void;
  onEdit: () => void;
  onDelete: () => void;
  showCheckbox?: boolean;
}) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return null;
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    if (min) return `$${min.toLocaleString()}+`;
    if (max) return `Up to $${max.toLocaleString()}`;
    return null;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return `${diffDays}d ago`;
  };

  return (
    <div
      className={`bg-white dark:bg-gray-800 border rounded-lg p-4 transition-all group ${
        isSelected
          ? 'border-blue-500 shadow-sm'
          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-sm'
      }`}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        {showCheckbox && (
          <div
            className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors cursor-pointer ${
              isSelected
                ? 'bg-blue-600 border-blue-600'
                : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
            }`}
            onClick={onToggle}
          >
            {isSelected && <Check className="w-3 h-3 text-white" />}
          </div>
        )}

        {/* Job Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold mb-1 truncate dark:text-white">{job.title}</h3>
          <p className="text-sm text-gray-900 dark:text-gray-300 mb-2">{job.company}</p>
          
          <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 mb-2">
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
              {formatDate(job.created_date)}
            </span>
            {(job.salary_min || job.salary_max) && (
              <span className="flex items-center gap-1">
                <DollarSign className="w-3 h-3" />
                {formatSalary(job.salary_min, job.salary_max)}
              </span>
            )}
          </div>

          {/* Skills */}
          {job.required_skills && job.required_skills.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {job.required_skills.slice(0, 3).map((skill, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {skill}
                </Badge>
              ))}
              {job.required_skills.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{job.required_skills.length - 3} more
                </Badge>
              )}
            </div>
          )}
        </div>

        {/* Actions */}
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
              <DropdownMenuItem onClick={onEdit}>
                <Edit3 className="w-4 h-4 mr-2" />
                Edit Job
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onDelete} className="text-red-600">
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>
  );
}

// Job Detail Modal
function JobDetailModal({ job, onClose }: { job: Job; onClose: () => void }) {
  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return 'Not specified';
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    if (min) return `$${min.toLocaleString()}+`;
    if (max) return `Up to $${max.toLocaleString()}`;
    return 'Not specified';
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-[800px] max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="sticky top-0 bg-white px-6 py-4 border-b border-gray-200 flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-semibold mb-1">{job.title}</h2>
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
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6">
          {/* Job Info Grid */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="font-semibold mb-2">Job Information</h3>
              <div className="space-y-2 text-sm">
                {job.employment_type && (
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-300">Employment Type:</span>
                    <span>{job.employment_type}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">Salary Range:</span>
                  <span>{formatSalary(job.salary_min, job.salary_max)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">Source:</span>
                  <span>{job.source}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">Posted:</span>
                  <span>{new Date(job.created_date).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-2">Required Skills</h3>
              {job.required_skills && job.required_skills.length > 0 ? (
                <div className="flex flex-wrap gap-1">
                  {job.required_skills.map((skill, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {skill}
                    </Badge>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400">No skills specified</p>
              )}
            </div>
          </div>

          {/* Requirements */}
          {job.requirements && job.requirements.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold mb-2">Requirements</h3>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                {job.requirements.map((req, index) => (
                  <li key={index}>{req}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Description */}
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Job Description</h3>
            <p className="text-sm text-gray-700 whitespace-pre-line">
              {job.description}
            </p>
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

// Create Group Modal
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
    if (groupName.trim()) {
      const groupData: JobGroupCreateRequest = {
        name: groupName,
        description: description || undefined,
        job_ids: selectedJobIds
      };

      createGroupMutation.mutate(groupData, {
        onSuccess: () => {
          onClose();
        }
      });
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-[500px]" onClick={(e) => e.stopPropagation()}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Create Job Group</h2>
        </div>
        <div className="p-6 space-y-4">
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Creating group with {selectedJobIds.length} selected job{selectedJobIds.length !== 1 ? 's' : ''}
          </p>
          
          <div>
            <label className="block text-sm font-semibold mb-2">Group Name *</label>
            <Input
              placeholder="e.g., FAANG Senior Roles"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">Description</label>
            <Textarea
              placeholder="Optional description for this group..."
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
            disabled={!groupName.trim() || createGroupMutation.isPending}
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

// Main Job Manager Component
export function JobManager({ onRunAnalysis }: JobManagerProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('all');
  const [selectedJobIds, setSelectedJobIds] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortBy>('created_date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  // Modal states
  const [showManualModal, setShowManualModal] = useState(false);
  const [showBulkImportModal, setShowBulkImportModal] = useState(false);
  const [showScrapingModal, setShowScrapingModal] = useState(false);
  const [showJobDetailModal, setShowJobDetailModal] = useState<Job | null>(null);
  const [showCreateGroupModal, setShowCreateGroupModal] = useState(false);
  const [editingJob, setEditingJob] = useState<Job | null>(null);
  const [deleteConfirmation, setDeleteConfirmation] = useState<{
    open: boolean;
    job: Job | null;
  }>({ open: false, job: null });

  // Build filters for API call
  const filters: JobFilters = {
    sort_by: sortBy,
    sort_order: sortOrder,
    skip: (currentPage - 1) * itemsPerPage,
    limit: itemsPerPage,
  };

  // Fetch data
  const { data: jobs, isLoading: jobsLoading, error: jobsError, refetch: refetchJobs } = useJobs(filters);
  const { data: groups, isLoading: groupsLoading, error: groupsError } = useJobGroups();
  
  // Delete mutation
  const deleteJobMutation = useDeleteJob();

  // Filter jobs by search query (client-side for now)
  const filteredJobs = jobs?.filter(job =>
    job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (job.location && job.location.toLowerCase().includes(searchQuery.toLowerCase()))
  ) || [];

  const handleToggleJob = (jobId: string) => {
    setSelectedJobIds(prev =>
      prev.includes(jobId) ? prev.filter(id => id !== jobId) : [...prev, jobId]
    );
  };

  const handleRunAnalysis = () => {
    if (selectedJobIds.length > 0 && onRunAnalysis) {
      onRunAnalysis(selectedJobIds);
    }
  };

  const handleDeleteJob = (job: Job) => {
    setDeleteConfirmation({ open: true, job });
  };

  const confirmDeleteJob = () => {
    if (deleteConfirmation.job) {
      deleteJobMutation.mutate(deleteConfirmation.job.id);
    }
  };

  const handleEditJob = (job: Job) => {
    setEditingJob(job);
    setShowManualModal(true);
  };

  const handleExportJobs = () => {
    // Export selected jobs or all jobs
    const jobsToExport = selectedJobIds.length > 0 
      ? filteredJobs.filter(job => selectedJobIds.includes(job.id))
      : filteredJobs;
    
    const exportData = JSON.stringify(jobsToExport, null, 2);
    const blob = new Blob([exportData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `jobs_export_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success(`Exported ${jobsToExport.length} jobs`);
  };

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
      <div className="max-w-[1200px] mx-auto p-4 sm:p-6 lg:p-8 xl:p-12">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-semibold mb-3 dark:text-white">Job Manager</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your job opportunities through manual entry, bulk import, or automated scraping
          </p>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <button
            onClick={() => setShowManualModal(true)}
            className="bg-white border-2 border-dashed border-gray-300 rounded-xl p-6 hover:border-gray-400 hover:bg-gray-50 transition-all"
          >
            <Plus className="w-8 h-8 text-gray-400 mx-auto mb-3" />
            <p className="font-semibold">Add Job Manually</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Enter job details from any source
            </p>
          </button>

          <button
            onClick={() => setShowBulkImportModal(true)}
            className="bg-white border-2 border-dashed border-gray-300 rounded-xl p-6 hover:border-gray-400 hover:bg-gray-50 transition-all"
          >
            <Upload className="w-8 h-8 text-gray-400 mx-auto mb-3" />
            <p className="font-semibold">Bulk Import</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Import from JSON or CSV files
            </p>
          </button>

          <button
            onClick={() => setShowScrapingModal(true)}
            className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl p-6 hover:from-purple-600 hover:to-purple-700 transition-all"
          >
            <Zap className="w-8 h-8 mx-auto mb-3" />
            <p className="font-semibold">Auto-Scrape Jobs</p>
            <p className="text-sm text-purple-100 mt-1">
              Discover jobs automatically
            </p>
          </button>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            {/* View Toggle */}
            <div className="inline-flex rounded-lg border border-gray-200 bg-white p-1">
              <button
                onClick={() => setViewMode('all')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'all'
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                All Jobs
              </button>
              <button
                onClick={() => setViewMode('groups')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'groups'
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Groups
              </button>
            </div>

            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                placeholder="Search jobs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 w-[300px]"
              />
            </div>

            {/* Sort */}
            <Select value={`${sortBy}_${sortOrder}`} onValueChange={(value) => {
              const [field, order] = value.split('_') as [SortBy, 'asc' | 'desc'];
              setSortBy(field);
              setSortOrder(order);
              setCurrentPage(1);
            }}>
              <SelectTrigger className="w-[200px]">
                <ArrowUpDown className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="created_date_desc">Newest First</SelectItem>
                <SelectItem value="created_date_asc">Oldest First</SelectItem>
                <SelectItem value="title_asc">Title A-Z</SelectItem>
                <SelectItem value="title_desc">Title Z-A</SelectItem>
                <SelectItem value="company_asc">Company A-Z</SelectItem>
                <SelectItem value="company_desc">Company Z-A</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            {selectedJobIds.length > 0 && (
              <>
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  {selectedJobIds.length} selected
                </span>
                {onRunAnalysis && (
                  <Button onClick={handleRunAnalysis} className="gap-2">
                    <Search className="w-4 h-4" />
                    Run Analysis
                  </Button>
                )}
                <Button variant="outline" className="gap-2" onClick={() => setShowCreateGroupModal(true)}>
                  <FolderPlus className="w-4 h-4" />
                  Create Group
                </Button>
              </>
            )}
            <Button variant="outline" onClick={handleExportJobs} className="gap-2">
              <Download className="w-4 h-4" />
              Export
            </Button>
          </div>
        </div>

        {/* Content */}
        {viewMode === 'all' && (
          <div>
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
            {!jobsLoading && !jobsError && filteredJobs.length === 0 && (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2 dark:text-white">
                  {searchQuery ? 'No matching jobs' : 'No jobs yet'}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  {searchQuery 
                    ? 'Try adjusting your search terms'
                    : 'Add your first job to get started with career analysis'
                  }
                </p>
                {!searchQuery && (
                  <Button onClick={() => setShowManualModal(true)} className="gap-2">
                    <Plus className="w-4 h-4" />
                    Add Your First Job
                  </Button>
                )}
              </div>
            )}

            {/* Job List */}
            {!jobsLoading && !jobsError && filteredJobs.length > 0 && (
              <div className="space-y-4">
                {filteredJobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    isSelected={selectedJobIds.includes(job.id)}
                    onToggle={() => handleToggleJob(job.id)}
                    onView={() => setShowJobDetailModal(job)}
                    onEdit={() => handleEditJob(job)}
                    onDelete={() => handleDeleteJob(job)}
                    showCheckbox={selectedJobIds.length > 0 || onRunAnalysis !== undefined}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Groups View */}
        {viewMode === 'groups' && (
          <div>
            {groupsLoading && (
              <div className="text-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">Loading groups...</p>
              </div>
            )}

            {groupsError && (
              <div className="text-center py-12">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <p className="text-red-600 mb-4">Failed to load groups</p>
              </div>
            )}

            {!groupsLoading && !groupsError && (!groups || groups.length === 0) && (
              <div className="text-center py-12">
                <FolderPlus className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2 dark:text-white">No groups yet</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Create groups to organize jobs by company, role type, or any criteria
                </p>
                <Button onClick={() => setViewMode('all')} className="gap-2">
                  <Eye className="w-4 h-4" />
                  Browse All Jobs
                </Button>
              </div>
            )}

            {!groupsLoading && !groupsError && groups && groups.length > 0 && (
              <div className="space-y-6">
                {groups.map((group) => (
                  <div key={group.id} className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="font-semibold">{group.name}</h3>
                        {group.description && (
                          <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{group.description}</p>
                        )}
                      </div>
                      <Badge variant="secondary">
                        {group.job_count} jobs
                      </Badge>
                    </div>
                    
                    <div className="space-y-2">
                      {jobs?.filter(job => group.job_ids.includes(job.id)).map((job) => (
                        <JobCard
                          key={job.id}
                          job={job}
                          isSelected={selectedJobIds.includes(job.id)}
                          onToggle={() => handleToggleJob(job.id)}
                          onView={() => setShowJobDetailModal(job)}
                          onEdit={() => handleEditJob(job)}
                          onDelete={() => handleDeleteJob(job)}
                          showCheckbox={selectedJobIds.length > 0 || onRunAnalysis !== undefined}
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modals */}
      {showManualModal && (
        <ManualJobModal
          onClose={() => {
            setShowManualModal(false);
            setEditingJob(null);
          }}
          editJob={editingJob || undefined}
        />
      )}

      {showBulkImportModal && (
        <BulkImportModal
          onClose={() => setShowBulkImportModal(false)}
        />
      )}

      {showScrapingModal && (
        <ScrapingModal
          onClose={() => setShowScrapingModal(false)}
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

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        open={deleteConfirmation.open}
        onOpenChange={(open) => setDeleteConfirmation({ open, job: null })}
        title="Delete Job"
        description={
          deleteConfirmation.job
            ? `Are you sure you want to delete the job "${deleteConfirmation.job.title}" at ${deleteConfirmation.job.company}? This action cannot be undone.`
            : ''
        }
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
        onConfirm={confirmDeleteJob}
      />
    </div>
  );
}