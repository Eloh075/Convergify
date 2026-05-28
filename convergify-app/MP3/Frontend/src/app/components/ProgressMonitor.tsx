import { useState, useEffect } from 'react';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Loader2, 
  Play, 
  Pause, 
  Square,
  RefreshCw,
  Activity
} from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Progress } from '@/app/components/ui/progress';
import { Badge } from '@/app/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { useTaskStatus } from '@/hooks/useApi';

interface TaskProgress {
  task_id: string;
  task_name: string;
  status: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE' | 'REVOKED';
  progress?: number;
  current_step?: string;
  estimated_completion?: string;
  error?: string;
  result?: any;
  created_at?: string;
  started_at?: string;
  completed_at?: string;
}

interface ProgressMonitorProps {
  taskId?: string;
  onTaskComplete?: (result: any) => void;
  onTaskError?: (error: string) => void;
  showDetails?: boolean;
  compact?: boolean;
}

export function ProgressMonitor({ 
  taskId, 
  onTaskComplete, 
  onTaskError, 
  showDetails = true,
  compact = false 
}: ProgressMonitorProps) {
  const [isMonitoring, setIsMonitoring] = useState(!!taskId);
  
  const { 
    data: taskStatus, 
    isLoading, 
    error, 
    refetch 
  } = useTaskStatus(taskId || '', isMonitoring);

  // Handle task completion
  useEffect(() => {
    if (taskStatus) {
      if (taskStatus.status === 'SUCCESS' && onTaskComplete) {
        onTaskComplete(taskStatus.result);
        setIsMonitoring(false);
      } else if (taskStatus.status === 'FAILURE' && onTaskError) {
        onTaskError(taskStatus.error || 'Task failed');
        setIsMonitoring(false);
      } else if (taskStatus.status === 'REVOKED') {
        setIsMonitoring(false);
      }
    }
  }, [taskStatus, onTaskComplete, onTaskError]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'FAILURE':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'REVOKED':
        return <Square className="w-4 h-4 text-gray-600" />;
      case 'PROGRESS':
        return <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />;
      case 'PENDING':
      default:
        return <Clock className="w-4 h-4 text-yellow-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'FAILURE':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'REVOKED':
        return 'bg-gray-100 text-gray-700 border-gray-200';
      case 'PROGRESS':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'PENDING':
      default:
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    }
  };

  const formatDuration = (startTime?: string, endTime?: string) => {
    if (!startTime) return null;
    
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const duration = Math.floor((end.getTime() - start.getTime()) / 1000);
    
    if (duration < 60) return `${duration}s`;
    if (duration < 3600) return `${Math.floor(duration / 60)}m ${duration % 60}s`;
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`;
  };

  const formatTaskName = (taskName: string) => {
    return taskName
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  };

  if (!taskId) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Task Monitor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            No active tasks to monitor
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isLoading && !taskStatus) {
    return (
      <Card className="w-full">
        <CardContent className="p-6">
          <div className="flex items-center gap-3">
            <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
            <span>Loading task status...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full border-red-200">
        <CardContent className="p-6">
          <div className="flex items-center gap-3 text-red-600">
            <AlertCircle className="w-5 h-5" />
            <span>Failed to load task status</span>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (compact) {
    return (
      <div className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border">
        {getStatusIcon(taskStatus?.status || 'PENDING')}
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate">
            {taskStatus?.task_name ? formatTaskName(taskStatus.task_name) : 'Processing...'}
          </div>
          {taskStatus?.current_step && (
            <div className="text-xs text-gray-500 truncate">
              {taskStatus.current_step}
            </div>
          )}
        </div>
        {taskStatus?.progress !== undefined && (
          <div className="w-20">
            <Progress value={taskStatus.progress} className="h-2" />
          </div>
        )}
        <Badge className={getStatusColor(taskStatus?.status || 'PENDING')}>
          {taskStatus?.status || 'PENDING'}
        </Badge>
      </div>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Task Progress
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsMonitoring(!isMonitoring)}
            >
              {isMonitoring ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {isMonitoring ? 'Pause' : 'Resume'}
            </Button>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Task Info */}
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              {getStatusIcon(taskStatus?.status || 'PENDING')}
              <span className="font-medium">
                {taskStatus?.task_name ? formatTaskName(taskStatus.task_name) : 'Processing Task'}
              </span>
            </div>
            <div className="text-sm text-gray-500">
              Task ID: {taskId}
            </div>
          </div>
          <Badge className={getStatusColor(taskStatus?.status || 'PENDING')}>
            {taskStatus?.status || 'PENDING'}
          </Badge>
        </div>

        {/* Progress Bar */}
        {taskStatus?.progress !== undefined && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress</span>
              <span>{taskStatus.progress}%</span>
            </div>
            <Progress value={taskStatus.progress} className="h-3" />
          </div>
        )}

        {/* Current Step */}
        {taskStatus?.current_step && (
          <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="text-sm font-medium text-blue-900 dark:text-blue-100">
              Current Step
            </div>
            <div className="text-sm text-blue-700 dark:text-blue-200">
              {taskStatus.current_step}
            </div>
          </div>
        )}

        {/* Estimated Completion */}
        {taskStatus?.estimated_completion && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="w-4 h-4" />
            <span>
              Estimated completion: {new Date(taskStatus.estimated_completion).toLocaleTimeString()}
            </span>
          </div>
        )}

        {/* Timing Information */}
        {showDetails && (
          <div className="grid grid-cols-2 gap-4 text-sm">
            {taskStatus?.created_at && (
              <div>
                <span className="text-gray-500">Created:</span>
                <div>{new Date(taskStatus.created_at).toLocaleString()}</div>
              </div>
            )}
            {taskStatus?.started_at && (
              <div>
                <span className="text-gray-500">Started:</span>
                <div>{new Date(taskStatus.started_at).toLocaleString()}</div>
              </div>
            )}
            {taskStatus?.completed_at && (
              <div>
                <span className="text-gray-500">Completed:</span>
                <div>{new Date(taskStatus.completed_at).toLocaleString()}</div>
              </div>
            )}
            {taskStatus?.started_at && (
              <div>
                <span className="text-gray-500">Duration:</span>
                <div>{formatDuration(taskStatus.started_at, taskStatus.completed_at)}</div>
              </div>
            )}
          </div>
        )}

        {/* Error Display */}
        {taskStatus?.error && (
          <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
            <div className="flex items-center gap-2 text-red-900 dark:text-red-100 font-medium">
              <XCircle className="w-4 h-4" />
              Error
            </div>
            <div className="text-sm text-red-700 dark:text-red-200 mt-1">
              {taskStatus.error}
            </div>
          </div>
        )}

        {/* Success Result */}
        {taskStatus?.status === 'SUCCESS' && taskStatus?.result && (
          <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="flex items-center gap-2 text-green-900 dark:text-green-100 font-medium">
              <CheckCircle className="w-4 h-4" />
              Completed Successfully
            </div>
            {showDetails && (
              <div className="text-sm text-green-700 dark:text-green-200 mt-1">
                <pre className="whitespace-pre-wrap">
                  {typeof taskStatus.result === 'string' 
                    ? taskStatus.result 
                    : JSON.stringify(taskStatus.result, null, 2)
                  }
                </pre>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Queue Monitor Component
interface QueueMonitorProps {
  refreshInterval?: number;
}

export function QueueMonitor({ refreshInterval = 5000 }: QueueMonitorProps) {
  const [queueStats, setQueueStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchQueueStats = async () => {
      try {
        // This would call an API endpoint to get queue statistics
        // For now, we'll use mock data
        setQueueStats({
          queues: {
            analysis: { length: 2, consumers: 1 },
            scraping: { length: 0, consumers: 1 },
            processing: { length: 1, consumers: 1 }
          },
          total_workers: 3,
          total_active_tasks: 1
        });
      } catch (error) {
        console.error('Failed to fetch queue stats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchQueueStats();
    const interval = setInterval(fetchQueueStats, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Queue Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Loading queue status...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Queue Status
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Overall Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {queueStats?.total_workers || 0}
              </div>
              <div className="text-sm text-blue-700">Active Workers</div>
            </div>
            <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {queueStats?.total_active_tasks || 0}
              </div>
              <div className="text-sm text-green-700">Running Tasks</div>
            </div>
          </div>

          {/* Queue Details */}
          {queueStats?.queues && (
            <div className="space-y-2">
              <h4 className="font-medium">Queue Details</h4>
              {Object.entries(queueStats.queues).map(([queueName, stats]: [string, any]) => (
                <div key={queueName} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <span className="font-medium capitalize">{queueName}</span>
                  <div className="flex items-center gap-4 text-sm">
                    <span>{stats.length} queued</span>
                    <span>{stats.consumers} workers</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}