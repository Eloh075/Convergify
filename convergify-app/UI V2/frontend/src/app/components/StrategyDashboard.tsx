import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router";
import { motion } from "motion/react";
import { ArrowLeft, Target, Zap, AlertCircle, CheckCircle2, Filter, ChevronRight, Star, PenLine, ArrowRight, BarChart3, MousePointerClick } from "lucide-react";
import { useAppContext, type SkillItem } from "./AppContext";
import { MatchGauge } from "./MatchGauge";
import { GapDrawer } from "./GapDrawer";
import { TutorialOverlay, type TutorialStep } from "./TutorialOverlay";
import { getAnalysisResult } from "../../lib/api";

const RESULTS_TUTORIAL_STEPS: TutorialStep[] = [
  {
    selector: '[data-tutorial="match-score"]',
    title: "Fit Score",
    description: "How well your resume matches this role.",
    icon: <BarChart3 className="w-4 h-4" />,
    position: "right",
  },
  {
    selector: '[data-tutorial="priorities"]',
    title: "Top Priorities",
    description: "Your 3 biggest gaps. Click any card for details.",
    icon: <Target className="w-4 h-4" />,
    position: "bottom",
  },
  {
    selector: '[data-tutorial="evidence-grid"]',
    title: "Evidence Grid",
    description: "Tap red or amber pills to open recommendations.",
    icon: <MousePointerClick className="w-4 h-4" />,
    position: "top",
  },
  {
    selector: '[data-tutorial="critical-toggle"]',
    title: "Focus Mode",
    description: "Filter to gaps and partial matches only.",
    icon: <Filter className="w-4 h-4" />,
    position: "bottom",
  },
  {
    selector: '[data-tutorial="optimize-btn"]',
    title: "Optimize Resume",
    description: "Your AI-rewritten resume with changes highlighted.",
    icon: <PenLine className="w-4 h-4" />,
    position: "bottom",
  },
];

const categoryOrder = [
  "AI Specialization",
  "ML Frameworks",
  "Programming",
  "DevOps",
  "Cloud",
  "Data",
  "Tools",
  "Methodology",
  "Soft Skills",
];

export function StrategyDashboard() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { analyses, setCurrentAnalysisId, showTutorial, setShowTutorial } = useAppContext();
  const [selectedSkill, setSelectedSkill] = useState<SkillItem | null>(null);
  const [viewMode, setViewMode] = useState<"all" | "critical">("all");

  const analysis = analyses.find(a => a.id === id);

  useEffect(() => {
    if (id) setCurrentAnalysisId(id);
  }, [id, setCurrentAnalysisId]);

  // Auto-show tutorial on first visit
  useEffect(() => {
    const seen = localStorage.getItem("strategylab-results-tutorial-seen");
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

  const matchCount = analysis.skills.filter(s => s.status === "match").length;
  const gapCount = analysis.skills.filter(s => s.status === "gap").length;
  const partialCount = analysis.skills.filter(s => s.status === "partial").length;

  // Identify high priority actions (Gaps/Partials with highest market demand)
  const prioritySkills = analysis.skills
    .filter(s => s.status === "gap" || s.status === "partial")
    .sort((a, b) => (b.marketDemand || 0) - (a.marketDemand || 0))
    .slice(0, 3);

  // Group skills by category based on viewMode
  const grouped: Record<string, SkillItem[]> = {};
  analysis.skills.forEach(s => {
    if (viewMode === "critical" && s.status === "match") return;
    
    if (!grouped[s.category]) grouped[s.category] = [];
    grouped[s.category].push(s);
  });

  const sortedCategories = Object.keys(grouped).sort(
    (a, b) => (categoryOrder.indexOf(a) === -1 ? 99 : categoryOrder.indexOf(a)) - (categoryOrder.indexOf(b) === -1 ? 99 : categoryOrder.indexOf(b))
  );

  // Navigation Logic
  const flatSkills: SkillItem[] = [];
  sortedCategories.forEach(cat => {
    flatSkills.push(...grouped[cat]);
  });

  const currentSkillIndex = flatSkills.findIndex(s => s.id === selectedSkill?.id);
  const hasNext = currentSkillIndex !== -1 && currentSkillIndex < flatSkills.length - 1;
  const hasPrev = currentSkillIndex !== -1 && currentSkillIndex > 0;

  const handleNext = () => {
    if (hasNext) setSelectedSkill(flatSkills[currentSkillIndex + 1]);
  };

  const handlePrev = () => {
    if (hasPrev) setSelectedSkill(flatSkills[currentSkillIndex - 1]);
  };

  return (
    <div className="flex-1 bg-gradient-to-br from-[#F8FAFC] via-white to-[#EFF6FF]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-8">
        {/* Back Button */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-1.5 text-[#64748B] hover:text-[#2563EB] transition-colors cursor-pointer text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            New Analysis
          </button>

          {/* Optimize Resume Button */}
          {analysis.strategicOptimization && (
            <button
              data-tutorial="optimize-btn"
              onClick={() => navigate(`/optimization/${id}`)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#0F172A] text-white text-sm hover:bg-[#1E293B] transition-all cursor-pointer group shadow-sm"
            >
              <PenLine className="w-4 h-4 text-[#F59E0B]" />
              <span>Optimize Resume</span>
              <ArrowRight className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all" />
            </button>
          )}
        </div>

        {/* Section A: Fit Header */}
        <motion.div
          data-tutorial="match-score"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] border border-[#E2E8F0] p-6 sm:p-8"
        >
          <div className="flex flex-col md:flex-row items-center gap-6 md:gap-10">
            {/* Gauge */}
            <div className="flex-shrink-0">
              <MatchGauge score={analysis.matchScore} size={180} />
            </div>

            {/* Summary */}
            <div className="flex-1 text-center md:text-left">
              <div className="flex flex-col sm:flex-row items-center md:items-start gap-2 sm:gap-3 mb-2">
                <h1 className="text-[#0F172A]">{analysis.jobTitle}</h1>
                <span className="text-sm text-[#64748B] bg-[#F1F5F9] px-3 py-1 rounded-full">
                  {analysis.company}
                </span>
              </div>
              <p className="text-[#64748B] text-sm leading-relaxed mt-3 max-w-2xl">
                {analysis.strategicSummary}
              </p>
              <div className="flex items-center justify-center md:justify-start gap-4 mt-5">
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-[#22C55E]" />
                  <span className="text-xs text-[#64748B]">{matchCount} Matches</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-[#EF4444]" />
                  <span className="text-xs text-[#64748B]">{gapCount} Gaps</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-[#F59E0B]" />
                  <span className="text-xs text-[#64748B]">{partialCount} Partial</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Section A.5: Priority Actions (New Recommendation) */}
        {prioritySkills.length > 0 && (
          <motion.div
            data-tutorial="priorities"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-4"
          >
            <div className="md:col-span-3 flex items-center gap-2 mb-1">
              <Star className="w-5 h-5 text-[#F59E0B] fill-[#F59E0B]" />
              <h2 className="text-[#0F172A] font-medium">Top Strategic Priorities</h2>
            </div>
            {prioritySkills.map((skill, i) => (
              <button
                key={skill.id}
                onClick={() => setSelectedSkill(skill)}
                className="text-left bg-white p-4 rounded-xl shadow-sm border border-[#E2E8F0] hover:border-[#2563EB]/50 hover:shadow-md transition-all group relative overflow-hidden"
              >
                <div className={`absolute top-0 left-0 w-1 h-full ${skill.status === 'gap' ? 'bg-[#EF4444]' : 'bg-[#F59E0B]'}`} />
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-medium text-[#64748B] uppercase tracking-wider">{skill.category}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                    skill.status === 'gap' 
                      ? 'bg-[#FEF2F2] text-[#991B1B]' 
                      : 'bg-[#FFFBEB] text-[#92400E]'
                  }`}>
                    {skill.status === 'gap' ? 'Critical Gap' : 'Partial Match'}
                  </span>
                </div>
                <h3 className="font-semibold text-[#0F172A] mb-1 group-hover:text-[#2563EB] transition-colors">{skill.name}</h3>
                <p className="text-xs text-[#64748B] line-clamp-2">{skill.recommendation}</p>
                <div className="mt-3 flex items-center text-[#2563EB] text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                  View Recommendation <ChevronRight className="w-3 h-3 ml-1" />
                </div>
              </button>
            ))}
          </motion.div>
        )}

        {/* Section B: Evidence Grid */}
        <motion.div
          data-tutorial="evidence-grid"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-[#2563EB]" />
              <h2 className="text-[#0F172A]">Evidence Grid</h2>
            </div>
            
            {/* View Mode Toggle */}
            <div className="flex bg-white p-1 rounded-lg border border-[#E2E8F0]">
              <button
                onClick={() => setViewMode("all")}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                  viewMode === "all" 
                    ? "bg-[#F1F5F9] text-[#0F172A]" 
                    : "text-[#64748B] hover:text-[#0F172A]"
                }`}
              >
                All Skills
              </button>
              <button
                data-tutorial="critical-toggle"
                onClick={() => setViewMode("critical")}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                  viewMode === "critical" 
                    ? "bg-[#FEF2F2] text-[#991B1B]" 
                    : "text-[#64748B] hover:text-[#991B1B]"
                }`}
              >
                <Filter className="w-3 h-3" />
                Critical Only
              </button>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] border border-[#E2E8F0] p-5 sm:p-6 min-h-[300px]">
            {sortedCategories.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-48 text-center">
                <CheckCircle2 className="w-10 h-10 text-[#22C55E] mb-3 opacity-20" />
                <p className="text-[#64748B] font-medium">No critical gaps found!</p>
                <p className="text-xs text-[#94A3B8]">You are fully matched in these categories.</p>
                <button 
                  onClick={() => setViewMode("all")}
                  className="mt-3 text-[#2563EB] text-xs hover:underline"
                >
                  View all skills
                </button>
              </div>
            ) : (
              <div className="space-y-5">
                {sortedCategories.map(category => (
                  <div key={category}>
                    <span className="text-xs text-[#94A3B8] uppercase tracking-wider">{category}</span>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {grouped[category].map(skill => (
                        <button
                          key={skill.id}
                          onClick={() => {
                            if (skill.status !== "match") setSelectedSkill(skill);
                          }}
                          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm transition-all ${
                            skill.status === "match"
                              ? "bg-[#F0FDF4] text-[#166534] border border-[#BBF7D0]"
                              : skill.status === "gap"
                              ? "bg-[#FEF2F2] text-[#991B1B] border border-[#FECACA] cursor-pointer hover:shadow-md hover:scale-105"
                              : "bg-[#FFFBEB] text-[#92400E] border border-[#FDE68A] cursor-pointer hover:shadow-md hover:scale-105"
                          }`}
                        >
                          <div
                            className={`w-1.5 h-1.5 rounded-full ${
                              skill.status === "match"
                                ? "bg-[#22C55E]"
                                : skill.status === "gap"
                                ? "bg-[#EF4444]"
                                : "bg-[#F59E0B]"
                            }`}
                          />
                          {skill.name}
                          {skill.status !== "match" && (
                            <Zap className="w-3 h-3 opacity-50" />
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <p className="mt-5 text-xs text-[#94A3B8] text-center">
              Click on a <span className="text-[#EF4444]">Gap</span> or <span className="text-[#F59E0B]">Partial</span> skill to see strategic recommendations
            </p>
          </div>
        </motion.div>

        {/* removed bottom Optimization Studio card - now at top right */}
      </div>

      {/* Gap Drawer */}
      <GapDrawer 
        skill={selectedSkill} 
        onClose={() => setSelectedSkill(null)} 
        onNext={handleNext}
        onPrev={handlePrev}
        hasNext={hasNext}
        hasPrev={hasPrev}
      />

      {/* Tutorial Overlay */}
      <TutorialOverlay
        show={showTutorial}
        onClose={() => {
          setShowTutorial(false);
          localStorage.setItem("strategylab-results-tutorial-seen", "true");
        }}
        steps={RESULTS_TUTORIAL_STEPS}
      />
    </div>
  );
}