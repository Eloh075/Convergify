import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import { ChevronRight, X } from "lucide-react";

export interface TutorialStep {
  selector: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  position: "bottom" | "top" | "left" | "right";
}

interface SpotlightRect {
  top: number;
  left: number;
  width: number;
  height: number;
}

interface Props {
  show: boolean;
  steps: TutorialStep[];
  onClose: () => void;
}

export function TutorialOverlay({ show, steps, onClose }: Props) {
  const [step, setStep] = useState(0);
  const [rect, setRect] = useState<SpotlightRect | null>(null);
  const [ready, setReady] = useState(false);

  const current = steps[step];

  // Reset when opening
  useEffect(() => {
    if (show) {
      setStep(0);
      setReady(false);
      const t = setTimeout(() => setReady(true), 80);
      return () => clearTimeout(t);
    }
  }, [show]);

  const measureElement = useCallback(() => {
    if (!show || !ready || !current) return;
    const el = document.querySelector(current.selector);
    if (el) {
      const r = el.getBoundingClientRect();
      const padding = 8;
      setRect({
        top: r.top - padding,
        left: r.left - padding,
        width: r.width + padding * 2,
        height: r.height + padding * 2,
      });
      const viewportH = window.innerHeight;
      const isLarge = r.height > viewportH * 0.7;
      
      if (r.top < 0 || r.bottom > viewportH) {
        el.scrollIntoView({ 
          behavior: "smooth", 
          block: isLarge ? "start" : "center" 
        });
        setTimeout(() => {
          const r2 = el.getBoundingClientRect();
          setRect({
            top: r2.top - padding,
            left: r2.left - padding,
            width: r2.width + padding * 2,
            height: r2.height + padding * 2,
          });
        }, 400);
      }
    } else {
      setRect(null);
    }
  }, [current?.selector, show, ready]);

  useEffect(() => {
    measureElement();
    window.addEventListener("resize", measureElement);
    window.addEventListener("scroll", measureElement, true);
    return () => {
      window.removeEventListener("resize", measureElement);
      window.removeEventListener("scroll", measureElement, true);
    };
  }, [measureElement]);

  const handleNext = () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      onClose();
    }
  };

  // Tooltip positioning
  const getTooltipStyle = (): React.CSSProperties => {
    if (!rect || !current) return { top: "50%", left: "50%", transform: "translate(-50%, -50%)" };

    const pos = current.position;
    const gap = 14;
    const tooltipHeight = 160; // Approximate max height

    // Handle large elements or restricted viewport space
    if (pos === "top") {
      // If not enough space above, place inside at the top (sticky behavior)
      if (rect.top < tooltipHeight + gap) {
        return {
          position: "fixed",
          top: Math.max(gap + 16, rect.top + gap), // Stick to top with padding
          left: Math.max(16, Math.min(rect.left + rect.width / 2, window.innerWidth - 150)),
          transform: "translateX(-50%)",
        };
      }
      return {
        position: "fixed",
        bottom: window.innerHeight - rect.top + gap,
        left: Math.max(16, Math.min(rect.left + rect.width / 2, window.innerWidth - 150)),
        transform: "translateX(-50%)",
      };
    }

    if (pos === "bottom") {
      return {
        position: "fixed",
        top: rect.top + rect.height + gap,
        left: Math.max(16, Math.min(rect.left + rect.width / 2, window.innerWidth - 150)),
        transform: "translateX(-50%)",
      };
    }
    if (pos === "top") {
      return {
        position: "fixed",
        bottom: window.innerHeight - rect.top + gap,
        left: Math.max(16, Math.min(rect.left + rect.width / 2, window.innerWidth - 150)),
        transform: "translateX(-50%)",
      };
    }
    if (pos === "right") {
      const leftPos = rect.left + rect.width + gap;
      if (leftPos + 260 > window.innerWidth) {
        return {
          position: "fixed",
          top: rect.top + rect.height + gap,
          left: Math.max(16, Math.min(rect.left + rect.width / 2, window.innerWidth - 150)),
          transform: "translateX(-50%)",
        };
      }
      return {
        position: "fixed",
        top: rect.top + rect.height / 2,
        left: leftPos,
        transform: "translateY(-50%)",
      };
    }
    return {
      position: "fixed",
      top: rect.top + rect.height / 2,
      right: window.innerWidth - rect.left + gap,
      transform: "translateY(-50%)",
    };
  };

  if (!current) return null;

  return (
    <AnimatePresence>
      {show && ready && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="fixed inset-0 z-[9999]"
        >
          {/* Clickable dark backdrop */}
          <div
            className="fixed inset-0"
            style={{ zIndex: 9998 }}
            onClick={handleNext}
          />

          {/* Spotlight cutout */}
          {rect && (
            <motion.div
              key={`spotlight-${step}`}
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="rounded-xl border-2 border-[#2563EB]/50"
              style={{
                position: "fixed",
                top: rect.top,
                left: rect.left,
                width: rect.width,
                height: rect.height,
                zIndex: 10000,
                pointerEvents: "none",
                boxShadow:
                  "0 0 0 9999px rgba(15, 23, 42, 0.72), 0 0 24px rgba(37, 99, 235, 0.25)",
                background: "transparent",
              }}
            />
          )}

          {/* Tooltip card */}
          <motion.div
            key={`tooltip-${step}`}
            initial={{ opacity: 0, y: 6, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.18, delay: 0.08 }}
            style={{ ...getTooltipStyle(), zIndex: 10001 }}
            className="w-[250px]"
          >
            <div className="bg-white rounded-xl shadow-[0_8px_32px_rgba(0,0,0,0.24)] border border-[#E2E8F0] overflow-hidden">
              {/* Header */}
              <div className="px-3.5 py-2.5 flex items-center justify-between bg-[#F8FAFC] border-b border-[#E2E8F0]">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded bg-[#2563EB] flex items-center justify-center text-white">
                    {current.icon}
                  </div>
                  <span className="text-sm text-[#0F172A] font-medium">{current.title}</span>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); onClose(); }}
                  className="text-[#94A3B8] hover:text-[#64748B] cursor-pointer p-0.5"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Body */}
              <div className="px-3.5 py-2.5">
                <p className="text-xs text-[#64748B] leading-relaxed">{current.description}</p>
              </div>

              {/* Footer */}
              <div className="px-3.5 py-2 flex items-center justify-between border-t border-[#F1F5F9]">
                <div className="flex items-center gap-1">
                  {steps.map((_, i) => (
                    <div
                      key={i}
                      className={`w-1.5 h-1.5 rounded-full transition-all duration-200 ${
                        i === step ? "bg-[#2563EB] scale-125" : i < step ? "bg-[#93C5FD]" : "bg-[#E2E8F0]"
                      }`}
                    />
                  ))}
                </div>

                <button
                  onClick={(e) => { e.stopPropagation(); handleNext(); }}
                  className="flex items-center gap-0.5 text-xs text-[#2563EB] font-medium hover:text-[#1D4ED8] cursor-pointer"
                >
                  {step === steps.length - 1 ? "Got it" : "Next"}
                  {step < steps.length - 1 && <ChevronRight className="w-3 h-3" />}
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
