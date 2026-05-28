import { useState } from 'react';
import { Plus, Search, FolderPlus, Check, MapPin, Calendar, Zap, X, Building2, FileText } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Textarea } from '@/app/components/ui/textarea';
import { Job } from '@/app/data/mockJobs';
import { JobGroup, ScraperSession } from '@/app/data/sessionData';

interface JobHubProps {
  jobs: Job[];
  groups: JobGroup[];
  scraperSessions: ScraperSession[];
  onStartScraper: () => void;
  onRunAnalysis: (jobIds: string[]) => void;
}

function ManualJobModal({ onClose, onSave }: { onClose: () => void; onSave: (job: Partial<Job>) => void }) {
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [location, setLocation] = useState('');
  const [description, setDescription] = useState('');

  const handleSave = () => {
    onSave({ title, company, location, description });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-[600px]">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Add Job Manually</h2>
        </div>
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2">Job Title</label>
            <Input
              placeholder="e.g., Senior Account Manager"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2">Company</label>
            <Input
              placeholder="e.g., Salesforce"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2">Location</label>
            <Input
              placeholder="e.g., San Francisco, CA"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2">Job Description</label>
            <Textarea
              placeholder="Paste the full job description here..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={6}
            />
          </div>
        </div>
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave}>Add Job</Button>
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
  showCheckbox = true,
}: {
  job: Job;
  isSelected: boolean;
  onToggle: () => void;
  onClick?: () => void;
  showCheckbox?: boolean;
}) {
  const handleClick = (e: React.MouseEvent) => {
    if (showCheckbox) {
      onToggle();
    } else if (onClick) {
      onClick();
    }
  };

  return (
    <div
      className={`bg-white border rounded-lg p-4 transition-all cursor-pointer ${
        isSelected
          ? 'border-blue-500 shadow-sm'
          : 'border-gray-200 hover:border-gray-300'
      }`}
      onClick={handleClick}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        {showCheckbox && (
          <div
            className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
              isSelected
                ? 'bg-blue-600 border-blue-600'
                : 'border-gray-300'
            }`}
          >
            {isSelected && <Check className="w-3 h-3 text-white" />}
          </div>
        )}

        {/* Job Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold mb-1 truncate">{job.title}</h3>
          <p className="text-sm text-gray-900 mb-2">{job.company}</p>
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <MapPin className="w-3 h-3" />
              {job.location}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {job.postedDays}d ago
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function ScraperSessionCard({
  session,
  jobs,
  onExpand,
}: {
  session: ScraperSession;
  jobs: Job[];
  onExpand: () => void;
}) {
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <button
      onClick={onExpand}
      className="w-full bg-white border border-gray-200 rounded-lg p-4 hover:border-gray-300 hover:shadow-sm transition-all text-left"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1">
          <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
            <Zap className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="font-semibold mb-1">
              Scrape: {session.searchQuery}
            </h3>
            <p className="text-sm text-gray-600 mb-2">
              {session.jobsFound} roles found • {formatDate(session.createdAt)}
            </p>
            <div className="text-xs text-gray-500">
              Level: <span className="font-medium">{session.jobLevel}</span>
            </div>
          </div>
        </div>
      </div>
    </button>
  );
}

function JobDetailModal({ job, onClose }: { job: Job; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-[800px] max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="sticky top-0 bg-white px-6 py-4 border-b border-gray-200 flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-semibold mb-1">{job.title}</h2>
            <div className="flex items-center gap-3 text-sm text-gray-600">
              <span className="flex items-center gap-1">
                <Building2 className="w-4 h-4" />
                {job.company}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                {job.location}
              </span>
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
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Job Description</h3>
            <p className="text-sm text-gray-700 whitespace-pre-line">
              {job.description || 'No description available.'}
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Calendar className="w-4 h-4" />
            <span>Posted {job.postedDays} days ago</span>
          </div>
        </div>
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end gap-3">
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
  onClose, 
  onSave 
}: { 
  selectedJobIds: string[]; 
  onClose: () => void; 
  onSave: (name: string) => void;
}) {
  const [groupName, setGroupName] = useState('');

  const handleSave = () => {
    if (groupName.trim()) {
      onSave(groupName);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-[500px]" onClick={(e) => e.stopPropagation()}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Create Custom Group</h2>
        </div>
        <div className="p-6">
          <p className="text-sm text-gray-600 mb-4">
            Creating group with {selectedJobIds.length} selected job{selectedJobIds.length !== 1 ? 's' : ''}
          </p>
          <div>
            <label className="block text-sm font-semibold mb-2">Group Name</label>
            <Input
              placeholder="e.g., FAANG Senior Roles"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              autoFocus
            />
          </div>
        </div>
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!groupName.trim()}>
            Create Group
          </Button>
        </div>
      </div>
    </div>
  );
}

export function JobHub({
  jobs,
  groups,
  scraperSessions,
  onStartScraper,
  onRunAnalysis,
}: JobHubProps) {
  const [mode, setMode] = useState<'scraper' | 'manual' | null>(null);
  const [view, setView] = useState<'sessions' | 'groups' | 'all'>('sessions');
  const [selectedJobIds, setSelectedJobIds] = useState<string[]>([]);
  const [showManualModal, setShowManualModal] = useState(false);
  const [expandedSessionId, setExpandedSessionId] = useState<string | null>(null);
  const [showJobDetailModal, setShowJobDetailModal] = useState<Job | null>(null);
  const [showCreateGroupModal, setShowCreateGroupModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [allViewMode, setAllViewMode] = useState<'browse' | 'select'>('browse');

  const handleToggleJob = (jobId: string) => {
    setSelectedJobIds((prev) =>
      prev.includes(jobId) ? prev.filter((id) => id !== jobId) : [...prev, jobId]
    );
  };

  const handleSaveManualJob = (job: Partial<Job>) => {
    console.log('Saving manual job:', job);
    // Would save to state/database
  };

  const handleRunAnalysis = () => {
    if (selectedJobIds.length > 0) {
      onRunAnalysis(selectedJobIds);
    }
  };

  const displayJobs = expandedSessionId
    ? jobs.filter((job) =>
        scraperSessions
          .find((s) => s.id === expandedSessionId)
          ?.jobIds.includes(job.id)
      )
    : jobs;

  // Filter jobs based on search query
  const filteredJobs = jobs.filter((job) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      job.title.toLowerCase().includes(query) ||
      job.company.toLowerCase().includes(query) ||
      job.location.toLowerCase().includes(query)
    );
  });

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
      <div className="max-w-[1200px] mx-auto p-4 sm:p-6 lg:p-8 xl:p-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-semibold mb-3">Job Hub</h1>
          <p className="text-gray-600">
            Build your job library through manual entry or automated discovery
          </p>
        </div>

        {/* Input Header - Two-Way Entry */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <button
            onClick={() => setShowManualModal(true)}
            className="bg-white border-2 border-dashed border-gray-300 rounded-xl p-6 hover:border-gray-400 hover:bg-gray-50 transition-all"
          >
            <Plus className="w-8 h-8 text-gray-400 mx-auto mb-3" />
            <p className="font-semibold">Add Job Manually</p>
            <p className="text-sm text-gray-500 mt-1">
              Paste job details from any source
            </p>
          </button>

          <button
            onClick={onStartScraper}
            className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl p-6 hover:from-purple-600 hover:to-purple-700 transition-all"
          >
            <Zap className="w-8 h-8 mx-auto mb-3" />
            <p className="font-semibold">Activate Discovery Mode</p>
            <p className="text-sm text-purple-100 mt-1">
              Auto-scrape matching positions
            </p>
          </button>
        </div>

        {/* View Switcher */}
        <div className="flex items-center justify-between mb-6">
          <div className="inline-flex rounded-lg border border-gray-200 bg-white p-1">
            <button
              onClick={() => setView('sessions')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                view === 'sessions'
                  ? 'bg-gray-100 text-gray-900'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Scraper Sessions
            </button>
            <button
              onClick={() => setView('groups')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                view === 'groups'
                  ? 'bg-gray-100 text-gray-900'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Custom Groups
            </button>
            <button
              onClick={() => setView('all')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                view === 'all'
                  ? 'bg-gray-100 text-gray-900'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              All Jobs
            </button>
          </div>

          {selectedJobIds.length > 0 && (
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">
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

        {/* Sessions View */}
        {view === 'sessions' && (
          <div className="space-y-6">
            {scraperSessions.map((session) => (
              <div key={session.id}>
                <ScraperSessionCard
                  session={session}
                  jobs={jobs.filter((j) => session.jobIds.includes(j.id))}
                  onExpand={() =>
                    setExpandedSessionId(
                      expandedSessionId === session.id ? null : session.id
                    )
                  }
                />
                {expandedSessionId === session.id && (
                  <div className="mt-3 ml-14 space-y-2">
                    {jobs
                      .filter((j) => session.jobIds.includes(j.id))
                      .map((job) => (
                        <JobCard
                          key={job.id}
                          job={job}
                          isSelected={selectedJobIds.includes(job.id)}
                          onToggle={() => handleToggleJob(job.id)}
                          onClick={() => setShowJobDetailModal(job)}
                        />
                      ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Groups View */}
        {view === 'groups' && (
          <div className="space-y-6">
            {groups.map((group) => (
              <div key={group.id} className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="font-semibold mb-4">
                  {group.name}{' '}
                  <span className="text-sm font-normal text-gray-500">
                    ({group.jobIds.length} jobs)
                  </span>
                </h3>
                <div className="space-y-2">
                  {jobs
                    .filter((j) => group.jobIds.includes(j.id))
                    .map((job) => (
                      <JobCard
                        key={job.id}
                        job={job}
                        isSelected={selectedJobIds.includes(job.id)}
                        onToggle={() => handleToggleJob(job.id)}
                        onClick={() => setShowJobDetailModal(job)}
                      />
                    ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* All Jobs View */}
        {view === 'all' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-4">
              <div className="relative w-full max-w-[400px]">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="Search jobs by title, company, or location..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="inline-flex rounded-lg border border-gray-200 bg-white p-1">
                <button
                  onClick={() => setAllViewMode('browse')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    allViewMode === 'browse'
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Browse
                </button>
                <button
                  onClick={() => setAllViewMode('select')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    allViewMode === 'select'
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Select & Group
                </button>
              </div>
            </div>
            <div className="grid grid-cols-1 gap-2">
              {filteredJobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  isSelected={selectedJobIds.includes(job.id)}
                  onToggle={() => handleToggleJob(job.id)}
                  onClick={() => setShowJobDetailModal(job)}
                  showCheckbox={allViewMode === 'select'}
                />
              ))}
            </div>
            {filteredJobs.length === 0 && (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No jobs found matching your search.</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Manual Job Modal */}
      {showManualModal && (
        <ManualJobModal
          onClose={() => setShowManualModal(false)}
          onSave={handleSaveManualJob}
        />
      )}

      {/* Job Detail Modal */}
      {showJobDetailModal && (
        <JobDetailModal
          job={showJobDetailModal}
          onClose={() => setShowJobDetailModal(null)}
        />
      )}

      {/* Create Group Modal */}
      {showCreateGroupModal && (
        <CreateGroupModal
          selectedJobIds={selectedJobIds}
          onClose={() => setShowCreateGroupModal(false)}
          onSave={(name) => {
            // Handle saving the group
            console.log('Creating group:', name);
          }}
        />
      )}
    </div>
  );
}