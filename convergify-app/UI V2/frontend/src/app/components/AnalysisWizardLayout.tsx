import { Outlet, useLocation } from "react-router";
import { StrategyTimeline } from "./StrategyTimeline";

export function AnalysisWizardLayout() {
  const location = useLocation();
  
  // Determine current step index
  const getCurrentStepIndex = () => {
    if (location.pathname === "/" || location.pathname === "/setup/target") return 0;
    if (location.pathname === "/setup/resume") return 1;
    if (location.pathname.startsWith("/processing")) return 2;
    return 0;
  };

  const currentStepIndex = getCurrentStepIndex();

  return (
    <div className="flex-1 flex flex-col bg-gradient-to-br from-slate-50 via-white to-blue-50 min-h-screen">
      {/* Timeline Header */}
      <div className="w-full bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-[57px] z-40 shadow-sm">
        <StrategyTimeline currentStepIndex={currentStepIndex} />
      </div>

      {/* Content Area */}
      <div className="flex-1 flex flex-col items-center p-6 md:p-12 animate-in fade-in duration-500">
        <div className="w-full max-w-4xl">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
