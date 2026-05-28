import { useState } from 'react';
import { Play, Square, RefreshCw, Settings } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { ProgressMonitor, QueueMonitor } from '@/app/components/ProgressMonitor';
import { toast } from 'sonner';

export function ProgressDemo() {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [taskCounter, setTaskCounter] = useState(1);

  const startMockTask = (taskType: string) => {
    const taskId = `mock_${taskType}_${Date.now()}`;
    setActiveTaskId(taskId);
    setTaskCounter(prev => prev + 1);
    toast.success(`Started ${taskType} task: ${taskId}`);
  };

  const stopTask = () => {
    setActiveTaskId(null);
    toast.info('Task monitoring stopped');
  };

  return (
    <div className="flex-1 h-full overflow-y-auto bg-gray-50 dark:bg-gray-900">
      <div className="max-w-[1200px] mx-auto p-4 sm:p-6 lg:p-8 xl:p-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-6 bg-gradient-to-br from-purple-500 to-purple-600">
            <Settings className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-semibold mb-3 dark:text-white">Progress Monitor Demo</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Demonstration of real-time task progress monitoring
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Controls */}
          <Card>
            <CardHeader>
              <CardTitle>Task Controls</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <Button 
                  onClick={() => startMockTask('resume_analysis')}
                  className="w-full gap-2"
                >
                  <Play className="w-4 h-4" />
                  Start Resume Analysis
                </Button>
                
                <Button 
                  onClick={() => startMockTask('job_scraping')}
                  variant="outline"
                  className="w-full gap-2"
                >
                  <Play className="w-4 h-4" />
                  Start Job Scraping
                </Button>
                
                <Button 
                  onClick={() => startMockTask('skill_extraction')}
                  variant="outline"
                  className="w-full gap-2"
                >
                  <Play className="w-4 h-4" />
                  Start Skill Extraction
                </Button>
                
                <Button 
                  onClick={() => startMockTask('market_analysis')}
                  variant="outline"
                  className="w-full gap-2"
                >
                  <Play className="w-4 h-4" />
                  Start Market Analysis
                </Button>
              </div>

              <div className="border-t pt-4">
                <Button 
                  onClick={stopTask}
                  variant="destructive"
                  className="w-full gap-2"
                  disabled={!activeTaskId}
                >
                  <Square className="w-4 h-4" />
                  Stop Monitoring
                </Button>
              </div>

              {activeTaskId && (
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="text-sm font-medium text-blue-900 dark:text-blue-100">
                    Active Task
                  </div>
                  <div className="text-sm text-blue-700 dark:text-blue-200 font-mono">
                    {activeTaskId}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Queue Monitor */}
          <QueueMonitor />
        </div>

        {/* Progress Monitor */}
        <div className="mt-8">
          <ProgressMonitor
            taskId={activeTaskId || undefined}
            onTaskComplete={(result) => {
              toast.success('Task completed successfully!');
              console.log('Task result:', result);
            }}
            onTaskError={(error) => {
              toast.error(`Task failed: ${error}`);
            }}
            showDetails={true}
          />
        </div>

        {/* Compact Progress Monitor Example */}
        {activeTaskId && (
          <div className="mt-8">
            <Card>
              <CardHeader>
                <CardTitle>Compact Progress Monitor</CardTitle>
              </CardHeader>
              <CardContent>
                <ProgressMonitor
                  taskId={activeTaskId}
                  compact={true}
                />
              </CardContent>
            </Card>
          </div>
        )}

        {/* Information */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>About Progress Monitoring</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-2">Features</h4>
                <ul className="text-sm space-y-1 text-gray-600 dark:text-gray-400">
                  <li>• Real-time task status updates</li>
                  <li>• Progress bars and completion estimates</li>
                  <li>• Error handling and retry mechanisms</li>
                  <li>• Task history and duration tracking</li>
                  <li>• Queue monitoring and worker statistics</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Task Types</h4>
                <ul className="text-sm space-y-1 text-gray-600 dark:text-gray-400">
                  <li>• Resume analysis and skill extraction</li>
                  <li>• Job scraping from multiple sources</li>
                  <li>• Market intelligence analysis</li>
                  <li>• Resume optimization generation</li>
                  <li>• Comprehensive career analysis</li>
                </ul>
              </div>
            </div>
            
            <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                <strong>Note:</strong> This demo uses mock task data since Celery/Redis is not configured. 
                In production, this would connect to real background task queues for live progress updates.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}