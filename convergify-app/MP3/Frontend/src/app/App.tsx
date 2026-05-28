import { useState, useEffect } from 'react';
import { Toaster } from 'sonner';
import { ThemeProvider } from '@/app/contexts/ThemeContext';
import { QueryProvider } from '@/providers/QueryProvider';
import { LeftSidebar } from '@/app/components/LeftSidebar';
import { ResumeVault } from '@/app/components/ResumeVault';
import { JobHub } from '@/app/components/JobHubEnhanced';
import { AnalysisLauncherIntelligence } from '@/app/components/AnalysisLauncherIntelligence';
import { AnalysisProgressMonitor } from '@/app/components/AnalysisProgressMonitor';
import { AnalysisResults } from '@/app/components/AnalysisResults';
import { mockSessions } from '@/app/data/sessionData';

type ActiveTab = 'resume' | 'jobs' | 'analysis' | 'progress' | 'results';

// Analysis state that persists across tab switches
interface AnalysisState {
  analysisId: string | null;
  status: 'idle' | 'running' | 'completed' | 'error';
}

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('resume');
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  const [analysisState, setAnalysisState] = useState<AnalysisState>({
    analysisId: null,
    status: 'idle'
  });
  
  // Track whether to show results in analysis tab
  const [showResultsInAnalysisTab, setShowResultsInAnalysisTab] = useState(false);

  // When switching to analysis tab, check state
  useEffect(() => {
    if (activeTab === 'analysis') {
      if (analysisState.status === 'running' && analysisState.analysisId) {
        // If there's a running analysis, redirect to progress tab
        setActiveTab('progress');
      } else if (analysisState.status === 'completed' && analysisState.analysisId) {
        // If there's a completed analysis, show results in analysis tab
        setShowResultsInAnalysisTab(true);
      }
    }
  }, [activeTab, analysisState]);

  const handleUploadNew = () => {
    // Switch to analysis tab to start new analysis
    setActiveTab('analysis');
  };

  const handleStartScraper = () => {
    // Would navigate to scraper setup, for now just switch to analysis
    setActiveTab('analysis');
  };

  const handleRunAnalysis = () => {
    setActiveTab('analysis');
  };

  const handleAnalysisStarted = (analysisId: string) => {
    console.log('Analysis started with ID:', analysisId);
    setAnalysisState({
      analysisId,
      status: 'running'
    });
    setActiveTab('progress');
  };

  const handleAnalysisComplete = () => {
    console.log('Analysis completed');
    setAnalysisState(prev => ({
      ...prev,
      status: 'completed'
    }));
    setShowResultsInAnalysisTab(true);
    setActiveTab('analysis'); // Go back to analysis tab to show results
  };
  
  const handleNewAnalysis = () => {
    console.log('Starting new analysis');
    setAnalysisState({
      analysisId: null,
      status: 'idle'
    });
    setShowResultsInAnalysisTab(false);
  };

  const handleAnalysisError = (error: string) => {
    console.error('Analysis error:', error);
    setAnalysisState(prev => ({
      ...prev,
      status: 'error'
    }));
    // Could show error toast or redirect back to analysis
  };

  return (
    <QueryProvider>
      <ThemeProvider>
        <div className="h-screen w-screen flex bg-white dark:bg-gray-900 transition-colors overflow-hidden">
          {/* Left Sidebar Navigation */}
          <LeftSidebar 
            activeTab={activeTab} 
            onTabChange={setActiveTab}
            isExpanded={sidebarExpanded}
            onToggleExpanded={setSidebarExpanded}
          />

          {/* Main Content Area - Adjusts to sidebar width */}
          <div 
            className={`flex-1 flex flex-col min-w-0 transition-all duration-300 overflow-y-auto ${
              sidebarExpanded ? 'ml-60' : 'ml-20'
            }`}
          >
            {activeTab === 'resume' && (
              <ResumeVault sessions={mockSessions} onUploadNew={handleUploadNew} />
            )}

            {activeTab === 'jobs' && (
              <JobHub
                onStartScraper={handleStartScraper}
                onRunAnalysis={handleRunAnalysis}
              />
            )}

            {activeTab === 'analysis' && !showResultsInAnalysisTab && (
              <AnalysisLauncherIntelligence
                onAnalysisStarted={handleAnalysisStarted}
              />
            )}
            
            {activeTab === 'analysis' && showResultsInAnalysisTab && analysisState.analysisId && (
              <AnalysisResults 
                analysisId={analysisState.analysisId}
                onNewAnalysis={handleNewAnalysis}
              />
            )}

            {activeTab === 'progress' && analysisState.analysisId && (
              <AnalysisProgressMonitor 
                analysisId={analysisState.analysisId}
                onComplete={handleAnalysisComplete}
                onError={handleAnalysisError}
              />
            )}

            {activeTab === 'results' && analysisState.analysisId && (
              <AnalysisResults analysisId={analysisState.analysisId} />
            )}
          </div>

          {/* Toast Notifications */}
          <Toaster position="top-right" richColors />
        </div>
      </ThemeProvider>
    </QueryProvider>
  );
}