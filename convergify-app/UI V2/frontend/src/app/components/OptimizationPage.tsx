import { useEffect } from "react";
import { useParams, useNavigate } from "react-router";
import { motion } from "motion/react";
import { ArrowLeft, AlertCircle, PenLine, Target, ChevronRight, FileDown, Archive } from "lucide-react";
import { useAppContext } from "./AppContext";
import { OptimizationStudio } from "./OptimizationStudio";
import { TutorialOverlay, type TutorialStep } from "./TutorialOverlay";

const OPTIMIZATION_TUTORIAL_STEPS: TutorialStep[] = [
  {
    selector: '[data-tutorial="optimization-diff"]',
    title: "Side-by-Side Comparison",
    description: "Your original resume is on the left, and the AI-optimized version is on the right. Highlighted text shows strategic additions.",
    icon: <PenLine className="w-4 h-4" />,
    position: "top",
  },
  {
    selector: '[data-tutorial="export-tools"]',
    title: "Export Your Resume",
    description: "Download the full analysis report or export the optimized resume when you're ready.",
    icon: <FileDown className="w-4 h-4" />,
    position: "top",
  },
  {
    selector: '[data-tutorial="lab-btn"]',
    title: "Past Analyses",
    description: "Access your previous strategy sessions and archived reports here.",
    icon: <Archive className="w-4 h-4" />,
    position: "bottom",
  },
];

export function OptimizationPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { analyses, setCurrentAnalysisId, showTutorial, setShowTutorial } = useAppContext();

  const analysis = analyses.find(a => a.id === id);

  useEffect(() => {
    if (id) setCurrentAnalysisId(id);
  }, [id, setCurrentAnalysisId]);

  // Auto-show tutorial on first visit
  useEffect(() => {
    const seen = localStorage.getItem("strategylab-optimization-tutorial-seen");
    if (!seen && analysis) {
      const timer = setTimeout(() => setShowTutorial(true), 600);
      return () => clearTimeout(timer);
    }
  }, [analysis, setShowTutorial]);

  if (!analysis) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-[#94A3B8] mx-auto mb-3" />
          <p className="text-[#64748B]">Analysis not found</p>
          <button
            onClick={() => navigate("/")}
            className="mt-4 px-4 py-2 rounded-lg bg-[#2563EB] text-white text-sm cursor-pointer"
          >
            Start New Analysis
          </button>
        </div>
      </div>
    );
  }

  const gapCount = analysis.skills.filter(s => s.status === "gap").length;
  const partialCount = analysis.skills.filter(s => s.status === "partial").length;

  return (
    <div className="flex-1 bg-gradient-to-br from-[#F8FAFC] via-white to-[#EFF6FF]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-8">
        {/* Back to Analysis */}
        <button
          onClick={() => navigate(`/results/${id}`)}
          className="flex items-center gap-1.5 text-[#64748B] hover:text-[#2563EB] transition-colors cursor-pointer text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Analysis
        </button>

        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] border border-[#E2E8F0] p-6 sm:p-8"
        >
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#F59E0B]/20 to-[#F59E0B]/5 flex items-center justify-center border border-[#F59E0B]/20">
                <PenLine className="w-6 h-6 text-[#F59E0B]" />
              </div>
              <div>
                <h1 className="text-[#0F172A]">Optimization Studio</h1>
                <p className="text-sm text-[#64748B] mt-0.5">
                  {analysis.jobTitle} at {analysis.company}
                </p>
              </div>
            </div>

            {/* Stats Badges */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#FEF2F2] border border-[#FECACA]">
                <div className="w-2 h-2 rounded-full bg-[#EF4444]" />
                <span className="text-xs text-[#991B1B]">{gapCount} Gaps addressed</span>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#FFFBEB] border border-[#FDE68A]">
                <div className="w-2 h-2 rounded-full bg-[#F59E0B]" />
                <span className="text-xs text-[#92400E]">{partialCount} Enhanced</span>
              </div>
            </div>
          </div>

          {/* Breadcrumb navigation */}
          <div className="flex items-center gap-2 mt-5 pt-5 border-t border-[#E2E8F0]">
            <button
              onClick={() => navigate(`/results/${id}`)}
              className="text-xs text-[#64748B] hover:text-[#2563EB] transition-colors cursor-pointer"
            >
              Strategy Dashboard
            </button>
            <ChevronRight className="w-3 h-3 text-[#CBD5E1]" />
            <span className="text-xs text-[#2563EB] font-medium">Optimization Studio</span>
          </div>
        </motion.div>

        {/* Step indicator */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center justify-center gap-3"
        >
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-[#22C55E] flex items-center justify-center">
              <Target className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-xs text-[#64748B]">Gap Analysis</span>
          </div>
          <div className="w-12 h-px bg-[#E2E8F0]" />
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-[#2563EB] flex items-center justify-center ring-4 ring-[#2563EB]/10">
              <PenLine className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-xs text-[#0F172A] font-medium">Resume Optimization</span>
          </div>
        </motion.div>

        {/* Optimization Studio Component */}
        <OptimizationStudio
          originalResume={analysis.originalResume}
          optimizedResume={analysis.optimizedResume}
        />
      </div>

      {/* Tutorial Overlay */}
      <TutorialOverlay
        show={showTutorial}
        onClose={() => {
          setShowTutorial(false);
          localStorage.setItem("strategylab-optimization-tutorial-seen", "true");
        }}
        steps={OPTIMIZATION_TUTORIAL_STEPS}
      />
    </div>
  );
}