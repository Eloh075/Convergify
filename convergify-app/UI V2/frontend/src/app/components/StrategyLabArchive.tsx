import { useState } from "react";
import { useNavigate } from "react-router";
import { motion, AnimatePresence } from "motion/react";
import { Eye, Download, Trash2, Search, FileText, ToggleLeft, ToggleRight, TrendingUp } from "lucide-react";
import { useAppContext } from "./AppContext";

export function StrategyLabArchive() {
  const navigate = useNavigate();
  const { analyses, deleteAnalysis } = useAppContext();
  const [search, setSearch] = useState("");
  const [showVault, setShowVault] = useState(false);

  const filtered = analyses.filter(
    a =>
      a.jobTitle.toLowerCase().includes(search.toLowerCase()) ||
      a.company.toLowerCase().includes(search.toLowerCase())
  );

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-[#22C55E] bg-[#F0FDF4]";
    if (score >= 60) return "text-[#2563EB] bg-[#EFF6FF]";
    if (score >= 40) return "text-[#F59E0B] bg-[#FFFBEB]";
    return "text-[#EF4444] bg-[#FEF2F2]";
  };

  const resumeVersions = [
    { name: "Jane_Mitchell_Resume_v3.pdf", lastOptimized: "2026-02-18", bestScore: 85 },
    { name: "Jane_Mitchell_Resume_v2.pdf", lastOptimized: "2026-02-10", bestScore: 72 },
    { name: "Jane_Mitchell_Resume_v1.pdf", lastOptimized: "2026-01-28", bestScore: 65 },
  ];

  return (
    <div className="flex-1 bg-gradient-to-br from-[#F8FAFC] via-white to-[#EFF6FF]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-[#0F172A]">Strategy Lab</h1>
            <p className="text-sm text-[#64748B] mt-1">
              Your analysis archive — {analyses.length} strategies analyzed
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowVault(!showVault)}
              className="flex items-center gap-2 cursor-pointer text-sm"
            >
              {showVault ? (
                <ToggleRight className="w-7 h-4 text-[#2563EB]" />
              ) : (
                <ToggleLeft className="w-7 h-4 text-[#94A3B8]" />
              )}
              <span className={showVault ? "text-[#0F172A]" : "text-[#94A3B8]"}>
                Resume Vault
              </span>
            </button>
          </div>
        </div>

        {/* Resume Vault */}
        <AnimatePresence>
          {showVault && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 overflow-hidden"
            >
              <div className="bg-white rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] border border-[#E2E8F0] p-5">
                <div className="flex items-center gap-2 mb-4">
                  <FileText className="w-4 h-4 text-[#2563EB]" />
                  <span className="text-sm text-[#0F172A]">Resume Vault</span>
                </div>
                <div className="space-y-2">
                  {resumeVersions.map((r, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]"
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="w-4 h-4 text-[#94A3B8]" />
                        <div>
                          <p className="text-sm text-[#0F172A]">{r.name}</p>
                          <p className="text-xs text-[#94A3B8]">
                            Last optimized: {r.lastOptimized}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-1">
                          <TrendingUp className="w-3 h-3 text-[#2563EB]" />
                          <span className="text-xs text-[#2563EB]">Best: {r.bestScore}%</span>
                        </div>
                        <button className="text-[#94A3B8] hover:text-[#2563EB] transition-colors cursor-pointer">
                          <Download className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#94A3B8]" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by job title or company..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#E2E8F0] bg-white text-sm text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 focus:border-[#2563EB] transition-all"
          />
        </div>

        {/* Table */}
        <div className="bg-white rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] border border-[#E2E8F0] overflow-hidden">
          {/* Header */}
          <div className="hidden sm:grid grid-cols-[1fr_140px_100px_120px_100px] px-5 py-3 bg-[#F8FAFC] border-b border-[#E2E8F0] text-xs text-[#94A3B8] uppercase tracking-wider">
            <span>Target Job</span>
            <span>Company</span>
            <span className="text-center">Match Score</span>
            <span className="text-center">Date Analyzed</span>
            <span className="text-center">Actions</span>
          </div>

          {/* Rows */}
          <div className="divide-y divide-[#E2E8F0]">
            <AnimatePresence>
              {filtered.length === 0 ? (
                <div className="p-8 text-center text-[#94A3B8] text-sm">
                  {search ? "No analyses match your search." : "No analyses yet. Start your first analysis!"}
                </div>
              ) : (
                filtered.map(analysis => (
                  <motion.div
                    key={analysis.id}
                    layout
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0, height: 0 }}
                    className="grid grid-cols-1 sm:grid-cols-[1fr_140px_100px_120px_100px] items-center px-5 py-4 hover:bg-[#F8FAFC] transition-colors gap-2 sm:gap-0"
                  >
                    <div>
                      <p className="text-sm text-[#0F172A]">{analysis.jobTitle}</p>
                      <p className="sm:hidden text-xs text-[#64748B]">{analysis.company} · {analysis.date}</p>
                    </div>
                    <span className="hidden sm:block text-sm text-[#64748B]">{analysis.company}</span>
                    <div className="hidden sm:flex justify-center">
                      <span className={`text-sm px-2.5 py-1 rounded-full ${getScoreColor(analysis.matchScore)}`}>
                        {analysis.matchScore}%
                      </span>
                    </div>
                    <span className="hidden sm:block text-sm text-[#64748B] text-center">{analysis.date}</span>
                    <div className="flex items-center justify-end sm:justify-center gap-1">
                      <span className={`sm:hidden text-sm px-2.5 py-1 rounded-full ${getScoreColor(analysis.matchScore)}`}>
                        {analysis.matchScore}%
                      </span>
                      <div className="flex-1" />
                      <button
                        onClick={() => navigate(`/results/${analysis.id}`)}
                        className="w-8 h-8 rounded-lg flex items-center justify-center text-[#94A3B8] hover:text-[#2563EB] hover:bg-[#EFF6FF] transition-all cursor-pointer"
                        title="View"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        className="w-8 h-8 rounded-lg flex items-center justify-center text-[#94A3B8] hover:text-[#2563EB] hover:bg-[#EFF6FF] transition-all cursor-pointer"
                        title="Download"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteAnalysis(analysis.id)}
                        className="w-8 h-8 rounded-lg flex items-center justify-center text-[#94A3B8] hover:text-[#EF4444] hover:bg-[#FEF2F2] transition-all cursor-pointer"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </motion.div>
                ))
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
