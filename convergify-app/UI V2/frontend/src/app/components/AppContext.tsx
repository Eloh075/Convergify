import React, { createContext, useContext, useState, useCallback } from "react";

export interface SkillItem {
  id: string;
  name: string;
  status: "match" | "gap" | "partial";
  category: string;
  marketDemand?: number;
  recommendation?: string;
  resumeEvidence?: string;
}

export interface Analysis {
  id: string;
  jobTitle: string;
  company: string;
  matchScore: number;
  date: string;
  skills: SkillItem[];
  strategicSummary: string;
  originalResume: string;
  optimizedResume: string;
  jobDescription: string;
  marketBenchmarking: boolean;
  strategicOptimization: boolean;
}

interface AppState {
  analyses: Analysis[];
  currentAnalysisId: string | null;
  addAnalysis: (analysis: Analysis) => void;
  deleteAnalysis: (id: string) => void;
  getCurrentAnalysis: () => Analysis | null;
  setCurrentAnalysisId: (id: string | null) => void;
  showTutorial: boolean;
  setShowTutorial: (show: boolean) => void;
  draftRoleTitle: string;
  setDraftRoleTitle: (title: string) => void;
  draftCompany: string;
  setDraftCompany: (company: string) => void;
  draftJobText: string;
  setDraftJobText: (text: string) => void;
  draftFileName: string | null;
  setDraftFileName: (name: string | null) => void;
  clearDraftState: () => void;
}

const AppContext = createContext<AppState | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [currentAnalysisId, setCurrentAnalysisId] = useState<string | null>(null);
  const [showTutorial, setShowTutorial] = useState(false);
  const [draftJobText, setDraftJobText] = useState("");
  const [draftRoleTitle, setDraftRoleTitle] = useState("");
  const [draftCompany, setDraftCompany] = useState("");
  const [draftFileName, setDraftFileName] = useState<string | null>(null);

  const addAnalysis = useCallback((analysis: Analysis) => {
    setAnalyses(prev => [analysis, ...prev]);
    setCurrentAnalysisId(analysis.id);
  }, []);

  const deleteAnalysis = useCallback((id: string) => {
    setAnalyses(prev => prev.filter(a => a.id !== id));
  }, []);

  const getCurrentAnalysis = useCallback(() => {
    return analyses.find(a => a.id === currentAnalysisId) || null;
  }, [analyses, currentAnalysisId]);

  const clearDraftState = useCallback(() => {
    setDraftRoleTitle("");
    setDraftCompany("");
    setDraftJobText("");
    setDraftFileName(null);
  }, []);

  return (
    <AppContext.Provider value={{
      analyses,
      currentAnalysisId,
      addAnalysis,
      deleteAnalysis,
      getCurrentAnalysis,
      setCurrentAnalysisId,
      showTutorial,
      setShowTutorial,
      draftRoleTitle,
      setDraftRoleTitle,
      draftCompany,
      setDraftCompany,
      draftJobText,
      setDraftJobText,
      draftFileName,
      setDraftFileName,
      clearDraftState
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used within AppProvider");
  return ctx;
}