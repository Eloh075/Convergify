import { X, TrendingUp, AlertTriangle, Lightbulb, ChevronLeft, ChevronRight } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import type { SkillItem } from "./AppContext";

interface GapDrawerProps {
  skill: SkillItem | null;
  onClose: () => void;
  onNext?: () => void;
  onPrev?: () => void;
  hasNext?: boolean;
  hasPrev?: boolean;
}

export function GapDrawer({ skill, onClose, onNext, onPrev, hasNext, hasPrev }: GapDrawerProps) {
  const isGap = skill?.status === "gap";
  const isPartial = skill?.status === "partial";

  return (
    <AnimatePresence>
      {skill && (
        <>
          {/* Backdrop */}
          <motion.div
            key="gap-drawer-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-[60]"
          />
          {/* Drawer */}
          <motion.div
            key="gap-drawer-panel"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-white shadow-2xl z-[70] flex flex-col"
          >
            {/* Header */}
            <div className={`px-6 py-5 border-b ${isGap ? "bg-red-50 border-red-100" : "bg-amber-50 border-amber-100"}`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${isGap ? "bg-red-100" : "bg-amber-100"}`}>
                    <AlertTriangle className={`w-5 h-5 ${isGap ? "text-red-600" : "text-amber-600"}`} />
                  </div>
                  <div>
                    <h3 className="text-[#0F172A] font-semibold">{skill.name}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      isGap ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"
                    }`}>
                      {isGap ? "Critical Gap" : "Partial Match"}
                    </span>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-[#94A3B8] hover:text-[#0F172A] hover:bg-black/5 transition-colors cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Navigation */}
              <div className="flex justify-between items-center pt-2">
                <button
                  onClick={onPrev}
                  disabled={!hasPrev}
                  className={`flex items-center gap-1 text-xs font-medium px-2 py-1 rounded transition-colors ${
                    hasPrev 
                      ? "text-[#64748B] hover:text-[#0F172A] hover:bg-black/5 cursor-pointer" 
                      : "text-gray-300 cursor-not-allowed"
                  }`}
                >
                  <ChevronLeft className="w-3 h-3" /> Previous
                </button>
                <button
                  onClick={onNext}
                  disabled={!hasNext}
                  className={`flex items-center gap-1 text-xs font-medium px-2 py-1 rounded transition-colors ${
                    hasNext 
                      ? "text-[#64748B] hover:text-[#0F172A] hover:bg-black/5 cursor-pointer" 
                      : "text-gray-300 cursor-not-allowed"
                  }`}
                >
                  Next <ChevronRight className="w-3 h-3" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 p-6 space-y-6 overflow-y-auto bg-white">
              {/* Market Demand */}
              <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-4 h-4 text-[#2563EB]" />
                  <span className="text-sm font-medium text-[#0F172A]">Market Demand</span>
                </div>
                <div className="flex items-end gap-2">
                  <span className="text-[#0F172A] font-bold" style={{ fontSize: "2rem", lineHeight: 1 }}>
                    {skill.marketDemand}%
                  </span>
                  <span className="text-sm text-[#64748B] mb-1.5">of similar roles require this</span>
                </div>
                <div className="mt-4 h-2 rounded-full bg-[#E2E8F0] overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${skill.marketDemand}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className="h-full rounded-full bg-gradient-to-r from-[#2563EB] to-[#7C3AED]"
                  />
                </div>
              </div>

              {/* Category */}
              <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Category</span>
                <p className="text-sm text-[#0F172A] mt-1 font-medium">{skill.category}</p>
              </div>

              {/* Recommendation */}
              {skill.recommendation && (
                <div className="p-4 rounded-xl bg-[#FFFBEB] border border-[#FDE68A]">
                  <div className="flex items-center gap-2 mb-3">
                    <Lightbulb className="w-4 h-4 text-[#F59E0B]" />
                    <span className="text-sm font-medium text-[#92400E]">Strategic Recommendation</span>
                  </div>
                  <p className="text-sm text-[#78350F] leading-relaxed">
                    {skill.recommendation}
                  </p>
                </div>
              )}

              {/* Resume Evidence */}
              {skill.resumeEvidence && (
                <div className="p-4 rounded-xl bg-[#F0FDF4] border border-[#BBF7D0]">
                  <span className="text-xs font-semibold text-[#15803D] uppercase tracking-wider">Your Resume Evidence</span>
                  <p className="text-sm text-[#166534] mt-1">{skill.resumeEvidence}</p>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}