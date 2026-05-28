import { motion } from "motion/react";
import { CheckCircle2, Globe, FileText, Sparkles } from "lucide-react";
import { useAppContext } from "./AppContext";

interface StrategyTimelineProps {
  currentStepIndex: number;
}

export function StrategyTimeline({ currentStepIndex }: StrategyTimelineProps) {
  const { draftRoleTitle, draftCompany } = useAppContext();

  const steps = [
    { 
      id: "target", 
      label: "Target Role", 
      sublabel: draftRoleTitle ? `${draftRoleTitle}${draftCompany ? ` at ${draftCompany}` : ""}` : "Define Destination",
      icon: Globe 
    },
    { 
      id: "resume", 
      label: "Current Baseline", 
      sublabel: "Upload Resume",
      icon: FileText 
    },
    { 
      id: "analysis", 
      label: "Strategy Gap", 
      sublabel: "Analysis & Plan",
      icon: Sparkles 
    },
  ];

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between w-full relative">
        {/* Progress Line Background */}
        <div className="absolute top-5 left-0 w-full h-0.5 bg-slate-200 -z-10" />
        
        {/* Active Progress Line */}
        <motion.div 
          className="absolute top-5 left-0 h-0.5 bg-blue-600 -z-10 origin-left"
          initial={{ scaleX: 0 }}
          animate={{ scaleX: currentStepIndex / (steps.length - 1) }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
          style={{ width: "100%" }}
        />

        {steps.map((step, index) => {
          const isActive = index === currentStepIndex;
          const isCompleted = index < currentStepIndex;
          const Icon = step.icon;

          return (
            <div key={step.id} className="flex flex-col items-center relative z-10 group cursor-default w-32">
              <motion.div 
                initial={false}
                animate={{
                  backgroundColor: isCompleted ? "#2563EB" : isActive ? "#EFF6FF" : "#FFFFFF",
                  borderColor: isCompleted || isActive ? "#2563EB" : "#E2E8F0",
                  scale: isActive ? 1.1 : 1,
                }}
                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300 ${
                  isCompleted ? "text-white" : isActive ? "text-blue-600" : "text-slate-400"
                }`}
              >
                {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : <Icon className="w-5 h-5" />}
              </motion.div>
              
              <div className="mt-3 flex flex-col items-center text-center">
                <span className={`text-sm font-semibold transition-colors duration-300 ${
                  isActive ? "text-slate-900" : isCompleted ? "text-blue-700" : "text-slate-500"
                }`}>
                  {step.label}
                </span>
                <span className="text-xs text-slate-500 max-w-[140px] truncate mt-0.5">
                  {step.sublabel}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
