import { useState } from "react";
import { Download, FileDown, FileText, PenLine } from "lucide-react";
import { motion } from "motion/react";

interface OptimizationStudioProps {
  originalResume: string;
  optimizedResume: string;
}

function renderResumeMarkdown(text: string, isOptimized: boolean) {
  const lines = text.split("\n");
  return lines.map((line, i) => {
    // Handle highlighted text (==text==)
    if (isOptimized && line.includes("==")) {
      const parts = line.split(/==(.*?)==/g);
      const rendered = parts.map((part, j) => {
        if (j % 2 === 1) {
          return (
            <span
              key={j}
              className="bg-[#F59E0B]/15 text-[#92400E] px-1 rounded border-b-2 border-[#F59E0B]/40"
            >
              {part}
            </span>
          );
        }
        return <span key={j}>{formatInlineMarkdown(part)}</span>;
      });

      if (line.startsWith("- ")) {
        return (
          <div key={i} className="flex gap-2 pl-4 py-0.5">
            <span className="text-[#94A3B8] flex-shrink-0">•</span>
            <span className="text-sm leading-relaxed text-[#334155]">{rendered}</span>
          </div>
        );
      }

      return (
        <div key={i} className="py-0.5">
          <span className="text-sm leading-relaxed text-[#334155]">{rendered}</span>
        </div>
      );
    }

    // Headers
    if (line.startsWith("# ")) {
      return (
        <h2 key={i} className="text-[#0F172A] mt-2 mb-1">
          {line.replace("# ", "")}
        </h2>
      );
    }
    if (line.startsWith("## ")) {
      return (
        <h3 key={i} className="text-[#64748B] mb-3">
          {line.replace("## ", "")}
        </h3>
      );
    }
    if (line.startsWith("### ")) {
      return (
        <h4 key={i} className="text-[#2563EB] mt-4 mb-2 pb-1 border-b border-[#E2E8F0]">
          {line.replace("### ", "")}
        </h4>
      );
    }

    // Bullet points
    if (line.startsWith("- ")) {
      return (
        <div key={i} className="flex gap-2 pl-4 py-0.5">
          <span className="text-[#94A3B8] flex-shrink-0">•</span>
          <span className="text-sm leading-relaxed text-[#334155]">
            {formatInlineMarkdown(line.replace("- ", ""))}
          </span>
        </div>
      );
    }

    // Empty lines
    if (line.trim() === "") {
      return <div key={i} className="h-2" />;
    }

    // Regular text
    return (
      <p key={i} className="text-sm text-[#334155] leading-relaxed">
        {formatInlineMarkdown(line)}
      </p>
    );
  });
}

function formatInlineMarkdown(text: string) {
  const parts = text.split(/\*\*(.*?)\*\*/g);
  return parts.map((part, i) => {
    if (i % 2 === 1) {
      return <strong key={i} className="text-[#0F172A]">{part}</strong>;
    }
    return <span key={i}>{part}</span>;
  });
}

export function OptimizationStudio({ originalResume, optimizedResume }: OptimizationStudioProps) {
  const [editedResume, setEditedResume] = useState(optimizedResume);
  const [isEditing, setIsEditing] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-[#0F172A]">Optimization Studio</h2>
        <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-[#FFFBEB] border border-[#FDE68A]">
          <div className="w-3 h-3 rounded bg-[#F59E0B]/20 border border-[#F59E0B]/40" />
          <span className="text-xs text-[#92400E]">AI Enhancements</span>
        </div>
      </div>

      <div data-tutorial="optimization-diff" className="bg-white rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] border border-[#E2E8F0] overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-[#E2E8F0]">
          {/* Left: Original */}
          <div className="flex flex-col">
            <div className="px-5 py-3 bg-[#F8FAFC] border-b border-[#E2E8F0] flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#94A3B8]" />
              <span className="text-sm text-[#64748B]">Your Current Resume</span>
            </div>
            <div className="p-5 opacity-60 overflow-y-auto max-h-[600px]">
              {renderResumeMarkdown(originalResume, false)}
            </div>
          </div>

          {/* Right: Optimized */}
          <div className="flex flex-col">
            <div className="px-5 py-3 bg-[#FFFBEB]/50 border-b border-[#E2E8F0] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <PenLine className="w-4 h-4 text-[#F59E0B]" />
                <span className="text-sm text-[#92400E]">Strategically Optimized Resume</span>
              </div>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="text-xs px-2 py-1 rounded-md border border-[#E2E8F0] text-[#64748B] hover:text-[#2563EB] hover:border-[#2563EB]/30 transition-colors cursor-pointer"
              >
                {isEditing ? "Preview" : "Edit"}
              </button>
            </div>
            <div className="p-5 overflow-y-auto max-h-[600px]">
              {isEditing ? (
                <textarea
                  value={editedResume}
                  onChange={e => setEditedResume(e.target.value)}
                  className="w-full h-[560px] p-3 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] text-sm text-[#334155] resize-none focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30"
                  style={{ fontFamily: "'JetBrains Mono', monospace" }}
                />
              ) : (
                renderResumeMarkdown(editedResume, true)
              )}
            </div>
          </div>
        </div>

        {/* Floating Bar */}
        <div data-tutorial="export-tools" className="px-5 py-4 bg-[#F8FAFC] border-t border-[#E2E8F0] flex flex-col sm:flex-row items-center justify-center gap-3">
          <button className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#0F172A] text-white hover:bg-[#1E293B] transition-colors cursor-pointer text-sm">
            <Download className="w-4 h-4" />
            Download Analysis PDF
          </button>
          <button className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2563EB] text-white hover:bg-[#1D4ED8] transition-colors cursor-pointer text-sm">
            <FileDown className="w-4 h-4" />
            Export Optimized Resume
          </button>
        </div>
      </div>
    </motion.div>
  );
}