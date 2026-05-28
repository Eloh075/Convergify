import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { Globe, ArrowRight, Building2, Briefcase, Target } from "lucide-react";
import { useAppContext } from "./AppContext";
import { motion } from "motion/react";
import { getTargetOptions } from "../../lib/api";
import { useApi } from "../../hooks/useApi";
import type { TargetOptionsResponse } from "../../types/api";

const browseJobs = [
  { title: "Senior AI Engineer", company: "TechVault AI", description: "Build and deploy cutting-edge ML models for enterprise clients. Requires PyTorch, Python, AWS, and client-facing communication skills." },
  { title: "ML Platform Engineer", company: "Anthropic", description: "Design and scale ML infrastructure. Strong MLOps, Kubernetes, and distributed systems experience required." },
  { title: "Applied Scientist", company: "OpenAI", description: "Research and implement novel AI architectures. PhD preferred. PyTorch, NLP, and publication record valued." },
  { title: "AI Solutions Architect", company: "Google Cloud", description: "Help enterprise customers implement AI solutions. Strong communication, cloud architecture, and ML deployment experience." },
  { title: "Staff ML Engineer", company: "Meta", description: "Lead ML systems at scale. Expertise in recommendation systems, PyTorch, and large-scale data processing." },
];

type AnalysisMode = 'job-posting' | 'market-role';

export function JobDescriptionStep() {
  const navigate = useNavigate();
  const { 
    draftJobText, setDraftJobText,
    draftRoleTitle, setDraftRoleTitle,
    draftCompany, setDraftCompany
  } = useAppContext();
  
  const [showBrowse, setShowBrowse] = useState(false);
  const [mode, setMode] = useState<AnalysisMode>('job-posting');
  
  // Market role selection state
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [selectedSpecialty, setSelectedSpecialty] = useState<string>('');
  const [selectedExperience, setSelectedExperience] = useState<string[]>([]);
  
  // Fetch target options
  const { data: targetOptions, loading: loadingOptions, error: optionsError, execute: fetchOptions } = useApi<TargetOptionsResponse, []>(getTargetOptions);
  
  useEffect(() => {
    // Fetch target options on mount
    fetchOptions();
  }, []);
  
  // Reset specialty when role changes
  useEffect(() => {
    setSelectedSpecialty('');
  }, [selectedRole]);

  const selectBrowseJob = (job: typeof browseJobs[0]) => {
    setDraftRoleTitle(job.title);
    setDraftCompany(job.company);
    setDraftJobText(job.description);
    setShowBrowse(false);
  };
  
  const toggleExperienceLevel = (level: string) => {
    setSelectedExperience(prev => 
      prev.includes(level) 
        ? prev.filter(l => l !== level)
        : [...prev, level]
    );
  };

  // Validation
  const isJobPostingValid = mode === 'job-posting' && draftRoleTitle.trim() && draftJobText.trim();
  const isMarketRoleValid = mode === 'market-role' && selectedRole && selectedExperience.length > 0;
  const isFormValid = isJobPostingValid || isMarketRoleValid;
  
  // Store mode and selections in context for next step
  const handleNext = () => {
    // Store analysis mode and selections
    localStorage.setItem('analysisMode', mode);
    if (mode === 'market-role') {
      localStorage.setItem('marketRoleSelection', JSON.stringify({
        role: selectedRole,
        specialty: selectedSpecialty || null,
        experience_levels: selectedExperience
      }));
    }
    navigate("/setup/resume");
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-8">
        {/* Mode Toggle */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center border border-blue-100">
              <Target className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-slate-900 font-semibold text-lg">Choose Your Analysis Mode</h2>
              <p className="text-slate-500 text-sm">How do you want to analyze your resume?</p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => setMode('job-posting')}
              className={`p-4 rounded-xl border-2 transition-all text-left ${
                mode === 'job-posting'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <Briefcase className={`w-5 h-5 ${mode === 'job-posting' ? 'text-blue-600' : 'text-slate-400'}`} />
                <span className={`font-semibold ${mode === 'job-posting' ? 'text-blue-900' : 'text-slate-700'}`}>
                  Specific Job Posting
                </span>
              </div>
              <p className="text-sm text-slate-600">
                Analyze against a specific job description you're targeting
              </p>
            </button>
            
            <button
              onClick={() => setMode('market-role')}
              className={`p-4 rounded-xl border-2 transition-all text-left ${
                mode === 'market-role'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <Globe className={`w-5 h-5 ${mode === 'market-role' ? 'text-blue-600' : 'text-slate-400'}`} />
                <span className={`font-semibold ${mode === 'market-role' ? 'text-blue-900' : 'text-slate-700'}`}>
                  Market Role Analysis
                </span>
              </div>
              <p className="text-sm text-slate-600">
                Compare against market data for a role category
              </p>
            </button>
          </div>
        </div>

        {/* Mode 1: Job Posting */}
        {mode === 'job-posting' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center border border-blue-100">
                  <Globe className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-slate-900 font-semibold">Define The Target</h3>
                  <p className="text-slate-500 text-sm">Paste the job posting you're targeting</p>
                </div>
              </div>
              
              <div className="relative">
                <button
                  onClick={() => setShowBrowse(!showBrowse)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:text-blue-600 hover:border-blue-200 hover:bg-blue-50 transition-all cursor-pointer text-sm font-medium"
                >
                  <Globe className="w-3.5 h-3.5" />
                  <span>Browse Samples</span>
                </button>

                {showBrowse && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute right-0 top-full mt-2 w-64 bg-white rounded-xl border border-slate-200 shadow-xl z-20 overflow-hidden"
                  >
                    <div className="py-1">
                      <div className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider bg-slate-50 border-b border-slate-100">
                        Sample Roles
                      </div>
                      {browseJobs.map((job, i) => (
                        <button
                          key={i}
                          onClick={() => selectBrowseJob(job)}
                          className="w-full text-left px-4 py-2 hover:bg-slate-50 transition-colors cursor-pointer group"
                        >
                          <div className="text-sm font-medium text-slate-700 group-hover:text-blue-700">{job.title}</div>
                          <div className="text-xs text-slate-500">{job.company}</div>
                        </button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-slate-400" />
                  Target Role Title
                </label>
                <input
                  type="text"
                  value={draftRoleTitle}
                  onChange={e => setDraftRoleTitle(e.target.value)}
                  placeholder="e.g. Senior Product Manager"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-slate-400" />
                  Target Company <span className="text-slate-400 font-normal">(Optional)</span>
                </label>
                <input
                  type="text"
                  value={draftCompany}
                  onChange={e => setDraftCompany(e.target.value)}
                  placeholder="e.g. Google"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">
                Job Description / Requirements
              </label>
              <textarea
                value={draftJobText}
                onChange={e => setDraftJobText(e.target.value)}
                placeholder="Paste the full job description here..."
                className="w-full h-48 p-4 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 placeholder-slate-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-mono text-sm leading-relaxed"
              />
            </div>
          </motion.div>
        )}

        {/* Mode 2: Market Role */}
        {mode === 'market-role' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center border border-blue-100">
                <Globe className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="text-slate-900 font-semibold">Select Market Role</h3>
                <p className="text-slate-500 text-sm">Choose the role category you're targeting</p>
              </div>
            </div>

            {loadingOptions ? (
              <div className="text-center py-8 text-slate-500">
                Loading market data...
              </div>
            ) : optionsError ? (
              <div className="p-4 rounded-xl bg-red-50 border border-red-200">
                <p className="text-sm text-red-900 font-medium mb-1">Failed to load market data</p>
                <p className="text-xs text-red-700">{optionsError}</p>
                <button
                  onClick={() => fetchOptions()}
                  className="mt-2 text-xs text-red-600 hover:text-red-800 underline"
                >
                  Retry
                </button>
              </div>
            ) : targetOptions ? (
              <div className="space-y-6">
                {/* Role Selection */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">
                    Job Role
                  </label>
                  <select
                    value={selectedRole}
                    onChange={e => setSelectedRole(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                  >
                    <option value="">Select a role...</option>
                    {targetOptions.roles.map(role => (
                      <option key={role} value={role}>{role}</option>
                    ))}
                  </select>
                </div>

                {/* Specialty Selection */}
                {selectedRole && targetOptions.specialties[selectedRole] && (
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">
                      Specialty <span className="text-slate-400 font-normal">(Optional)</span>
                    </label>
                    <select
                      value={selectedSpecialty}
                      onChange={e => setSelectedSpecialty(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                    >
                      <option value="">Generalist (All Specialties)</option>
                      {targetOptions.specialties[selectedRole].map(specialty => (
                        <option key={specialty} value={specialty}>{specialty}</option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Experience Level Multi-Select */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">
                    Experience Level <span className="text-slate-500 text-xs">(Select one or more)</span>
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {targetOptions.experience_levels.map(level => (
                      <button
                        key={level}
                        onClick={() => toggleExperienceLevel(level)}
                        className={`px-4 py-2.5 rounded-xl border-2 transition-all text-sm font-medium ${
                          selectedExperience.includes(level)
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-slate-200 bg-slate-50 text-slate-700 hover:border-slate-300'
                        }`}
                      >
                        {level}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Selection Summary */}
                {selectedRole && selectedExperience.length > 0 && (
                  <div className="p-4 rounded-xl bg-blue-50 border border-blue-100">
                    <p className="text-sm text-blue-900 font-medium mb-1">Analysis Target:</p>
                    <p className="text-sm text-blue-700">
                      {selectedRole}
                      {selectedSpecialty && ` / ${selectedSpecialty}`}
                      {' / '}
                      {selectedExperience.join(' + ')}
                    </p>
                    <p className="text-xs text-blue-600 mt-2">
                      Your resume will be compared against market data for this role category
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500">
                No market data available
              </div>
            )}
          </motion.div>
        )}
      </div>

      <div className="px-8 py-5 flex justify-end border-t border-slate-100 bg-slate-50/50">
        <button
          onClick={handleNext}
          disabled={!isFormValid}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl text-white transition-all cursor-pointer font-medium shadow-sm ${
            isFormValid
              ? "bg-blue-600 hover:bg-blue-700 shadow-blue-200 hover:shadow-blue-300 translate-y-0"
              : "bg-slate-300 cursor-not-allowed shadow-none"
          }`}
        >
          <span>Next: Upload Resume</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
