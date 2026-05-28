import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router";
import { motion } from "motion/react";
import { ArrowLeft, ChevronDown, ChevronUp, ArrowRight, Database, AlertCircle } from "lucide-react";
import { getAnalysisResult, type AnalysisResponse, type MarketSkill } from "../../lib/api";
import { useAppContext } from "./AppContext";

export function MarketIntelligenceDashboard() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { clearDraftState } = useAppContext();
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [bonusExpanded, setBonusExpanded] = useState(false);

  useEffect(() => {
    const fetchAnalysisData = async () => {
      if (!id) {
        setError("No analysis ID provided");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const result = await getAnalysisResult(id);
        
        if (!result) {
          throw new Error("Invalid analysis data received");
        }

        setAnalysisData(result);
      } catch (err) {
        console.error("Error fetching analysis:", err);
        setError(err instanceof Error ? err.message : "Failed to connect to server");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysisData();
  }, [id]);

  const handleNewAnalysis = () => {
    clearDraftState();
    navigate("/");
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-slate-900 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-slate-600">Loading market intelligence...</p>
        </div>
      </div>
    );
  }

  if (error || !analysisData) {
    return (
      <div className="flex-1 flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-slate-400 mx-auto mb-3" />
          <p className="text-slate-600 mb-4">{error || "Analysis not found"}</p>
          <button
            onClick={handleNewAnalysis}
            className="px-4 py-2 rounded-lg bg-slate-900 text-white text-sm cursor-pointer hover:bg-slate-800 transition-colors"
          >
            Start New Analysis
          </button>
        </div>
      </div>
    );
  }

  const { market_context, match_score, dealbreakers, differentiators, bonus, summary } = analysisData;

  // Calculate match score color (spec: 0-49 rose, 50-74 amber, 75-100 emerald)
  const getScoreColor = (score: number) => {
    if (score >= 75) return "text-emerald-500";
    if (score >= 50) return "text-amber-500";
    return "text-rose-600";
  };

  const getScoreStroke = (score: number) => {
    if (score >= 75) return "#10b981"; // emerald-500
    if (score >= 50) return "#f59e0b"; // amber-500
    return "#dc2626"; // rose-600
  };

  // Render skill row using CSS Grid for perfect alignment
  const renderSkillRow = (skill: MarketSkill, hasSkill: boolean, isMissingDealbreaker: boolean) => {
    const percentage = Math.round(skill.frequency_percentage);
    
    // Determine styling based on match status and importance
    let iconColor, iconBg, textColor, barColor, showMissingBadge;
    
    if (hasSkill) {
      // Matched skill - green check
      iconColor = "text-white";
      iconBg = "bg-emerald-500";
      textColor = "text-slate-800";
      barColor = "bg-emerald-500";
      showMissingBadge = false;
    } else if (isMissingDealbreaker) {
      // Missing dealbreaker - bold red
      iconColor = "text-white";
      iconBg = "bg-rose-500";
      textColor = "text-rose-600 font-semibold";
      barColor = "bg-rose-500";
      showMissingBadge = true;
    } else {
      // Missing differentiator/bonus - muted gray
      iconColor = "text-slate-300";
      iconBg = "bg-transparent border-2 border-slate-300";
      textColor = "text-slate-500";
      barColor = "bg-slate-300";
      showMissingBadge = false;
    }
    
    return (
      <div 
        key={skill.canonical_name} 
        className="grid grid-cols-[auto_150px_1fr_60px_100px] gap-3 items-center py-2"
      >
        {/* Icon */}
        <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${iconBg} ${iconColor}`}>
          {hasSkill ? "✓" : (isMissingDealbreaker ? "✕" : "○")}
        </div>
        
        {/* Skill Name */}
        <span className={`text-sm ${textColor} truncate`}>
          {skill.canonical_name}
        </span>
        
        {/* Progress Bar */}
        <div className="bg-slate-100 h-3 rounded-full overflow-hidden">
          <div 
            className={`h-full ${barColor} transition-all duration-500`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        
        {/* Percentage (monospace) */}
        <span className={`text-sm font-mono font-semibold ${textColor} text-right`}>
          {percentage}%
        </span>
        
        {/* Job Count (monospace) */}
        <div className="flex items-center justify-end gap-2">
          <span className="text-xs font-mono text-slate-500">
            ({skill.unique_jobs} jobs)
          </span>
          {showMissingBadge && (
            <span className="text-xs font-semibold text-rose-600">◀ MISSING</span>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="flex-1 bg-slate-50 min-h-screen">
      <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
        {/* Back Button */}
        <button
          onClick={handleNewAnalysis}
          className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors cursor-pointer text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>New Analysis</span>
        </button>

        {/* Target Market Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow-sm border border-slate-200 p-6"
        >
          {/* Breadcrumb-style tags */}
          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              {market_context.role}
            </span>
            <span className="text-slate-400">▶</span>
            <span className="text-sm font-bold text-slate-700 uppercase tracking-wide">
              {market_context.specialty || "Generalist"}
            </span>
            <span className="text-slate-400">▶</span>
            <span className="text-sm font-bold text-slate-600 uppercase tracking-wide">
              {market_context.experience_levels.join(" & ")}
            </span>
          </div>
          
          {/* Data context with icon */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Database className="w-4 h-4" />
              <span>
                Intelligence pulled from <span className="font-mono font-semibold text-slate-900">{market_context.job_count}</span> local jobs
              </span>
            </div>
            {market_context.job_count < 10 && (
              <div className="flex items-center gap-1.5 px-3 py-1 bg-amber-50 border border-amber-200 rounded">
                <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                <span className="text-xs font-medium text-amber-900">
                  Limited data - results may not be fully accurate
                </span>
              </div>
            )}
          </div>
        </motion.div>

        {/* Market Verdict Hero Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-sm border border-slate-200 p-8"
        >
          <div className="flex items-start gap-8">
            {/* Left: Text (70%) */}
            <div className="flex-[7]">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                Market Verdict
              </div>
              <p className="text-lg text-slate-900 leading-relaxed">
                You possess <span className="font-semibold font-mono">{dealbreakers.matched.length}</span> of <span className="font-semibold font-mono">{summary.must_have_count}</span> core requirements, 
                but are missing <span className="font-semibold text-rose-600">{dealbreakers.gaps.length} critical skills</span> that this specific market demands.
              </p>
            </div>
            
            {/* Right: Gauge (30%) */}
            <div className="flex-[3] flex flex-col items-center gap-2">
              <div className="relative">
                <svg className="w-32 h-32 transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="#f1f5f9"
                    strokeWidth="10"
                    fill="none"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke={getScoreStroke(match_score)}
                    strokeWidth="10"
                    fill="none"
                    strokeDasharray={`${2 * Math.PI * 56}`}
                    strokeDashoffset={`${2 * Math.PI * 56 * (1 - match_score / 100)}`}
                    strokeLinecap="round"
                    className="transition-all duration-1000"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={`text-4xl font-bold font-mono ${getScoreColor(match_score)}`}>
                    {match_score}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Gap Analysis Matrix */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-6"
        >
          {/* Dealbreakers Section */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 border-t-4 border-t-rose-500 p-6">
            <div className="mb-2">
              <h3 className="text-base font-bold text-slate-900 uppercase tracking-wide mb-1">
                🔴 Dealbreakers (&gt;60%)
              </h3>
              <p className="text-sm text-slate-500">
                Required by majority of jobs. You have matched <span className="font-mono font-semibold text-slate-900">{dealbreakers.matched.length}</span> of <span className="font-mono font-semibold text-slate-900">{summary.must_have_count}</span>.
              </p>
            </div>
            
            <div className="mt-4 space-y-1">
              {[...dealbreakers.matched, ...dealbreakers.gaps]
                .sort((a, b) => b.frequency_percentage - a.frequency_percentage)
                .map(skill => renderSkillRow(skill, dealbreakers.matched.includes(skill), !dealbreakers.matched.includes(skill)))}
            </div>
          </div>

          {/* Differentiators Section */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 border-t-4 border-t-amber-400 p-6">
            <div className="mb-2">
              <h3 className="text-base font-bold text-slate-900 uppercase tracking-wide mb-1">
                🟡 Differentiators (30-59%)
              </h3>
              <p className="text-sm text-slate-500">
                Found in 30-59% of jobs. Adding these puts you in the top 50% of applicants.
              </p>
            </div>
            
            <div className="mt-4 space-y-1">
              {[...differentiators.matched, ...differentiators.gaps]
                .sort((a, b) => b.frequency_percentage - a.frequency_percentage)
                .map(skill => renderSkillRow(skill, differentiators.matched.includes(skill), false))}
            </div>
          </div>

          {/* Bonus Section (Collapsed Accordion) */}
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
            <button
              onClick={() => setBonusExpanded(!bonusExpanded)}
              className="flex items-center justify-between w-full text-left"
            >
              <div>
                <h3 className="text-base font-bold text-slate-900 uppercase tracking-wide mb-1">
                  🟢 Bonus / Niche (&lt;30%)
                </h3>
                {!bonusExpanded && (
                  <p className="text-sm text-slate-500">
                    ▶ Expand <span className="font-mono font-semibold">{summary.preferred_count}</span> Preferred Skills
                  </p>
                )}
              </div>
              {bonusExpanded ? (
                <ChevronUp className="w-5 h-5 text-slate-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-slate-400" />
              )}
            </button>
            
            {bonusExpanded && (
              <div className="mt-4 space-y-1">
                {[...bonus.matched, ...bonus.gaps]
                  .sort((a, b) => b.frequency_percentage - a.frequency_percentage)
                  .map(skill => renderSkillRow(skill, bonus.matched.includes(skill), false))}
              </div>
            )}
          </div>
        </motion.div>

        {/* Cliffhanger CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-slate-900 text-white rounded-lg shadow-lg p-8"
        >
          <p className="text-slate-300 text-sm mb-4 text-center">
            Your resume formatting, bullet points, and structure need adjustments to properly sell these skills to recruiters.
          </p>
          <div className="flex justify-center">
            <button
              onClick={() => navigate(`/resume-analysis/${id}`)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-slate-900 rounded-lg font-semibold hover:bg-slate-100 transition-all cursor-pointer group"
            >
              <span>VIEW RESUME EDITS & ACTION PLAN</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
