import { useState, useEffect } from 'react';
import { 
  X, 
  Download, 
  FileText, 
  ArrowRight, 
  Copy, 
  ExternalLink,
  Zap,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { useResumeComparison } from '@/hooks/useApi';
import { downloadFile, API_ENDPOINTS } from '@/lib/api';
import type { Resume } from '@/types/api';

interface ResumeComparisonProps {
  originalResume: Resume;
  optimizedResumeId: string;
  onClose: () => void;
  onExport?: (format: 'pdf' | 'docx') => void;
}

interface DiffLine {
  type: 'added' | 'removed' | 'unchanged' | 'modified';
  content: string;
  lineNumber?: number;
  highlight?: boolean;
}

function DiffViewer({ 
  originalText, 
  optimizedText
}: { 
  originalText: string; 
  optimizedText: string;
}) {
  const [diffLines, setDiffLines] = useState<DiffLine[]>([]);

  useEffect(() => {
    // Simple diff algorithm for demonstration
    const originalLines = originalText.split('\n');
    const optimizedLines = optimizedText.split('\n');
    const diff: DiffLine[] = [];

    // For now, we'll show a simplified diff
    // In a real implementation, you'd use a proper diff algorithm
    const maxLines = Math.max(originalLines.length, optimizedLines.length);
    
    for (let i = 0; i < maxLines; i++) {
      const originalLine = originalLines[i] || '';
      const optimizedLine = optimizedLines[i] || '';
      
      if (originalLine === optimizedLine) {
        diff.push({
          type: 'unchanged',
          content: originalLine,
          lineNumber: i + 1
        });
      } else if (originalLine && !optimizedLine) {
        diff.push({
          type: 'removed',
          content: originalLine,
          lineNumber: i + 1
        });
      } else if (!originalLine && optimizedLine) {
        diff.push({
          type: 'added',
          content: optimizedLine,
          lineNumber: i + 1,
          highlight: true
        });
      } else {
        diff.push({
          type: 'modified',
          content: optimizedLine,
          lineNumber: i + 1,
          highlight: true
        });
      }
    }

    setDiffLines(diff);
  }, [originalText, optimizedText]);

  return (
    <div className="font-mono text-sm">
      {diffLines.map((line, index) => (
        <div
          key={index}
          className={`flex items-start gap-3 px-3 py-1 ${
            line.type === 'added' 
              ? 'bg-green-50 dark:bg-green-900/20 border-l-2 border-green-500 dark:border-green-400' 
              : line.type === 'removed'
              ? 'bg-red-50 dark:bg-red-900/20 border-l-2 border-red-500 dark:border-red-400'
              : line.type === 'modified'
              ? 'bg-yellow-50 dark:bg-yellow-900/20 border-l-2 border-yellow-500 dark:border-yellow-400'
              : 'hover:bg-gray-50 dark:hover:bg-gray-800'
          }`}
        >
          <span className="text-gray-400 dark:text-gray-500 text-xs w-8 flex-shrink-0 text-right">
            {line.lineNumber}
          </span>
          <span className={`flex-1 ${
            line.type === 'added' ? 'text-green-800 dark:text-green-200' :
            line.type === 'removed' ? 'text-red-800 dark:text-red-200' :
            line.type === 'modified' ? 'text-yellow-800 dark:text-yellow-200' :
            'text-gray-700 dark:text-gray-300'
          }`}>
            {line.content || ' '}
          </span>
          {line.highlight && (
            <Zap className="w-3 h-3 text-orange-500 dark:text-orange-400 flex-shrink-0" />
          )}
        </div>
      ))}
    </div>
  );
}

function ChangesSummary({ 
  changes, 
  improvementScore 
}: { 
  changes: any[]; 
  improvementScore?: number;
}) {
  const changeTypes = changes.reduce((acc, change) => {
    acc[change.type] = (acc[change.type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const totalSkillsAdded = changes
    .filter(change => change.skills_added)
    .reduce((total, change) => total + change.skills_added.length, 0);

  return (
    <div className="space-y-4">
      {/* Improvement Score */}
      {improvementScore && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
            <div>
              <h3 className="font-semibold text-green-800 dark:text-green-200">Improvement Score</h3>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{improvementScore}%</p>
              <p className="text-sm text-green-700 dark:text-green-300">Overall match improvement</p>
            </div>
          </div>
        </div>
      )}

      {/* Changes Overview */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <h4 className="font-semibold mb-2 flex items-center gap-2 dark:text-white">
            <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
            Changes Made
          </h4>
          <div className="space-y-2">
            {Object.entries(changeTypes).map(([type, count]) => (
              <div key={type} className="flex justify-between text-sm">
                <span className="capitalize dark:text-gray-300">{type.replace('_', ' ')}</span>
                <Badge variant="secondary">{String(count)}</Badge>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <h4 className="font-semibold mb-2 flex items-center gap-2 dark:text-white">
            <Zap className="w-4 h-4 text-orange-600 dark:text-orange-400" />
            Skills Enhanced
          </h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="dark:text-gray-300">Skills Added</span>
              <Badge variant="secondary">{totalSkillsAdded}</Badge>
            </div>
            <div className="flex justify-between text-sm">
              <span className="dark:text-gray-300">Sections Modified</span>
              <Badge variant="secondary">{changes.length}</Badge>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Changes */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
        <h4 className="font-semibold mb-3 flex items-center gap-2 dark:text-white">
          <Info className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          Change Details
        </h4>
        <div className="space-y-3">
          {changes.map((change, index) => (
            <div key={index} className="border-l-2 border-blue-200 dark:border-blue-800 pl-3">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <p className="font-medium text-sm dark:text-white">{change.description}</p>
                  {change.skills_added && change.skills_added.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {change.skills_added.map((skill: string, skillIndex: number) => (
                        <Badge key={skillIndex} variant="outline" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  )}
                  {change.recommendations && change.recommendations.length > 0 && (
                    <ul className="mt-2 text-xs text-gray-600 dark:text-gray-300 list-disc list-inside">
                      {change.recommendations.map((rec: string, recIndex: number) => (
                        <li key={recIndex}>{rec}</li>
                      ))}
                    </ul>
                  )}
                </div>
                <Badge 
                  variant={change.type === 'addition' ? 'default' : 'secondary'}
                  className="text-xs"
                >
                  {change.type}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function ResumeComparison({
  originalResume,
  optimizedResumeId,
  onClose,
  onExport
}: ResumeComparisonProps) {
  const { data: comparison, isLoading, error } = useResumeComparison(
    originalResume.id,
    optimizedResumeId
  );

  const handleExport = async (format: 'pdf' | 'docx') => {
    if (onExport) {
      onExport(format);
    } else {
      try {
        // Generate filename for the comparison export
        const timestamp = new Date().toISOString().split('T')[0];
        const filename = `resume_comparison_${originalResume.filename.replace(/\.[^/.]+$/, "")}_${timestamp}.${format}`;
        
        // For now, we'll download the optimized resume
        // In a real implementation, this would be a dedicated comparison export endpoint
        if (comparison?.optimized?.id) {
          await downloadFile(API_ENDPOINTS.RESUME_DOWNLOAD(comparison.optimized.id), filename);
        }
      } catch (error) {
        console.error('Export failed:', error);
        // Could show a toast notification here
      }
    }
  };

  const handleCopyOptimized = async () => {
    if (comparison?.optimized?.text) {
      try {
        await navigator.clipboard.writeText(comparison.optimized.text);
        // Could show a toast notification here
        console.log('Optimized resume copied to clipboard');
      } catch (error) {
        console.error('Failed to copy to clipboard:', error);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-8">
          <div className="flex items-center gap-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span className="dark:text-white">Loading comparison...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !comparison) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-8 max-w-md">
          <div className="flex items-center gap-3 mb-4">
            <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
            <h3 className="font-semibold dark:text-white">Comparison Unavailable</h3>
          </div>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            Unable to load the resume comparison. The optimized version may not be ready yet.
          </p>
          <Button onClick={onClose}>Close</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-[1400px] h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-xl font-semibold dark:text-white">Resume Comparison</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {originalResume.filename} → Optimized Version
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={handleCopyOptimized} className="gap-2">
              <Copy className="w-4 h-4" />
              Copy Optimized
            </Button>
            <Button onClick={() => handleExport('pdf')} className="gap-2">
              <Download className="w-4 h-4" />
              Export PDF
            </Button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 dark:text-gray-300" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          <Tabs defaultValue="side-by-side" className="h-full flex flex-col">
            <TabsList className="mx-6 mt-4">
              <TabsTrigger value="side-by-side">Side by Side</TabsTrigger>
              <TabsTrigger value="diff">Diff View</TabsTrigger>
              <TabsTrigger value="changes">Changes Summary</TabsTrigger>
            </TabsList>

            <TabsContent value="side-by-side" className="flex-1 overflow-hidden mt-4">
              <div className="h-full flex">
                {/* Original Resume */}
                <div className="flex-1 border-r border-gray-200 dark:border-gray-700 flex flex-col">
                  <div className="px-6 py-3 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                    <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200 flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Original Resume
                    </h3>
                  </div>
                  <div className="flex-1 overflow-y-auto p-6">
                    <div className="prose prose-sm max-w-none">
                      <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 font-sans">
                        {comparison.original.text}
                      </pre>
                    </div>
                  </div>
                </div>

                {/* Optimized Resume */}
                <div className="flex-1 flex flex-col">
                  <div className="px-6 py-3 bg-green-50 dark:bg-green-900/20 border-b border-green-200 dark:border-green-800">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-green-700 dark:text-green-200 flex items-center gap-2">
                        <Zap className="w-4 h-4" />
                        Optimized Resume
                      </h3>
                      {comparison.comparison.improvement_score && (
                        <Badge className="bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200">
                          +{comparison.comparison.improvement_score}% improvement
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="flex-1 overflow-y-auto p-6">
                    <div className="prose prose-sm max-w-none">
                      <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 font-sans">
                        {comparison.optimized.text}
                      </pre>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="diff" className="flex-1 overflow-hidden mt-4">
              <div className="h-full overflow-y-auto px-6">
                <DiffViewer
                  originalText={comparison.original.text}
                  optimizedText={comparison.optimized.text}
                />
              </div>
            </TabsContent>

            <TabsContent value="changes" className="flex-1 overflow-hidden mt-4">
              <div className="h-full overflow-y-auto px-6">
                <ChangesSummary
                  changes={comparison.optimized.changes}
                  improvementScore={comparison.comparison.improvement_score}
                />
              </div>
            </TabsContent>
          </Tabs>
        </div>

        {/* Footer Stats */}
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Original Length</p>
                <p className="text-sm font-semibold dark:text-white">{comparison.original.text_length} chars</p>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400 dark:text-gray-500" />
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Optimized Length</p>
                <p className="text-sm font-semibold dark:text-white">{comparison.optimized.text_length} chars</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Changes Made</p>
                <p className="text-sm font-semibold dark:text-white">{comparison.comparison.changes_count}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" className="gap-2">
                <ExternalLink className="w-4 h-4" />
                Open in New Tab
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}