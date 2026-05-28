import { FlaskConical, Plus, Archive, HelpCircle } from "lucide-react";
import { useNavigate, useLocation } from "react-router";
import { useAppContext } from "./AppContext";

export function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const { showTutorial, setShowTutorial, clearDraftState } = useAppContext();
  const isLab = location.pathname === "/lab";
  const isResults = location.pathname.startsWith("/results/");
  const isOptimization = location.pathname.startsWith("/optimization/");

  const handleNewAnalysis = () => {
    clearDraftState();
    navigate("/");
  };

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between px-6 py-3 bg-[#0F172A] border-b border-[#1E293B]">
      <button
        onClick={handleNewAnalysis}
        className="flex items-center gap-2.5 text-white hover:opacity-90 transition-opacity cursor-pointer"
      >
        <div className="w-8 h-8 rounded-lg bg-[#2563EB] flex items-center justify-center">
          <FlaskConical className="w-4.5 h-4.5 text-white" />
        </div>
        <span className="text-white tracking-tight" style={{ fontFamily: "Inter, sans-serif" }}>
          The Strategy Lab
        </span>
      </button>

      <div className="flex items-center gap-2">
        {(isResults || isOptimization) && (
          <button
            onClick={() => setShowTutorial(true)}
            className="flex items-center justify-center w-8 h-8 rounded-lg text-slate-400 hover:text-white hover:bg-[#1E293B] transition-all cursor-pointer"
            title="Quick tour"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
        )}
        {!isLab && location.pathname !== "/" && (
          <button
            onClick={handleNewAnalysis}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-[#1E293B] transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span className="text-sm">New Analysis</span>
          </button>
        )}
        <button
          data-tutorial="lab-btn"
          onClick={() => {
            if (isLab) {
              // If in archive, go back to home
              navigate("/");
            } else {
              // If not in archive, go to archive
              navigate("/lab");
            }
          }}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all cursor-pointer ${
            isLab
              ? "bg-[#2563EB] text-white"
              : "text-slate-300 hover:text-white hover:bg-[#1E293B]"
          }`}
        >
          <Archive className="w-4 h-4" />
          <span className="text-sm">Archive</span>
        </button>
      </div>
    </header>
  );
}