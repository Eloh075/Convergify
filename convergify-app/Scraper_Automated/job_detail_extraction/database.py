"""Database operations for job details."""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger
from supabase import create_client, Client

from .models import JobDetails


class JobDetailDatabase:
    """Database operations for storing job details."""
    
    def __init__(self):
        """Initialize with Supabase client from environment."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not found in environment")
            self.supabase = None
        else:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("JobDetailDatabase initialized with Supabase client")
    
    def save_job_details(self, job_details: JobDetails) -> bool:
        """Save job details to database."""
        try:
            if not self.supabase:
                logger.warning("No Supabase client available, skipping database save")
                return False
            
            # Get job_role from job_listings if not set
            if not job_details.job_role or job_details.job_role == "":
                try:
                    listing = self.supabase.table("job_listings").select("job_role").eq("url", job_details.url).execute()
                    if listing.data and len(listing.data) > 0:
                        job_details.job_role = listing.data[0].get("job_role", "")
                        logger.debug(f"Retrieved job_role from job_listings: {job_details.job_role}")
                except Exception as e:
                    logger.warning(f"Could not retrieve job_role from job_listings: {e}")
            
            # Convert to dictionary for job_details table
            details_data = {
                "url": job_details.url,
                "job_role": job_details.job_role,
                "job_title": job_details.job_title,
                "company": job_details.company,
                "location": job_details.location,
                "date_posted": job_details.date_posted,
                "application_deadline": job_details.application_deadline,
                "job_type": job_details.job_type,
                "experience_level": job_details.experience_level,
                "seniority_level": job_details.seniority_level,
                "salary_range": job_details.salary_range,
                "industry": job_details.industry,
                "category": job_details.category,
                "description": job_details.description,
                "skills": job_details.skills,  # Will be stored as JSON array
                "extracted_at": job_details.extracted_at.isoformat() if job_details.extracted_at else None,
                "error_message": job_details.error_message,
                "raw_data": job_details.raw_data,
            }
            
            # Remove None values
            details_data = {k: v for k, v in details_data.items() if v is not None}
            
            # Check if record exists in job_details table
            existing = self.supabase.table("job_details").select("*").eq("url", job_details.url).execute()
            
            if existing.data:
                # Update existing record in job_details
                result = self.supabase.table("job_details").update(details_data).eq("url", job_details.url).execute()
                logger.info(f"Updated job details for {job_details.url}")
            else:
                # Insert new record in job_details
                result = self.supabase.table("job_details").insert(details_data).execute()
                logger.info(f"Inserted new job details for {job_details.url}")
            
            # Also update the job_listings table to mark as extracted
            if job_details.success:
                self.supabase.table("job_listings").update({
                    "extracted": True,
                    "extracted_at": job_details.extracted_at.isoformat() if job_details.extracted_at else None,
                }).eq("url", job_details.url).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving job details to database: {e}")
            return False
    
    def get_jobs_to_extract(self, limit: int = 100, website: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get jobs that need detail extraction."""
        try:
            if not self.supabase:
                logger.warning("No Supabase client available")
                return []
            
            # Simple query: get jobs from job_listings that haven't been extracted
            query = self.supabase.table("job_listings").select("*").eq("extracted", False)
            
            if website:
                query = query.eq("website", website)
            
            result = query.limit(limit).execute()
            
            logger.info(f"Found {len(result.data)} jobs to extract")
            return result.data
            
        except Exception as e:
            logger.error(f"Error getting jobs to extract: {e}")
            return []
    
    def mark_as_extracted(self, url: str, success: bool = True, error_message: Optional[str] = None) -> bool:
        """Mark job as extracted (successfully or not)."""
        try:
            if not self.supabase:
                return False
            
            # Update job_listings table
            update_data = {
                "extracted": success,
                "extracted_at": datetime.now().isoformat() if success else None,
            }
            
            if error_message and not success:
                update_data["extraction_error"] = error_message
            
            result = self.supabase.table("job_listings").update(update_data).eq("url", url).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking job as extracted: {e}")
            return False
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get extraction statistics."""
        try:
            if not self.supabase:
                return {}
            
            # Get total jobs
            total_result = self.supabase.table("job_listings").select("count", count="exact").execute()
            total_jobs = total_result.count or 0
            
            # Get extracted jobs
            extracted_result = self.supabase.table("job_listings").select("count", count="exact").eq("extracted", True).execute()
            extracted_jobs = extracted_result.count or 0
            
            # Get by website
            website_result = self.supabase.table("job_listings").select("website, count(*)").group("website").execute()
            website_stats = {item["website"]: item["count"] for item in website_result.data}
            
            # Get by job role
            role_result = self.supabase.table("job_listings").select("job_role, count(*)").group("job_role").execute()
            role_stats = {item["job_role"]: item["count"] for item in role_result.data}
            
            return {
                "total_jobs": total_jobs,
                "extracted_jobs": extracted_jobs,
                "pending_extraction": total_jobs - extracted_jobs,
                "extraction_rate": (extracted_jobs / total_jobs * 100) if total_jobs > 0 else 0,
                "by_website": website_stats,
                "by_role": role_stats,
            }
            
        except Exception as e:
            logger.error(f"Error getting extraction stats: {e}")
            return {}