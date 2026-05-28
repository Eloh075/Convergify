import { useState, useRef } from "react";
import { useNavigate } from "react-router";
import { Upload, CheckCircle2, Sparkles, FileText, ArrowRight } from "lucide-react";
import { useAppContext } from "./AppContext";
import { fileToBase64, analyzeMarketRole, analyzeJobPosting } from "../../lib/api";
import { transformMarketRoleAnalysis, transformJobPostingAnalysis } from "../../lib/transformers";
import { useApi } from "../../hooks/useApi";
import type { MarketRoleAnalysisResponse, JobPostingAnalysisResponse } from "../../types/api";

export function ResumeUploadStep() {
  const navigate = useNavigate();
  const { 
    addAnalysis, 
    draftJobText, 
    draftRoleTitle,
    draftCompany,
    draftFileName, 
    setDraftFileName,
    clearDraftState,
  } = useAppContext();
  
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && (file.name.endsWith(".pdf") || file.name.endsWith(".docx"))) {
      setDraftFileName(file.name);
      setUploadedFile(file);
      setError(null);
    } else {
      setError("Please upload a PDF or DOCX file");
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setDraftFileName(file.name);
      setUploadedFile(file);
      setError(null);
    }
  };

  const handleBackToTarget = () => {
    clearDraftState();
    setUploadedFile(null);
    navigate("/");
  };

  const generateStrategy = async () => {
    if (!draftFileName || !uploadedFile) return;
    
    setIsAnalyzing(true);
    setError(null);
    
    try {
      console.log('Starting file conversion...', uploadedFile.name, uploadedFile.size);
      
      // Convert file to base64
      const base64File = await fileToBase64(uploadedFile);
      console.log('File converted to base64, length:', base64File.length);
      
      // Get analysis mode from localStorage
      const mode = localStorage.getItem('analysisMode') as 'job-posting' | 'market-role' | null;
      
      if (!mode) {
        throw new Error('Analysis mode not found. Please go back and select a target.');
      }
      
      let analysis;
      
      if (mode === 'market-role') {
        // Market role analysis
        const marketRoleSelection = localStorage.getItem('marketRoleSelection');
        if (!marketRoleSelection) {
          throw new Error('Market role selection not found. Please go back and select a role.');
        }
        
        const { role, specialty, experience_levels } = JSON.parse(marketRoleSelection);
        console.log('Calling API with:', { role, specialty, experience_levels, fileSize: base64File.length });
        
        const response = await analyzeMarketRole({
          role,
          specialty,
          experience_levels,
          resume_file: base64File
        }) as MarketRoleAnalysisResponse;
        
        console.log('API response received:', response);
        
        // For resume text, use a placeholder since we can't easily extract from PDF/DOCX in browser
        const resumeText = `Resume file: ${draftFileName}`;
        analysis = transformMarketRoleAnalysis(
          response,
          resumeText,
          `${role}${specialty ? ` - ${specialty}` : ''}`,
          `Market Analysis (${experience_levels.join(', ')})`
        );
        
      } else {
        // Job posting analysis
        if (!draftRoleTitle || !draftJobText) {
          throw new Error('Job details not found. Please go back and enter job information.');
        }
        
        console.log('Calling API with job posting mode');
        
        const response = await analyzeJobPosting({
          job_title: draftRoleTitle,
          company: draftCompany || undefined,
          job_description: draftJobText,
          resume_file: base64File
        }) as JobPostingAnalysisResponse;
        
        console.log('API response received:', response);
        
        // For resume text, use a placeholder since we can't easily extract from PDF/DOCX in browser
        const resumeText = `Resume file: ${draftFileName}`;
        analysis = transformJobPostingAnalysis(
          response,
          resumeText,
          draftRoleTitle,
          draftCompany || 'Target Company',
          draftJobText
        );
      }
      
      // Add analysis to context and navigate
      addAnalysis(analysis);
      navigate(`/processing/${analysis.id}`);
      
    } catch (err: any) {
      console.error('Analysis error:', err);
      setError(err.response?.data?.error || err.message || 'Failed to analyze resume. Please try again.');
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-8">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center border border-blue-100">
            <FileText className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-slate-900 font-semibold text-xl">Your Baseline</h2>
            <p className="text-slate-500 text-sm">Upload your resume to compare against the target.</p>
          </div>
        </div>

        <div
          data-tutorial="resume-area"
          onDragOver={e => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleFileDrop}
          onClick={() => fileRef.current?.click()}
          className={`h-64 flex flex-col items-center justify-center rounded-xl border-2 border-dashed cursor-pointer transition-all duration-300 ${
            isDragging
              ? "border-blue-500 bg-blue-50 scale-[1.02]"
              : draftFileName
              ? "border-emerald-400 bg-emerald-50"
              : "border-slate-300 bg-slate-50 hover:border-blue-400 hover:bg-blue-50/50"
          }`}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileSelect}
            className="hidden"
          />
          {draftFileName ? (
            <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
              <CheckCircle2 className="w-16 h-16 text-emerald-500 mb-4 drop-shadow-sm" />
              <p className="text-xl font-semibold text-emerald-700">{draftFileName}</p>
              <p className="text-sm text-emerald-600 mt-2 bg-emerald-100 px-3 py-1 rounded-full">Ready for Analysis</p>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 rounded-full bg-white flex items-center justify-center mb-4 shadow-sm border border-slate-100">
                <Upload className="w-8 h-8 text-slate-400" />
              </div>
              <p className="text-lg font-medium text-slate-600">Drag & Drop Resume</p>
              <p className="text-sm text-slate-400 mt-2">Supports PDF or DOCX</p>
            </div>
          )}
        </div>
      </div>

      <div className="px-8 py-5 border-t border-slate-100 bg-slate-50/50">
        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200">
            <p className="text-sm text-red-900">{error}</p>
          </div>
        )}
        
        <div className="flex items-center justify-between">
            <button
                onClick={handleBackToTarget}
                disabled={isAnalyzing}
                className="text-slate-500 hover:text-slate-900 text-sm font-medium px-4 py-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
                Back to Target
            </button>
            <button
                onClick={generateStrategy}
                disabled={!draftFileName || isAnalyzing}
                className={`flex items-center gap-2 px-8 py-3.5 rounded-xl text-white transition-all font-medium shadow-md ${
                draftFileName && !isAnalyzing
                    ? "bg-blue-600 hover:bg-blue-700 shadow-blue-200 hover:shadow-blue-300 cursor-pointer"
                    : "bg-slate-300 cursor-not-allowed shadow-none"
                }`}
            >
                <Sparkles className={`w-5 h-5 ${isAnalyzing ? 'animate-spin' : ''}`} />
                <span>{isAnalyzing ? 'Analyzing...' : 'Generate Strategy'}</span>
            </button>
        </div>
      </div>
    </div>
  );
}
