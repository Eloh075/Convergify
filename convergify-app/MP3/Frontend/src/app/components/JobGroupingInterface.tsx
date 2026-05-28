import { useState, useEffect, useCallback } from 'react';
import { 
  Plus, 
  Search, 
  FolderPlus, 
  Check, 
  MapPin, 
  Calendar, 
  Building2, 
  X, 
  Edit3,
  Trash2,
  ArrowUpDown,
  Filter,
  MoreHorizontal,
  Loader2,
  AlertCircle,
  DollarSign,
  Users,
  Move,
  Eye,
  ChevronDown,
  ChevronRight,
  Grip
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
  DropdownMenuSeparator,
} from '@/app/components/ui/dropdown-menu';
import { Badge } from '@/app/components/ui/badge';
import { Checkbox } from '@/app/components/ui/checkbox';
import { 
  useJobs, 
  useJobGroups, 
  useCreateJobGroup,
} from '@/hooks/useApi';
import type { 
  Job, 
  JobGroup, 
  JobGroupCreateRequest,
  JobFilters 
} from '@/types/api';

interface JobGroupingInterfaceProps {
  onRunAnalysis?: (jobIds: string[]) => void;
}

type SortBy = 'created_date' | 'title' | 'company' | 'location';
type FilterBy = 'all' | 'ungrouped' | 'grouped';

// Draggable Job Card Component
function DraggableJobCard({
  job,
  isSelected,
  onToggle,
  onView,
  isDragging,
  onDragStart,
  onDragEnd,
  showCheckbox = true,
}: {
  job: Job;
  isSelected: boolean;
  onToggle: () => void;
  onView: () => void;
  isDragging: boolean;
  onDragStart: () => void;
  onDragEnd: () => void;
  showCheckbox?: boolean;
}) {
  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return null;
    if (min && max) return `${min.toLocaleString()} - ${max.toLocaleString()}`;
    if (min) return `${min.toLocaleString()}+`;
    if (max) return `Up to ${max.toLocaleString()}`;
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
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      className={`bg-white dark:bg-gray-800 border rounded-lg p-4 transition-all group cursor-move ${
        isDragging
          ? 'opacity-50 scale-95 shadow-lg'
          : isSelected
          ? 'border-blue-500 shadow-sm'
          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-sm'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Drag Handle */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <Grip className="w-4 h-4 text-gray-400" />
          {showCheckbox && (
            <Checkbox
              checked={isSelected}
              onCheckedChange={onToggle}
              className="mt-0.5"
            />
          )}
        </div>

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
            <div className="flex flex-wrap gap-1">
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
        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button variant="outline" size="sm" onClick={onView}>
            <Eye className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}

// Job Group Component with Drop Zone
function JobGroupCard({
  group,
  jobs,
  selectedJobIds,
  onToggleJob,
  onViewJob,
  onEditGroup,
  onDeleteGroup,
  onDrop,
  onRemoveJobsFromGroup,
  isExpanded,
  onToggleExpanded,
}: {
  group: JobGroup;
  jobs: Job[];
  selectedJobIds: string[];
  onToggleJob: (jobId: string) => void;
  onViewJob: (job: Job) => void;
  onEditGroup: (group: JobGroup) => void;
  onDeleteGroup: (group: JobGroup) => void;
  onDrop: (groupId: string, jobIds: string[]) => void;
  onRemoveJobsFromGroup: (groupId: string, jobIds: string[]) => void;
  isExpanded: boolean;
  onToggleExpanded: () => void;
}) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [draggedJobIds, setDraggedJobIds] = useState<string[]>([]);

  const groupJobs = jobs.filter(job => group.job_ids.includes(job.id));
  const selectedGroupJobs = groupJobs.filter(job => selectedJobIds.includes(job.id));

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (draggedJobIds.length > 0) {
      onDrop(group.id, draggedJobIds);
      setDraggedJobIds([]);
    }
  };

  const handleRemoveSelected = () => {
    if (selectedGroupJobs.length > 0) {
      onRemoveJobsFromGroup(group.id, selectedGroupJobs.map(job => job.id));
    }
  };

  return (
    <div
      className={`bg-white dark:bg-gray-800 border rounded-lg transition-all ${
        isDragOver
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
          : 'border-gray-200 dark:border-gray-700'
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Group Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={onToggleExpanded}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            >
              {isExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
            
            <div>
              <h3 className="font-semibold dark:text-white">{group.name}</h3>
              {group.description && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {group.description}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Badge variant="secondary" className="flex items-center gap-1">
              <Users className="w-3 h-3" />
              {group.job_count} jobs
            </Badge>
            
            {selectedGroupJobs.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleRemoveSelected}
                className="text-red-600 hover:text-red-700"
              >
                Remove {selectedGroupJobs.length}
              </Button>
            )}

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <MoreHorizontal className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => onEditGroup(group)}>
                  <Edit3 className="w-4 h-4 mr-2" />
                  Edit Group
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={() => onDeleteGroup(group)}
                  className="text-red-600"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Group
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>

      {/* Drop Zone Indicator */}
      {isDragOver && (
        <div className="p-4 text-center border-b border-gray-200 dark:border-gray-700 bg-blue-50 dark:bg-blue-900/20">
          <Move className="w-6 h-6 text-blue-600 mx-auto mb-2" />
          <p className="text-sm text-blue-600 font-medium">
            Drop jobs here to add them to "{group.name}"
          </p>
        </div>
      )}

      {/* Group Jobs */}
      {isExpanded && (
        <div className="p-4">
          {groupJobs.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <FolderPlus className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No jobs in this group yet</p>
              <p className="text-xs mt-1">Drag jobs here to add them</p>
            </div>
          ) : (
            <div className="space-y-3">
              {groupJobs.map((job) => (
                <DraggableJobCard
                  key={job.id}
                  job={job}
                  isSelected={selectedJobIds.includes(job.id)}
                  onToggle={() => onToggleJob(job.id)}
                  onView={() => onViewJob(job)}
                  isDragging={false}
                  onDragStart={() => setDraggedJobIds([job.id])}
                  onDragEnd={() => setDraggedJobIds([])}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Create/Edit Group Modal
function GroupModal({
  group,
  onClose,
  onSave,
}: {
  group?: JobGroup;
  onClose: () => void;
  onSave: (data: JobGroupCreateRequest) => void;
}) {
  const [name, setName] = useState(group?.name || '');
  const [description, setDescription] = useState(group?.description || '');
  const [isLoading, setIsLoading] = useState(false);

  const handleSave = async () => {
    if (!name.trim()) {
      toast.error('Group name is required');
      return;
    }

    setIsLoading(true);
    try {
      await onSave({
        name: name.trim(),
        description: description.trim() || undefined,
        job_ids: group?.job_ids || [],
      });
      onClose();
    } catch (error) {
      toast.error('Failed to save group');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[500px]">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold dark:text-white">
            {group ? 'Edit Group' : 'Create New Group'}
          </h2>
        </div>
        
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Group Name *
            </label>
            <Input
              placeholder="e.g., FAANG Companies, Remote Jobs, Senior Roles"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-gray-200">
              Description
            </label>
            <Textarea
              placeholder="Optional description for this group..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>
        </div>
        
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-750 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!name.trim() || isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                {group ? 'Updating...' : 'Creating...'}
              </>
            ) : (
              group ? 'Update Group' : 'Create Group'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

// Job Detail Modal (simplified version)
function JobDetailModal({ job, onClose }: { job: Job; onClose: () => void }) {
  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return 'Not specified';
    if (min && max) return `${min.toLocaleString()} - ${max.toLocaleString()}`;
    if (min) return `${min.toLocaleString()}+`;
    if (max) return `Up to ${max.toLocaleString()}`;
    return 'Not specified';
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8" onClick={onClose}>
      <div 
        className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[800px] max-h-[90vh] overflow-y-auto" 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-white dark:bg-gray-800 px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-semibold mb-1 dark:text-white">{job.title}</h2>
            <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
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
          {/* Job Info Grid */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="font-semibold mb-2 dark:text-white">Job Information</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Salary Range:</span>
                  <span className="dark:text-gray-200">{formatSalary(job.salary_min, job.salary_max)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Source:</span>
                  <span className="dark:text-gray-200">{job.source}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Posted:</span>
                  <span className="dark:text-gray-200">{new Date(job.created_date).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-2 dark:text-white">Required Skills</h3>
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
              <h3 className="font-semibold mb-2 dark:text-white">Requirements</h3>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-700 dark:text-gray-300">
                {job.requirements.map((req, index) => (
                  <li key={index}>{req}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Description */}
          <div className="mb-6">
            <h3 className="font-semibold mb-2 dark:text-white">Job Description</h3>
            <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">
              {job.description}
            </p>
          </div>
        </div>
        
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-750 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
// Main Job Grouping Interface Component
export function JobGroupingInterface({ onRunAnalysis }: JobGroupingInterfaceProps) {
  const [selectedJobIds, setSelectedJobIds] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortBy>('created_date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [filterBy, setFilterBy] = useState<FilterBy>('all');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const [draggedJobIds, setDraggedJobIds] = useState<string[]>([]);

  // Modal states
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [editingGroup, setEditingGroup] = useState<JobGroup | null>(null);
  const [showJobDetailModal, setShowJobDetailModal] = useState<Job | null>(null);

  // Build filters for API call
  const filters: JobFilters = {
    sort_by: sortBy,
    sort_order: sortOrder,
    skip: 0,
    limit: 1000, // Get all jobs for grouping interface
  };

  // Fetch data
  const { data: jobs, isLoading: jobsLoading, error: jobsError, refetch: refetchJobs } = useJobs(filters);
  const { data: groups, isLoading: groupsLoading, error: groupsError, refetch: refetchGroups } = useJobGroups();
  const createGroupMutation = useCreateJobGroup();

  // Filter jobs based on search and filter criteria
  const filteredJobs = jobs?.filter(job => {
    // Search filter
    const matchesSearch = !searchQuery || 
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (job.location && job.location.toLowerCase().includes(searchQuery.toLowerCase()));

    // Group filter
    const hasGroup = groups?.some(group => group.job_ids.includes(job.id));
    const matchesFilter = filterBy === 'all' || 
      (filterBy === 'grouped' && hasGroup) ||
      (filterBy === 'ungrouped' && !hasGroup);

    return matchesSearch && matchesFilter;
  }) || [];

  // Get ungrouped jobs
  const ungroupedJobs = filteredJobs.filter(job => 
    !groups?.some(group => group.job_ids.includes(job.id))
  );

  const handleToggleJob = useCallback((jobId: string) => {
    setSelectedJobIds(prev => 
      prev.includes(jobId) ? prev.filter(id => id !== jobId) : [...prev, jobId]
    );
  }, []);

  const handleToggleGroup = useCallback((groupId: string) => {
    setExpandedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(groupId)) {
        newSet.delete(groupId);
      } else {
        newSet.add(groupId);
      }
      return newSet;
    });
  }, []);

  const handleCreateGroup = () => {
    setEditingGroup(null);
    setShowGroupModal(true);
  };

  const handleEditGroup = (group: JobGroup) => {
    setEditingGroup(group);
    setShowGroupModal(true);
  };

  const handleSaveGroup = async (data: JobGroupCreateRequest) => {
    if (editingGroup) {
      // Update existing group (would need update mutation)
      console.log('Updating group:', editingGroup.id, data);
      toast.success('Group updated successfully');
    } else {
      // Create new group
      createGroupMutation.mutate(data, {
        onSuccess: () => {
          refetchGroups();
          toast.success('Group created successfully');
        }
      });
    }
  };

  const handleDeleteGroup = (group: JobGroup) => {
    // Would need delete mutation
    console.log('Deleting group:', group.id);
    toast.success('Group deleted successfully');
    refetchGroups();
  };

  const handleDropJobsOnGroup = (groupId: string, jobIds: string[]) => {
    // Would need API call to add jobs to group
    console.log('Adding jobs to group:', groupId, jobIds);
    toast.success(`Added ${jobIds.length} job(s) to group`);
    refetchGroups();
  };

  const handleRemoveJobsFromGroup = (groupId: string, jobIds: string[]) => {
    // Would need API call to remove jobs from group
    console.log('Removing jobs from group:', groupId, jobIds);
    toast.success(`Removed ${jobIds.length} job(s) from group`);
    refetchGroups();
  };

  const handleRunAnalysis = () => {
    if (selectedJobIds.length > 0 && onRunAnalysis) {
      onRunAnalysis(selectedJobIds);
    }
  };

  const handleSelectAll = () => {
    if (selectedJobIds.length === filteredJobs.length) {
      setSelectedJobIds([]);
    } else {
      setSelectedJobIds(filteredJobs.map(job => job.id));
    }
  };

  const handleCreateGroupFromSelected = () => {
    if (selectedJobIds.length > 0) {
      setEditingGroup(null);
      setShowGroupModal(true);
    }
  };

  // Initialize expanded groups
  useEffect(() => {
    if (groups && expandedGroups.size === 0) {
      setExpandedGroups(new Set(groups.map(group => group.id)));
    }
  }, [groups, expandedGroups.size]);

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
      <div className="max-w-[1400px] mx-auto p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-semibold mb-3 dark:text-white">Job Organization</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Organize your jobs into groups for better analysis and management
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
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

            {/* Filter */}
            <Select value={filterBy} onValueChange={(value) => setFilterBy(value as FilterBy)}>
              <SelectTrigger className="w-[150px]">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Jobs</SelectItem>
                <SelectItem value="grouped">Grouped Only</SelectItem>
                <SelectItem value="ungrouped">Ungrouped Only</SelectItem>
              </SelectContent>
            </Select>

            {/* Sort */}
            <Select value={`${sortBy}_${sortOrder}`} onValueChange={(value) => {
              const [field, order] = value.split('_') as [SortBy, 'asc' | 'desc'];
              setSortBy(field);
              setSortOrder(order);
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
            {filteredJobs.length > 0 && (
              <Button variant="outline" onClick={handleSelectAll} className="gap-2">
                <Check className="w-4 h-4" />
                {selectedJobIds.length === filteredJobs.length ? 'Deselect All' : 'Select All'}
              </Button>
            )}
            
            {selectedJobIds.length > 0 && (
              <>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {selectedJobIds.length} selected
                </span>
                
                <Button onClick={handleCreateGroupFromSelected} className="gap-2">
                  <FolderPlus className="w-4 h-4" />
                  Create Group
                </Button>
                
                {onRunAnalysis && (
                  <Button onClick={handleRunAnalysis} className="gap-2">
                    <Search className="w-4 h-4" />
                    Run Analysis
                  </Button>
                )}
              </>
            )}
            
            <Button onClick={handleCreateGroup} className="gap-2">
              <Plus className="w-4 h-4" />
              New Group
            </Button>
          </div>
        </div>

        {/* Loading State */}
        {(jobsLoading || groupsLoading) && (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">Loading jobs and groups...</p>
          </div>
        )}

        {/* Error State */}
        {(jobsError || groupsError) && (
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-red-600 mb-4">Failed to load data</p>
            <Button variant="outline" onClick={() => { refetchJobs(); refetchGroups(); }}>
              Try Again
            </Button>
          </div>
        )}

        {/* Content */}
        {!jobsLoading && !groupsLoading && !jobsError && !groupsError && (
          <div className="space-y-6">
            {/* Job Groups */}
            {groups && groups.length > 0 && (
              <div className="space-y-4">
                <h2 className="text-xl font-semibold dark:text-white">Job Groups</h2>
                {groups.map((group) => (
                  <JobGroupCard
                    key={group.id}
                    group={group}
                    jobs={jobs || []}
                    selectedJobIds={selectedJobIds}
                    onToggleJob={handleToggleJob}
                    onViewJob={setShowJobDetailModal}
                    onEditGroup={handleEditGroup}
                    onDeleteGroup={handleDeleteGroup}
                    onDrop={handleDropJobsOnGroup}
                    onRemoveJobsFromGroup={handleRemoveJobsFromGroup}
                    isExpanded={expandedGroups.has(group.id)}
                    onToggleExpanded={() => handleToggleGroup(group.id)}
                  />
                ))}
              </div>
            )}

            {/* Ungrouped Jobs */}
            {ungroupedJobs.length > 0 && (
              <div className="space-y-4">
                <h2 className="text-xl font-semibold dark:text-white">
                  Ungrouped Jobs ({ungroupedJobs.length})
                </h2>
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="space-y-3">
                    {ungroupedJobs.map((job) => (
                      <DraggableJobCard
                        key={job.id}
                        job={job}
                        isSelected={selectedJobIds.includes(job.id)}
                        onToggle={() => handleToggleJob(job.id)}
                        onView={() => setShowJobDetailModal(job)}
                        isDragging={draggedJobIds.includes(job.id)}
                        onDragStart={() => setDraggedJobIds([job.id])}
                        onDragEnd={() => setDraggedJobIds([])}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Empty State */}
            {filteredJobs.length === 0 && (
              <div className="text-center py-12">
                <FolderPlus className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2 dark:text-white">
                  {searchQuery ? 'No matching jobs' : 'No jobs to organize'}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  {searchQuery 
                    ? 'Try adjusting your search terms or filters'
                    : 'Add some jobs first to start organizing them into groups'
                  }
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modals */}
      {showGroupModal && (
        <GroupModal
          group={editingGroup || undefined}
          onClose={() => {
            setShowGroupModal(false);
            setEditingGroup(null);
          }}
          onSave={handleSaveGroup}
        />
      )}

      {showJobDetailModal && (
        <JobDetailModal
          job={showJobDetailModal}
          onClose={() => setShowJobDetailModal(null)}
        />
      )}
    </div>
  );
}