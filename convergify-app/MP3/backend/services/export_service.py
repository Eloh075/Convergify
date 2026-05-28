"""
Export and reporting service for generating various output formats
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json
import csv
import io
import tempfile
import os
from pathlib import Path

from models.resume import Resume, OptimizedResume
from models.job import Job, JobGroup
from models.analysis import Analysis

class ExportService:
    """Service for exporting data in various formats"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "career_analysis_exports"
        self.temp_dir.mkdir(exist_ok=True)
    
    def export_analysis_report(self, analysis_id: str, format: str, db: Session) -> Optional[Dict[str, Any]]:
        """
        Export comprehensive analysis report
        
        Args:
            analysis_id: Analysis ID to export
            format: Export format (pdf, json, csv)
            db: Database session
            
        Returns:
            Dictionary with export information
        """
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis or not analysis.results_dict:
            return None
        
        # Get related data
        resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
        jobs = []
        if analysis.job_ids_list:
            jobs = db.query(Job).filter(Job.id.in_(analysis.job_ids_list)).all()
        
        # Prepare export data
        export_data = {
            "analysis_info": {
                "id": analysis.id,
                "type": analysis.analysis_type,
                "status": analysis.status,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None
            },
            "resume_info": {
                "id": resume.id if resume else None,
                "filename": resume.filename if resume else None,
                "skills": resume.skills_list if resume else []
            },
            "jobs_analyzed": [
                {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "skills": job.skills_list or []
                }
                for job in jobs
            ],
            "results": analysis.results_dict,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if format == "json":
            return self._export_json(export_data, f"analysis_report_{analysis_id}")
        elif format == "csv":
            return self._export_analysis_csv(export_data, analysis_id)
        elif format == "pdf":
            return self._export_analysis_pdf(export_data, analysis_id)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_resume_data(self, resume_id: str, format: str, include_analyses: bool,
                          include_optimizations: bool, db: Session) -> Optional[Dict[str, Any]]:
        """
        Export complete resume data
        
        Args:
            resume_id: Resume ID to export
            format: Export format
            include_analyses: Include analysis history
            include_optimizations: Include optimization history
            db: Database session
            
        Returns:
            Dictionary with export information
        """
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return None
        
        export_data = {
            "resume": {
                "id": resume.id,
                "filename": resume.filename,
                "file_size": resume.file_size,
                "analysis_status": resume.analysis_status,
                "skills": resume.skills_list,
                "created_at": resume.created_at.isoformat() if resume.created_at else None,
                "updated_at": resume.updated_at.isoformat() if resume.updated_at else None,
                "original_text": resume.original_text
            }
        }
        
        if include_analyses:
            analyses = db.query(Analysis).filter(Analysis.resume_id == resume_id).all()
            export_data["analyses"] = [
                {
                    "id": analysis.id,
                    "type": analysis.analysis_type,
                    "status": analysis.status,
                    "job_ids": analysis.job_ids_list,
                    "results": analysis.results_dict,
                    "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                    "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None
                }
                for analysis in analyses
            ]
        
        if include_optimizations:
            optimized_resumes = db.query(OptimizedResume).filter(
                OptimizedResume.original_resume_id == resume_id
            ).all()
            export_data["optimizations"] = [
                {
                    "id": opt.id,
                    "optimized_text": opt.optimized_text,
                    "changes": opt.changes_list,
                    "improvement_score": opt.improvement_score,
                    "target_jobs": opt.target_jobs_list,
                    "created_at": opt.created_at.isoformat() if opt.created_at else None
                }
                for opt in optimized_resumes
            ]
        
        export_data["generated_at"] = datetime.now(timezone.utc).isoformat()
        
        if format == "json":
            return self._export_json(export_data, f"resume_data_{resume_id}")
        elif format == "csv":
            return self._export_resume_csv(export_data, resume_id)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_jobs_data(self, format: str, group_id: Optional[str], include_skills: bool,
                        db: Session) -> Dict[str, Any]:
        """
        Export jobs data
        
        Args:
            format: Export format
            group_id: Optional group ID to filter jobs
            include_skills: Include extracted skills
            db: Database session
            
        Returns:
            Dictionary with export information
        """
        query = db.query(Job)
        
        if group_id:
            query = query.filter(Job.group_id == group_id)
        
        jobs = query.all()
        
        export_data = {
            "jobs": [
                {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "description": job.description,
                    "requirements": job.requirements,
                    "location": job.location,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "source": job.source,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "scraped_date": job.scraped_date.isoformat() if job.scraped_date else None,
                    **({"skills": job.skills_list} if include_skills else {})
                }
                for job in jobs
            ],
            "metadata": {
                "total_jobs": len(jobs),
                "group_id": group_id,
                "includes_skills": include_skills,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        if format == "json":
            return self._export_json(export_data, f"jobs_data_{group_id or 'all'}")
        elif format == "csv":
            return self._export_jobs_csv(export_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_session_backup(self, session_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Export complete session backup
        
        Args:
            session_data: Complete session data
            session_id: Session identifier
            
        Returns:
            Dictionary with export information
        """
        backup_data = {
            "session_id": session_id,
            "backup_version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": session_data
        }
        
        return self._export_json(backup_data, f"session_backup_{session_id}")
    
    def _export_json(self, data: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Export data as JSON file"""
        file_path = self.temp_dir / f"{filename}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return {
            "file_path": str(file_path),
            "filename": f"{filename}.json",
            "format": "json",
            "size": file_path.stat().st_size,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _export_analysis_csv(self, data: Dict[str, Any], analysis_id: str) -> Dict[str, Any]:
        """Export analysis data as CSV"""
        file_path = self.temp_dir / f"analysis_report_{analysis_id}.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write analysis info
            writer.writerow(["Analysis Report"])
            writer.writerow(["Analysis ID", data["analysis_info"]["id"]])
            writer.writerow(["Type", data["analysis_info"]["type"]])
            writer.writerow(["Status", data["analysis_info"]["status"]])
            writer.writerow(["Created", data["analysis_info"]["created_at"]])
            writer.writerow(["Completed", data["analysis_info"]["completed_at"]])
            writer.writerow([])
            
            # Write resume info
            writer.writerow(["Resume Information"])
            writer.writerow(["Resume ID", data["resume_info"]["id"]])
            writer.writerow(["Filename", data["resume_info"]["filename"]])
            writer.writerow(["Skills", ", ".join(data["resume_info"]["skills"])])
            writer.writerow([])
            
            # Write jobs analyzed
            if data["jobs_analyzed"]:
                writer.writerow(["Jobs Analyzed"])
                writer.writerow(["Job ID", "Title", "Company", "Location", "Skills"])
                for job in data["jobs_analyzed"]:
                    writer.writerow([
                        job["id"],
                        job["title"],
                        job["company"],
                        job["location"],
                        ", ".join(job["skills"])
                    ])
                writer.writerow([])
            
            # Write skill gaps if available
            results = data.get("results", {})
            if "career_analysis" in results and "skill_gaps" in results["career_analysis"]:
                writer.writerow(["Skill Gaps"])
                writer.writerow(["Skill", "Category", "Importance", "Market Demand"])
                for gap in results["career_analysis"]["skill_gaps"]:
                    writer.writerow([
                        gap.get("skill", ""),
                        gap.get("category", ""),
                        gap.get("importance", ""),
                        gap.get("market_demand", "")
                    ])
                writer.writerow([])
            
            # Write recommendations if available
            if "career_analysis" in results and "recommendations" in results["career_analysis"]:
                writer.writerow(["Recommendations"])
                writer.writerow(["Type", "Description"])
                recs = results["career_analysis"]["recommendations"]
                if isinstance(recs, dict):
                    for rec_type, rec_list in recs.items():
                        if isinstance(rec_list, list):
                            for rec in rec_list:
                                writer.writerow([rec_type, rec])
        
        return {
            "file_path": str(file_path),
            "filename": f"analysis_report_{analysis_id}.csv",
            "format": "csv",
            "size": file_path.stat().st_size,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _export_resume_csv(self, data: Dict[str, Any], resume_id: str) -> Dict[str, Any]:
        """Export resume data as CSV"""
        file_path = self.temp_dir / f"resume_data_{resume_id}.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write resume info
            writer.writerow(["Resume Data Export"])
            resume = data["resume"]
            writer.writerow(["Resume ID", resume["id"]])
            writer.writerow(["Filename", resume["filename"]])
            writer.writerow(["File Size", resume["file_size"]])
            writer.writerow(["Status", resume["analysis_status"]])
            writer.writerow(["Skills", ", ".join(resume["skills"] or [])])
            writer.writerow(["Created", resume["created_at"]])
            writer.writerow([])
            
            # Write analyses if included
            if "analyses" in data:
                writer.writerow(["Analysis History"])
                writer.writerow(["Analysis ID", "Type", "Status", "Created", "Completed", "Job Count"])
                for analysis in data["analyses"]:
                    writer.writerow([
                        analysis["id"],
                        analysis["type"],
                        analysis["status"],
                        analysis["created_at"],
                        analysis["completed_at"],
                        len(analysis["job_ids"])
                    ])
                writer.writerow([])
            
            # Write optimizations if included
            if "optimizations" in data:
                writer.writerow(["Optimization History"])
                writer.writerow(["Optimization ID", "Improvement Score", "Changes Count", "Created", "Target Jobs"])
                for opt in data["optimizations"]:
                    writer.writerow([
                        opt["id"],
                        opt["improvement_score"],
                        len(opt["changes"]),
                        opt["created_at"],
                        len(opt["target_jobs"])
                    ])
        
        return {
            "file_path": str(file_path),
            "filename": f"resume_data_{resume_id}.csv",
            "format": "csv",
            "size": file_path.stat().st_size,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _export_jobs_csv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Export jobs data as CSV"""
        file_path = self.temp_dir / f"jobs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            headers = ["Job ID", "Title", "Company", "Location", "Salary Min", "Salary Max", "Source", "Created", "Scraped"]
            if data["metadata"]["includes_skills"]:
                headers.append("Skills")
            writer.writerow(headers)
            
            # Write job data
            for job in data["jobs"]:
                row = [
                    job["id"],
                    job["title"],
                    job["company"],
                    job["location"],
                    job["salary_min"],
                    job["salary_max"],
                    job["source"],
                    job["created_at"],
                    job["scraped_date"]
                ]
                if data["metadata"]["includes_skills"]:
                    row.append(", ".join(job.get("skills", [])))
                writer.writerow(row)
        
        return {
            "file_path": str(file_path),
            "filename": file_path.name,
            "format": "csv",
            "size": file_path.stat().st_size,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _export_analysis_pdf(self, data: Dict[str, Any], analysis_id: str) -> Dict[str, Any]:
        """
        Export analysis as PDF report
        Note: This is a simplified implementation. In production, you'd use a proper PDF library like ReportLab
        """
        # For now, create a text-based report that could be converted to PDF
        file_path = self.temp_dir / f"analysis_report_{analysis_id}.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("CAREER ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Analysis info
            f.write("ANALYSIS INFORMATION\n")
            f.write("-" * 20 + "\n")
            f.write(f"Analysis ID: {data['analysis_info']['id']}\n")
            f.write(f"Type: {data['analysis_info']['type']}\n")
            f.write(f"Status: {data['analysis_info']['status']}\n")
            f.write(f"Created: {data['analysis_info']['created_at']}\n")
            f.write(f"Completed: {data['analysis_info']['completed_at']}\n\n")
            
            # Resume info
            f.write("RESUME INFORMATION\n")
            f.write("-" * 18 + "\n")
            f.write(f"Resume ID: {data['resume_info']['id']}\n")
            f.write(f"Filename: {data['resume_info']['filename']}\n")
            f.write(f"Skills: {', '.join(data['resume_info']['skills'])}\n\n")
            
            # Jobs analyzed
            if data["jobs_analyzed"]:
                f.write("JOBS ANALYZED\n")
                f.write("-" * 13 + "\n")
                for job in data["jobs_analyzed"]:
                    f.write(f"• {job['title']} at {job['company']}\n")
                    f.write(f"  Location: {job['location']}\n")
                    f.write(f"  Skills: {', '.join(job['skills'])}\n\n")
            
            # Analysis results
            results = data.get("results", {})
            if "career_analysis" in results:
                career_results = results["career_analysis"]
                
                # Skill gaps
                if "skill_gaps" in career_results:
                    f.write("SKILL GAPS IDENTIFIED\n")
                    f.write("-" * 21 + "\n")
                    for gap in career_results["skill_gaps"]:
                        f.write(f"• {gap.get('skill', 'Unknown')}\n")
                        f.write(f"  Category: {gap.get('category', 'N/A')}\n")
                        f.write(f"  Importance: {gap.get('importance', 'N/A')}\n")
                        f.write(f"  Market Demand: {gap.get('market_demand', 'N/A')}\n\n")
                
                # Recommendations
                if "recommendations" in career_results:
                    f.write("RECOMMENDATIONS\n")
                    f.write("-" * 15 + "\n")
                    recs = career_results["recommendations"]
                    if isinstance(recs, dict):
                        for rec_type, rec_list in recs.items():
                            f.write(f"\n{rec_type.upper()}:\n")
                            if isinstance(rec_list, list):
                                for rec in rec_list:
                                    f.write(f"• {rec}\n")
            
            f.write(f"\nReport generated on: {data['generated_at']}\n")
        
        return {
            "file_path": str(file_path),
            "filename": f"analysis_report_{analysis_id}.txt",
            "format": "txt",  # Would be PDF in production
            "size": file_path.stat().st_size,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def cleanup_temp_files(self, older_than_hours: int = 24):
        """Clean up temporary export files older than specified hours"""
        cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
        
        for file_path in self.temp_dir.glob("*"):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                except OSError:
                    pass  # File might be in use or already deleted
    
    def get_export_file(self, file_path: str) -> Optional[Path]:
        """Get export file if it exists and is in the temp directory"""
        path = Path(file_path)
        if path.exists() and path.parent == self.temp_dir:
            return path
        return None