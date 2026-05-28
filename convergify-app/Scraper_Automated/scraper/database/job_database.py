"""Supabase MCP integration for job database operations."""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from loguru import logger


class JobDatabase:
    """Database operations for job listings using Supabase MCP."""
    
    def __init__(self, table_name: str = "job_listings"):
        """Initialize database with table name."""
        self.table_name = table_name
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and Key must be configured in .env file")
        
        # Initialize Supabase client
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        logger.info(f"JobDatabase initialized for table: {table_name}")
    
    def save_job_urls(self, urls: List[str], website: str, job_role: str) -> Dict[str, int]:
        """Save URLs to database, return count of new records."""
        saved_count = 0
        existing_count = 0
        
        for url in urls:
            if self.url_exists(url):
                # Update scraping timestamp for existing URL
                self._update_scraped_at(url)
                existing_count += 1
            else:
                # Insert new URL with metadata
                self._insert_job_url(url, website, job_role)
                saved_count += 1
        
        logger.info(f"Saved {saved_count} new URLs, {existing_count} existing URLs updated")
        return {"new": saved_count, "existing": existing_count}
    
    def save_job_urls_with_metadata(self, urls: List[str], website: str, job_role: str, metadata_list: List[Dict[str, Any]], experience_level: str = "", suffix: Optional[str] = None) -> Dict[str, int]:
        """Save URLs to database with metadata, return count of new records."""
        saved_count = 0
        existing_count = 0
        
        for i, url in enumerate(urls):
            if self.url_exists(url):
                # Update scraping timestamp for existing URL
                metadata = metadata_list[i] if i < len(metadata_list) else {}
                # Only use search experience_level if metadata doesn't have one
                if experience_level and not metadata.get("experience_level"):
                    metadata["experience_level"] = experience_level
                self._update_scraped_at_with_metadata(url, metadata, suffix)
                existing_count += 1
            else:
                # Insert new URL with metadata
                metadata = metadata_list[i] if i < len(metadata_list) else {}
                # Only use search experience_level if metadata doesn't have one
                if experience_level and not metadata.get("experience_level"):
                    metadata["experience_level"] = experience_level
                self._insert_job_url_with_metadata(url, website, job_role, metadata, suffix)
                saved_count += 1
        
        logger.info(f"Saved {saved_count} new URLs, {existing_count} existing URLs updated")
        return {"new": saved_count, "existing": existing_count}
    
    def url_exists(self, url: str) -> bool:
        """Check if URL already exists in database."""
        try:
            result = self.supabase.table(self.table_name).select("url").eq("url", url).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error checking URL existence: {e}")
            return False
    
    def get_unextracted_urls(self, website: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get URLs where extracted flag is false, optionally filtered by website."""
        try:
            query = self.supabase.table(self.table_name).select("*").eq("extracted", False)
            
            if website:
                query = query.eq("website", website)
            
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching unextracted URLs: {e}")
            return []
    
    def get_urls_by_site(self, website: str) -> List[Dict[str, Any]]:
        """Get all URLs for a specific website."""
        try:
            result = self.supabase.table(self.table_name).select("*").eq("website", website).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching URLs by site: {e}")
            return []
    
    def get_urls_by_job_role(self, job_role: str) -> List[Dict[str, Any]]:
        """Get all URLs for a specific job role."""
        try:
            result = self.supabase.table(self.table_name).select("*").eq("job_role", job_role).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching URLs by job role: {e}")
            return []
    
    def mark_as_extracted(self, url: str) -> bool:
        """Mark a URL as extracted."""
        try:
            result = self.supabase.table(self.table_name).update({"extracted": True}).eq("url", url).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error marking URL as extracted: {e}")
            return False
    
    def update_job_sector(self, url: str, job_sector: str) -> bool:
        """Update the job sector for a URL."""
        try:
            result = self.supabase.table(self.table_name).update({"job_sector": job_sector}).eq("url", url).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error updating job sector: {e}")
            return False
    
    def _insert_job_url(self, url: str, website: str, job_role: str) -> bool:
        """Insert a new job URL into the database."""
        try:
            data = {
                "url": url,
                "website": website,
                "job_role": job_role,
                "scraped_at": datetime.utcnow().isoformat(),
                "extracted": False,
                "job_sector": ""
            }
            result = self.supabase.table(self.table_name).insert(data).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error inserting job URL: {e}")
            return False
    
    def _insert_job_url_with_metadata(self, url: str, website: str, job_role: str, metadata: Dict[str, Any], suffix: Optional[str] = None) -> bool:
        """Insert a new job URL into the database with metadata."""
        try:
            data = {
                "url": url,
                "website": website,
                "job_role": job_role,
                "suffix": suffix,
                "scraped_at": datetime.utcnow().isoformat(),
                "extracted": False,
                "job_sector": "",
                "location": metadata.get("location", ""),
                "experience_level": metadata.get("experience_level", ""),
                "date_posted": metadata.get("date_posted", "")
            }
            result = self.supabase.table(self.table_name).insert(data).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error inserting job URL with metadata: {e}")
            return False
    
    def _update_scraped_at(self, url: str) -> bool:
        """Update the scraped_at timestamp for an existing URL."""
        try:
            data = {
                "scraped_at": datetime.utcnow().isoformat()
            }
            result = self.supabase.table(self.table_name).update(data).eq("url", url).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error updating scraped_at: {e}")
            return False
    
    def _update_scraped_at_with_metadata(self, url: str, metadata: Dict[str, Any], suffix: Optional[str] = None) -> bool:
        """Update the scraped_at timestamp and metadata for an existing URL."""
        try:
            data = {
                "scraped_at": datetime.utcnow().isoformat()
            }
            
            # Add suffix if provided
            if suffix is not None:
                data["suffix"] = suffix
            
            # Add metadata fields if present
            if metadata.get("location"):
                data["location"] = metadata["location"]
            if metadata.get("experience_level"):
                data["experience_level"] = metadata["experience_level"]
            if metadata.get("date_posted"):
                data["date_posted"] = metadata["date_posted"]
            
            result = self.supabase.table(self.table_name).update(data).eq("url", url).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error updating scraped_at with metadata: {e}")
            return False