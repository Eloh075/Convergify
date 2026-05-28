"""
Analysis management service
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from models.analysis import Analysis
from models.resume import Resume
from models.job import Job
from schemas.analysis import AnalysisCreateRequest, AnalysisResponse, AnalysisResultsResponse

class AnalysisService:
    """Service for analysis management operations"""
    
    def create_analysis(self, analysis_data: AnalysisCreateRequest, db: Session) -> AnalysisResponse:
        """Create a new analysis"""
        analysis = Analysis(
            resume_id=analysis_data.resume_id,
            job_ids_list=analysis_data.job_ids or [],
            analysis_type=analysis_data.analysis_type,
            status="pending"
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return AnalysisResponse.from_orm(analysis)
    
    def list_analyses(self, resume_id: Optional[str] = None, status: Optional[str] = None,
                     analysis_type: Optional[str] = None, skip: int = 0, limit: int = 100,
                     sort_by: str = "created_at", sort_order: str = "desc",
                     db: Session = None) -> List[AnalysisResponse]:
        """List analyses with filtering and sorting"""
        query = db.query(Analysis)
        
        if resume_id:
            query = query.filter(Analysis.resume_id == resume_id)
        
        if status:
            query = query.filter(Analysis.status == status)
        
        if analysis_type:
            query = query.filter(Analysis.analysis_type == analysis_type)
        
        # Apply sorting
        if hasattr(Analysis, sort_by):
            sort_column = getattr(Analysis, sort_by)
            if sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        analyses = query.offset(skip).limit(limit).all()
        return [AnalysisResponse.from_orm(analysis) for analysis in analyses]
    
    def get_analysis(self, analysis_id: str, db: Session) -> Optional[AnalysisResponse]:
        """Get a specific analysis by ID"""
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        return AnalysisResponse.from_orm(analysis) if analysis else None
    
    def get_analysis_results(self, analysis_id: str, db: Session) -> Optional[AnalysisResultsResponse]:
        """Get detailed results of an analysis"""
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis or not analysis.results_dict:
            return None
        
        # Get related resume and jobs for context
        resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
        jobs = []
        if analysis.job_ids_list:
            jobs = db.query(Job).filter(Job.id.in_(analysis.job_ids_list)).all()
        
        return AnalysisResultsResponse(
            analysis_id=analysis.id,
            resume_id=analysis.resume_id,
            resume_filename=resume.filename if resume else None,
            job_count=len(jobs),
            job_titles=[job.title for job in jobs],
            analysis_type=analysis.analysis_type,
            status=analysis.status,
            results=analysis.results_dict,
            created_at=analysis.created_at,
            completed_at=analysis.completed_at
        )
    
    def get_analysis_status(self, analysis_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get current status of an analysis"""
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return None
        
        return {
            "analysis_id": analysis.id,
            "status": analysis.status,
            "analysis_type": analysis.analysis_type,
            "task_id": analysis.task_id,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
            "started_at": analysis.started_at.isoformat() if analysis.started_at else None,
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
            "error_message": analysis.error_message,
            "progress_percentage": self._calculate_progress(analysis),
            "has_results": analysis.results_dict is not None
        }
    
    def update_analysis_status(self, analysis_id: str, status: str, db: Session) -> bool:
        """Update analysis status"""
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return False
        
        analysis.status = status
        
        if status == "running" and not analysis.started_at:
            analysis.started_at = datetime.now(timezone.utc)
        elif status in ["completed", "failed", "cancelled"] and not analysis.completed_at:
            analysis.completed_at = datetime.now(timezone.utc)
        
        db.commit()
        return True
    
    def update_analysis_task_id(self, analysis_id: str, task_id: str, db: Session) -> bool:
        """Update analysis task ID"""
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return False
        
        analysis.task_id = task_id
        db.commit()
        return True
    
    def delete_analysis(self, analysis_id: str, db: Session) -> bool:
        """Delete an analysis"""
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return False
        
        db.delete(analysis)
        db.commit()
        return True
    
    def export_analysis(self, analysis_id: str, format: str, include_raw_data: bool, db: Session) -> Optional[Dict[str, Any]]:
        """Export analysis results"""
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis or not analysis.results_dict:
            return None
        
        # Get related data
        resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
        jobs = []
        if analysis.job_ids_list:
            jobs = db.query(Job).filter(Job.id.in_(analysis.job_ids_list)).all()
        
        export_data = {
            "analysis_info": {
                "id": analysis.id,
                "analysis_type": analysis.analysis_type,
                "status": analysis.status,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None
            },
            "resume_info": {
                "id": resume.id if resume else None,
                "filename": resume.filename if resume else None
            },
            "jobs_info": [
                {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company
                }
                for job in jobs
            ],
            "results_summary": self._extract_results_summary(analysis.results_dict)
        }
        
        if include_raw_data:
            export_data["raw_results"] = analysis.results_dict
        
        return {
            "format": format,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "data": export_data
        }
    
    def get_analysis_recommendations(self, analysis_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get actionable recommendations from analysis"""
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis or not analysis.results_dict:
            return None
        
        results = analysis.results_dict
        recommendations = {
            "analysis_id": analysis.id,
            "immediate_actions": [],
            "skill_development": [],
            "career_guidance": [],
            "resume_improvements": []
        }
        
        # Extract recommendations from results
        if "career_analysis" in results:
            career_results = results["career_analysis"]
            
            if "recommendations" in career_results:
                career_recs = career_results["recommendations"]
                recommendations["immediate_actions"] = career_recs.get("immediate_actions", [])
                recommendations["skill_development"] = career_recs.get("skill_development", [])
                recommendations["career_guidance"] = career_recs.get("career_guidance", [])
            
            if "skill_gaps" in career_results:
                skill_gaps = career_results["skill_gaps"]
                recommendations["resume_improvements"] = [
                    f"Consider highlighting experience with {gap['skill']}"
                    for gap in skill_gaps[:5]  # Top 5 gaps
                ]
        
        return recommendations
    
    def get_skill_gaps(self, analysis_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get skill gap analysis"""
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis or not analysis.results_dict:
            return None
        
        results = analysis.results_dict
        skill_gaps = {
            "analysis_id": analysis.id,
            "gaps": [],
            "strengths": [],
            "summary": {}
        }
        
        # Extract skill gaps from results
        if "career_analysis" in results:
            career_results = results["career_analysis"]
            
            if "skill_gaps" in career_results:
                skill_gaps["gaps"] = career_results["skill_gaps"]
            
            if "skill_strengths" in career_results:
                skill_gaps["strengths"] = career_results["skill_strengths"]
            
            # Calculate summary
            total_gaps = len(skill_gaps["gaps"])
            total_strengths = len(skill_gaps["strengths"])
            
            skill_gaps["summary"] = {
                "total_gaps": total_gaps,
                "total_strengths": total_strengths,
                "gap_categories": self._categorize_skills([gap["skill"] for gap in skill_gaps["gaps"]]),
                "strength_categories": self._categorize_skills([strength["skill"] for strength in skill_gaps["strengths"]])
            }
        
        return skill_gaps
    
    def compare_analyses(self, analysis_id: str, compare_with_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Compare two analyses"""
        analysis1 = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        analysis2 = db.query(Analysis).filter(Analysis.id == compare_with_id).first()
        
        if not analysis1 or not analysis2 or not analysis1.results_dict or not analysis2.results_dict:
            return None
        
        comparison = {
            "analysis1": {
                "id": analysis1.id,
                "analysis_type": analysis1.analysis_type,
                "created_at": analysis1.created_at.isoformat() if analysis1.created_at else None
            },
            "analysis2": {
                "id": analysis2.id,
                "analysis_type": analysis2.analysis_type,
                "created_at": analysis2.created_at.isoformat() if analysis2.created_at else None
            },
            "differences": self._compare_results(analysis1.results_dict, analysis2.results_dict),
            "similarities": self._find_similarities(analysis1.results_dict, analysis2.results_dict)
        }
        
        return comparison
    
    def get_analysis_stats(self, db: Session) -> Dict[str, Any]:
        """Get analysis statistics"""
        total_analyses = db.query(Analysis).count()
        
        # Count by status
        status_counts = db.query(Analysis.status, db.func.count(Analysis.id)).group_by(Analysis.status).all()
        
        # Count by type
        type_counts = db.query(Analysis.analysis_type, db.func.count(Analysis.id)).group_by(Analysis.analysis_type).all()
        
        # Average completion time for completed analyses
        completed_analyses = db.query(Analysis).filter(
            Analysis.status == "completed",
            Analysis.started_at.isnot(None),
            Analysis.completed_at.isnot(None)
        ).all()
        
        avg_completion_time = None
        if completed_analyses:
            total_time = sum(
                (analysis.completed_at - analysis.started_at).total_seconds()
                for analysis in completed_analyses
            )
            avg_completion_time = total_time / len(completed_analyses)
        
        return {
            "total_analyses": total_analyses,
            "status_breakdown": {status: count for status, count in status_counts},
            "type_breakdown": {type_: count for type_, count in type_counts},
            "average_completion_time_seconds": avg_completion_time,
            "completed_analyses": len(completed_analyses)
        }
    
    def _calculate_progress(self, analysis: Analysis) -> int:
        """Calculate progress percentage for an analysis"""
        if analysis.status == "pending":
            return 0
        elif analysis.status == "running":
            return 50  # Rough estimate
        elif analysis.status == "completed":
            return 100
        elif analysis.status in ["failed", "cancelled"]:
            return 0
        else:
            return 25  # Default for unknown status
    
    def _extract_results_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key summary information from results"""
        summary = {}
        
        if "career_analysis" in results:
            career_results = results["career_analysis"]
            summary["career_analysis"] = {
                "skill_gaps_count": len(career_results.get("skill_gaps", [])),
                "recommendations_count": len(career_results.get("recommendations", {}).get("immediate_actions", [])),
                "overall_score": career_results.get("overall_score", 0)
            }
        
        if "skill_classification" in results:
            skill_results = results["skill_classification"]
            summary["skills"] = {
                "total_skills": len(skill_results.get("classified_skills", [])),
                "categories": list(skill_results.get("skill_categories", {}).keys())
            }
        
        return summary
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, int]:
        """Categorize skills into broad categories"""
        categories = {
            "technical": 0,
            "soft": 0,
            "domain": 0,
            "tools": 0
        }
        
        # Simple categorization logic (would be more sophisticated in practice)
        technical_keywords = ["programming", "coding", "development", "software", "algorithm"]
        soft_keywords = ["communication", "leadership", "teamwork", "management", "problem-solving"]
        tool_keywords = ["excel", "powerpoint", "jira", "git", "docker", "aws"]
        
        for skill in skills:
            skill_lower = skill.lower()
            if any(keyword in skill_lower for keyword in technical_keywords):
                categories["technical"] += 1
            elif any(keyword in skill_lower for keyword in soft_keywords):
                categories["soft"] += 1
            elif any(keyword in skill_lower for keyword in tool_keywords):
                categories["tools"] += 1
            else:
                categories["domain"] += 1
        
        return categories
    
    def _compare_results(self, results1: Dict[str, Any], results2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two analysis results"""
        differences = {}
        
        # Compare skill gaps
        if "career_analysis" in results1 and "career_analysis" in results2:
            gaps1 = set(gap["skill"] for gap in results1["career_analysis"].get("skill_gaps", []))
            gaps2 = set(gap["skill"] for gap in results2["career_analysis"].get("skill_gaps", []))
            
            differences["skill_gaps"] = {
                "only_in_first": list(gaps1 - gaps2),
                "only_in_second": list(gaps2 - gaps1),
                "common": list(gaps1 & gaps2)
            }
        
        return differences
    
    def _find_similarities(self, results1: Dict[str, Any], results2: Dict[str, Any]) -> Dict[str, Any]:
        """Find similarities between two analysis results"""
        similarities = {}
        
        # Find common recommendations
        if "career_analysis" in results1 and "career_analysis" in results2:
            recs1 = set(results1["career_analysis"].get("recommendations", {}).get("immediate_actions", []))
            recs2 = set(results2["career_analysis"].get("recommendations", {}).get("immediate_actions", []))
            
            similarities["common_recommendations"] = list(recs1 & recs2)
        
        return similarities