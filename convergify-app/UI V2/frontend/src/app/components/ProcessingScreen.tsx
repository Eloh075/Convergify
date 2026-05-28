import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { motion, AnimatePresence } from "motion/react";
import { Check, Loader2, Terminal } from "lucide-react";

const steps = [
  { label: "[Parser] Extracting skills from Anchor Job...", duration: 1800 },
  { label: "[Market] Benchmarking against 10 AI Industry roles...", duration: 2200 },
  { label: "[Classifier] Mapping semantic equivalents (Generative AI → AI)...", duration: 1600 },
  { label: "[Consultant] Identifying 14 match points and 5 critical gaps...", duration: 2000 },
  { label: "[Optimizer] Generating strategic resume enhancements...", duration: 1500 },
  { label: "[Report] Compiling career strategy dashboard...", duration: 1200 },
];

export function ProcessingScreen() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);

  useEffect(() => {
    if (activeStep >= steps.length) {
      const timer = setTimeout(() => {
        navigate(`/results/${id}`, { replace: true });
      }, 600);
      return () => clearTimeout(timer);
    }

    const timer = setTimeout(() => {
      setCompletedSteps(prev => [...prev, activeStep]);
      setActiveStep(prev => prev + 1);
    }, steps[activeStep].duration);

    return () => clearTimeout(timer);
  }, [activeStep, id, navigate]);

  return (
    <div className="flex-1 flex items-center justify-center p-6 bg-[#0F172A] relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#2563EB]/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#7C3AED]/5 rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-xl"
      >
        {/* Terminal Window */}
        <div className="rounded-2xl overflow-hidden border border-[#1E293B] shadow-2xl bg-[#0B1120]">
          {/* Terminal Header */}
          <div className="flex items-center gap-2 px-4 py-3 bg-[#111827] border-b border-[#1E293B]">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-[#EF4444]" />
              <div className="w-3 h-3 rounded-full bg-[#F59E0B]" />
              <div className="w-3 h-3 rounded-full bg-[#22C55E]" />
            </div>
            <div className="flex items-center gap-1.5 ml-3">
              <Terminal className="w-3.5 h-3.5 text-[#64748B]" />
              <span className="text-xs text-[#64748B]" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                strategy-lab — processing
              </span>
            </div>
          </div>

          {/* Terminal Body */}
          <div className="p-6 space-y-4" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
            <AnimatePresence mode="popLayout">
              {steps.map((step, i) => {
                const isCompleted = completedSteps.includes(i);
                const isActive = activeStep === i;
                const isVisible = i <= activeStep;

                if (!isVisible) return null;

                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    className="flex items-start gap-3"
                  >
                    <div className="mt-0.5 flex-shrink-0">
                      {isCompleted ? (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="w-5 h-5 rounded-full bg-[#22C55E]/20 flex items-center justify-center"
                        >
                          <Check className="w-3 h-3 text-[#22C55E]" />
                        </motion.div>
                      ) : isActive ? (
                        <div className="w-5 h-5 flex items-center justify-center">
                          <Loader2 className="w-4 h-4 text-[#2563EB] animate-spin" />
                        </div>
                      ) : (
                        <div className="w-5 h-5 rounded-full bg-[#1E293B]" />
                      )}
                    </div>
                    <span
                      className={`text-xs leading-relaxed transition-colors duration-300 ${
                        isCompleted
                          ? "text-[#64748B]"
                          : isActive
                          ? "text-[#E2E8F0]"
                          : "text-[#334155]"
                      }`}
                    >
                      {step.label}
                    </span>
                  </motion.div>
                );
              })}
            </AnimatePresence>

            {/* Cursor blink */}
            {activeStep < steps.length && (
              <motion.div
                animate={{ opacity: [1, 0] }}
                transition={{ duration: 0.8, repeat: Infinity, repeatType: "reverse" }}
                className="w-2 h-4 bg-[#2563EB] ml-8"
              />
            )}

            {activeStep >= steps.length && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-2 pt-2"
              >
                <div className="w-5 h-5 rounded-full bg-[#22C55E]/20 flex items-center justify-center">
                  <Check className="w-3 h-3 text-[#22C55E]" />
                </div>
                <span className="text-xs text-[#22C55E]">
                  Strategy complete. Redirecting to dashboard...
                </span>
              </motion.div>
            )}
          </div>

          {/* Progress bar */}
          <div className="h-1 bg-[#1E293B]">
            <motion.div
              className="h-full bg-gradient-to-r from-[#2563EB] to-[#7C3AED]"
              initial={{ width: "0%" }}
              animate={{ width: `${(completedSteps.length / steps.length) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      </motion.div>
    </div>
  );
}
