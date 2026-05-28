import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/dropdown-menu';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Separator } from './ui/separator';
import { 
  Plus, 
  Play, 
  Pause, 
  Archive, 
  RotateCcw, 
  Trash2, 
  MoreVertical,
  Clock,
  FileText,
  Briefcase,
  BarChart3,
  Tag,
  Calendar
} from 'lucide-react';
import { useApi } from '../../hooks/useApi';
import { SessionDetails, SessionCreateRequest } from '../../types/api';

interface SessionManagerProps {
  onSessionSelect?: (sessionId: string) => void;
  selectedSessionId?: string;
}

export const SessionManager: React.FC<SessionManagerProps> = ({
  onSessionSelect,
  selectedSessionId
}) => {
  const [activeTab, setActiveTab] = useState('active');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedSession, setSelectedSession] = useState<SessionDetails | null>(null);
  const [isDetailsDialogOpen, setIsDetailsDialogOpen] = useState(false);

  // API hooks
  const { 
    data: sessions, 
    isLoading: isLoadingSessions, 
    refetch: refetchSessions 
  } = useApi.sessions.list({
    status: activeTab === 'all' ? undefined : activeTab
  });

  const { 
    data: sessionStats
  } = useApi.sessions.getStats();

  const createSessionMutation = useApi.sessions.create();
  const deleteSessionMutation = useApi.sessions.delete();
  const completeSessionMutation = useApi.sessions.complete();
  const archiveSessionMutation = useApi.sessions.archive();
  const restoreSessionMutation = useApi.sessions.restore();

  // Create session form state
  const [createForm, setCreateForm] = useState<SessionCreateRequest>({
    title: '',
    session_type: 'comprehensive',
    description: '',
    tags: []
  });

  const handleCreateSession = async () => {
    try {
      await createSessionMutation.mutateAsync(createForm);
      setIsCreateDialogOpen(false);
      setCreateForm({
        title: '',
        session_type: 'comprehensive',
        description: '',
        tags: []
      });
      refetchSessions();
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const handleSessionAction = async (sessionId: string, action: string) => {
    try {
      switch (action) {
        case 'complete':
          await completeSessionMutation.mutateAsync({ id: sessionId });
          break;
        case 'archive':
          await archiveSessionMutation.mutateAsync(sessionId);
          break;
        case 'restore':
          await restoreSessionMutation.mutateAsync(sessionId);
          break;
        case 'delete':
          await deleteSessionMutation.mutateAsync(sessionId);
          break;
      }
      refetchSessions();
    } catch (error) {
      console.error(`Failed to ${action} session:`, error);
    }
  };

  const handleViewDetails = async (sessionId: string) => {
    try {
      const details = await useApi.sessions.getDetails(sessionId);
      setSelectedSession(details);
      setIsDetailsDialogOpen(true);
    } catch (error) {
      console.error('Failed to fetch session details:', error);
    }
  };

  const formatDuration = (duration: string | null) => {
    if (!duration) return 'Ongoing';
    return duration;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      case 'archived': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSessionTypeIcon = (type: string) => {
    switch (type) {
      case 'comprehensive': return <BarChart3 className="h-4 w-4" />;
      case 'single_job': return <Briefcase className="h-4 w-4" />;
      case 'market_analysis': return <BarChart3 className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <div className="flex-1 h-full overflow-y-auto bg-gray-50 dark:bg-gray-900 transition-colors">
      <div className="max-w-[1200px] mx-auto p-4 sm:p-6 lg:p-8 xl:p-12 space-y-6">
        {/* Header with stats */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">Session Management</h2>
            <p className="text-muted-foreground">Manage your analysis sessions and track progress</p>
          </div>
          
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Session
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Session</DialogTitle>
                <DialogDescription>
                  Start a new analysis session to organize your career analysis workflow.
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Title</label>
                  <Input
                    value={createForm.title}
                    onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                    placeholder="Enter session title"
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium">Session Type</label>
                  <Select
                    value={createForm.session_type}
                    onValueChange={(value: 'comprehensive' | 'single_job' | 'market_analysis') => 
                      setCreateForm({ ...createForm, session_type: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="comprehensive">Comprehensive Analysis</SelectItem>
                      <SelectItem value="single_job">Single Job Analysis</SelectItem>
                      <SelectItem value="market_analysis">Market Analysis</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="text-sm font-medium">Description</label>
                  <Textarea
                    value={createForm.description}
                    onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                    placeholder="Optional description"
                    rows={3}
                  />
                </div>
                
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button 
                    onClick={handleCreateSession}
                    disabled={!createForm.title || createSessionMutation.isPending}
                  >
                    {createSessionMutation.isPending ? 'Creating...' : 'Create Session'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Stats Cards */}
        {sessionStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <FileText className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Total Sessions</p>
                    <p className="text-2xl font-bold">{sessionStats.total_sessions}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Play className="h-4 w-4 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Active</p>
                    <p className="text-2xl font-bold">{sessionStats.active_sessions}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <BarChart3 className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Completed</p>
                    <p className="text-2xl font-bold">{sessionStats.completed_sessions}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    <Archive className="h-4 w-4 text-gray-600" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Archived</p>
                    <p className="text-2xl font-bold">{sessionStats.archived_sessions}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Sessions List */}
        <Card>
          <CardHeader>
            <CardTitle>Sessions</CardTitle>
            <CardDescription>View and manage your analysis sessions</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList>
                <TabsTrigger value="active">Active</TabsTrigger>
                <TabsTrigger value="completed">Completed</TabsTrigger>
                <TabsTrigger value="archived">Archived</TabsTrigger>
                <TabsTrigger value="all">All</TabsTrigger>
              </TabsList>
              
              <TabsContent value={activeTab} className="mt-4">
                {isLoadingSessions ? (
                  <div className="text-center py-8">Loading sessions...</div>
                ) : sessions?.sessions.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No sessions found. Create your first session to get started.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {sessions?.sessions.map((session: any) => (
                      <Card 
                        key={session.id} 
                        className={`cursor-pointer transition-colors ${
                          selectedSessionId === session.id ? 'ring-2 ring-blue-500' : ''
                        }`}
                        onClick={() => onSessionSelect?.(session.id)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                              <div className="p-2 bg-gray-100 rounded-lg">
                                {getSessionTypeIcon(session.session_type)}
                              </div>
                              
                              <div className="flex-1">
                                <div className="flex items-center space-x-2">
                                  <h3 className="font-semibold">{session.title}</h3>
                                  <Badge className={getStatusColor(session.status)}>
                                    {session.status}
                                  </Badge>
                                </div>
                                
                                <div className="flex items-center space-x-4 mt-1 text-sm text-muted-foreground">
                                  <div className="flex items-center space-x-1">
                                    <Calendar className="h-3 w-3" />
                                    <span>{new Date(session.created_at).toLocaleDateString()}</span>
                                  </div>
                                  <div className="flex items-center space-x-1">
                                    <Clock className="h-3 w-3" />
                                    <span>{formatDuration(session.duration)}</span>
                                  </div>
                                  <div className="flex items-center space-x-1">
                                    <FileText className="h-3 w-3" />
                                    <span>{session.total_resumes} resumes</span>
                                  </div>
                                  <div className="flex items-center space-x-1">
                                    <Briefcase className="h-3 w-3" />
                                    <span>{session.total_jobs} jobs</span>
                                  </div>
                                  <div className="flex items-center space-x-1">
                                    <BarChart3 className="h-3 w-3" />
                                    <span>{session.total_analyses} analyses</span>
                                  </div>
                                </div>
                                
                                {session.tags.length > 0 && (
                                  <div className="flex items-center space-x-1 mt-2">
                                    <Tag className="h-3 w-3 text-muted-foreground" />
                                    <div className="flex space-x-1">
                                      {session.tags.map((tag: string, index: number) => (
                                        <Badge key={index} variant="outline" className="text-xs">
                                          {tag}
                                        </Badge>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleViewDetails(session.id);
                                }}
                              >
                                View Details
                              </Button>
                              
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="sm" onClick={(e) => e.stopPropagation()}>
                                    <MoreVertical className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  {session.status === 'active' && (
                                    <DropdownMenuItem onClick={() => handleSessionAction(session.id, 'complete')}>
                                      <Pause className="h-4 w-4 mr-2" />
                                      Complete
                                    </DropdownMenuItem>
                                  )}
                                  {session.status !== 'archived' && (
                                    <DropdownMenuItem onClick={() => handleSessionAction(session.id, 'archive')}>
                                      <Archive className="h-4 w-4 mr-2" />
                                      Archive
                                    </DropdownMenuItem>
                                  )}
                                  {session.status === 'archived' && (
                                    <DropdownMenuItem onClick={() => handleSessionAction(session.id, 'restore')}>
                                      <RotateCcw className="h-4 w-4 mr-2" />
                                      Restore
                                    </DropdownMenuItem>
                                  )}
                                  <Separator />
                                  <DropdownMenuItem 
                                    onClick={() => handleSessionAction(session.id, 'delete')}
                                    className="text-red-600"
                                  >
                                    <Trash2 className="h-4 w-4 mr-2" />
                                    Delete
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Session Details Dialog */}
        <Dialog open={isDetailsDialogOpen} onOpenChange={setIsDetailsDialogOpen}>
          <DialogContent className="max-w-4xl">
            <DialogHeader>
              <DialogTitle>Session Details</DialogTitle>
              <DialogDescription>
                Detailed information about the selected session
              </DialogDescription>
            </DialogHeader>
            
            {selectedSession && (
              <div className="space-y-6">
                {/* Session Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold mb-2">Session Information</h4>
                    <div className="space-y-2 text-sm">
                      <div><strong>Title:</strong> {selectedSession.session.title}</div>
                      <div><strong>Type:</strong> {selectedSession.session.session_type}</div>
                      <div><strong>Status:</strong> 
                        <Badge className={`ml-2 ${getStatusColor(selectedSession.session.status)}`}>
                          {selectedSession.session.status}
                        </Badge>
                      </div>
                      <div><strong>Created:</strong> {new Date(selectedSession.session.created_at).toLocaleString()}</div>
                      <div><strong>Duration:</strong> {formatDuration(selectedSession.session.duration || null)}</div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">Summary</h4>
                    <div className="space-y-2 text-sm">
                      <div><strong>Resumes:</strong> {selectedSession.session.total_resumes}</div>
                      <div><strong>Jobs:</strong> {selectedSession.session.total_jobs}</div>
                      <div><strong>Analyses:</strong> {selectedSession.session.total_analyses}</div>
                      {selectedSession.session.overall_match_score && (
                        <div><strong>Overall Score:</strong> {selectedSession.session.overall_match_score}%</div>
                      )}
                    </div>
                  </div>
                </div>
                
                <Separator />
                
                {/* Associated Items */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Resumes */}
                  <div>
                    <h4 className="font-semibold mb-2 flex items-center">
                      <FileText className="h-4 w-4 mr-2" />
                      Resumes ({selectedSession.resumes.length})
                    </h4>
                    <div className="space-y-2">
                      {selectedSession.resumes.map((resume) => (
                        <Card key={resume.id} className="p-3">
                          <div className="text-sm">
                            <div className="font-medium">{resume.filename}</div>
                            <div className="text-muted-foreground">
                              {resume.upload_date && new Date(resume.upload_date).toLocaleDateString()}
                            </div>
                            <Badge variant="outline" className="mt-1">
                              {resume.analysis_status}
                            </Badge>
                          </div>
                        </Card>
                      ))}
                      {selectedSession.resumes.length === 0 && (
                        <p className="text-sm text-muted-foreground">No resumes added</p>
                      )}
                    </div>
                  </div>
                  
                  {/* Jobs */}
                  <div>
                    <h4 className="font-semibold mb-2 flex items-center">
                      <Briefcase className="h-4 w-4 mr-2" />
                      Jobs ({selectedSession.jobs.length})
                    </h4>
                    <div className="space-y-2">
                      {selectedSession.jobs.map((job) => (
                        <Card key={job.id} className="p-3">
                          <div className="text-sm">
                            <div className="font-medium">{job.title}</div>
                            <div className="text-muted-foreground">{job.company}</div>
                            <div className="text-muted-foreground">{job.location}</div>
                          </div>
                        </Card>
                      ))}
                      {selectedSession.jobs.length === 0 && (
                        <p className="text-sm text-muted-foreground">No jobs added</p>
                      )}
                    </div>
                  </div>
                  
                  {/* Analyses */}
                  <div>
                    <h4 className="font-semibold mb-2 flex items-center">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Analyses ({selectedSession.analyses.length})
                    </h4>
                    <div className="space-y-2">
                      {selectedSession.analyses.map((analysis) => (
                        <Card key={analysis.id} className="p-3">
                          <div className="text-sm">
                            <Badge variant="outline">{analysis.status}</Badge>
                            <div className="mt-1 text-muted-foreground">
                              {analysis.start_date && new Date(analysis.start_date).toLocaleDateString()}
                            </div>
                            <div className="text-muted-foreground">
                              {analysis.job_count} jobs analyzed
                            </div>
                          </div>
                        </Card>
                      ))}
                      {selectedSession.analyses.length === 0 && (
                        <p className="text-sm text-muted-foreground">No analyses completed</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default SessionManager;