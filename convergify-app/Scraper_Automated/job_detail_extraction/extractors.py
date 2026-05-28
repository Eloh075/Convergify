"""Job detail extractors for different websites."""

import re
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from .config import JobDetailExtractorConfig
from .models import JobDetails


class BaseJobDetailExtractor:
    """Base class for job detail extractors."""
    
    def __init__(self, config: Optional[JobDetailExtractorConfig] = None):
        self.config = config or JobDetailExtractorConfig()
    
    def extract(self, url: str, browser) -> JobDetails:
        """Extract job details from URL."""
        raise NotImplementedError("Subclasses must implement extract method")
    
    def _extract_json_ld(self, browser) -> List[Dict[str, Any]]:
        """Extract JSON-LD structured data from page."""
        json_ld_data = []
        try:
            scripts = browser.page.query_selector_all('script[type="application/ld+json"]')
            for script in scripts:
                try:
                    content = script.inner_text()
                    if content:
                        data = json.loads(content)
                        json_ld_data.append(data)
                except json.JSONDecodeError:
                    # Try to clean and parse
                    try:
                        # Remove any invalid characters
                        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
                        data = json.loads(cleaned)
                        json_ld_data.append(data)
                    except:
                        pass
        except Exception as e:
            logger.debug(f"Error extracting JSON-LD: {e}")
        
        return json_ld_data
    
    def _extract_from_json_ld(self, json_ld_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract job details from JSON-LD structured data."""
        result = {}
        
        for data in json_ld_data:
            if data.get("@type") == "JobPosting":
                # Map JSON-LD fields to our model
                mapping = {
                    "title": "job_title",
                    "hiringOrganization.name": "company",
                    "jobLocation.address.addressLocality": "location",
                    "datePosted": "date_posted",
                    "validThrough": "application_deadline",
                    "employmentType": "job_type",
                    "experienceRequirements": "experience_level",
                    "baseSalary.value.minValue": "salary_min",
                    "baseSalary.value.maxValue": "salary_max",
                    "baseSalary.value.unitText": "salary_unit",
                    "industry": "industry",
                    "description": "description",
                }
                
                for json_key, our_key in mapping.items():
                    value = self._get_nested_value(data, json_key)
                    if value:
                        result[our_key] = value
                
                # Combine salary fields
                if "salary_min" in result and "salary_max" in result:
                    unit = result.get("salary_unit", "")
                    result["salary_range"] = f"{result['salary_min']} to {result['salary_max']} {unit}"
                    result.pop("salary_min", None)
                    result.pop("salary_max", None)
                    result.pop("salary_unit", None)
        
        return result
    
    def _get_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """Get nested value from dictionary using dot notation."""
        keys = key_path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common unwanted characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text


class LinkedInJobDetailExtractor(BaseJobDetailExtractor):
    """Extract job details from LinkedIn."""
    
    def extract(self, url: str, browser, job_role: str = "") -> JobDetails:
        """Extract job details from LinkedIn URL."""
        logger.info(f"Extracting LinkedIn job details from: {url}")
        
        job_details = JobDetails(
            url=url,
            website="LinkedIn",
            job_role=job_role,
            extracted_at=datetime.now(),
        )
        
        try:
            # Navigate to URL
            browser.navigate_to(url)
            browser.wait(3)
            
            # Wait for page to load
            browser.wait_for_selector(".job-view-layout", timeout=10000)
            
            # Extract JSON-LD structured data first
            json_ld_data = self._extract_json_ld(browser)
            structured_data = self._extract_from_json_ld(json_ld_data)
            
            # Extract using CSS selectors
            extracted_data = {}
            
            for field, selector in self.config.linkedin_selectors.items():
                try:
                    element = browser.page.query_selector(selector)
                    if element:
                        text = element.inner_text()
                        extracted_data[field] = self._clean_text(text)
                except Exception as e:
                    logger.debug(f"Could not extract {field}: {e}")
            
            # Parse job criteria (LinkedIn specific)
            self._extract_job_criteria(browser, extracted_data)
            
            # Combine all data
            all_data = {**structured_data, **extracted_data}
            
            # Map to JobDetails model
            job_details.job_title = all_data.get("job_title")
            job_details.company = all_data.get("company")
            job_details.location = all_data.get("location")
            job_details.date_posted = all_data.get("date_posted")
            job_details.description = all_data.get("description")
            job_details.job_type = all_data.get("job_type")
            job_details.experience_level = all_data.get("experience_level")
            job_details.industry = all_data.get("industry")
            job_details.salary_range = all_data.get("salary_range")
            
            # Try to extract job role from title
            if job_details.job_title:
                # Simple extraction - could be enhanced
                job_details.job_role = self._extract_job_role_from_title(job_details.job_title)
            elif not job_details.job_role:
                # Fallback if no job_role provided and no title extracted
                job_details.job_role = "Unknown"
            
            job_details.success = True
            job_details.raw_data = all_data
            
        except Exception as e:
            logger.error(f"Error extracting LinkedIn job details: {e}")
            job_details.error_message = str(e)
            job_details.success = False
        
        return job_details
    
    def _extract_job_criteria(self, browser, extracted_data: Dict[str, Any]):
        """Extract job criteria from LinkedIn job posting."""
        try:
            criteria_items = browser.page.query_selector_all(self.config.linkedin_selectors["job_criteria_items"])
            for item in criteria_items:
                try:
                    header = item.query_selector(self.config.linkedin_selectors["criteria_header"])
                    text = item.query_selector(self.config.linkedin_selectors["criteria_text"])
                    
                    if header and text:
                        header_text = header.inner_text().strip().lower()
                        value_text = text.inner_text().strip()
                        
                        if "seniority" in header_text:
                            extracted_data["experience_level"] = value_text
                        elif "employment type" in header_text:
                            extracted_data["job_type"] = value_text
                        elif "industry" in header_text or "industries" in header_text:
                            extracted_data["industry"] = value_text
                        elif "job function" in header_text:
                            extracted_data["job_function"] = value_text
                except:
                    pass
        except Exception as e:
            logger.debug(f"Error extracting job criteria: {e}")
    
    def _extract_job_role_from_title(self, title: str) -> str:
        """Extract job role from title."""
        # Common job roles to look for
        common_roles = [
            "Software Engineer", "Data Analyst", "AI Engineer", "Machine Learning Engineer",
            "Product Manager", "Business Analyst", "Full Stack Developer", "Data Scientist",
            "Frontend Developer", "Backend Developer", "DevOps Engineer", "Cloud Engineer",
        ]
        
        title_lower = title.lower()
        for role in common_roles:
            if role.lower() in title_lower:
                return role
        
        # Return first few words as fallback
        words = title.split()
        if len(words) >= 2:
            return f"{words[0]} {words[1]}"
        
        return title


class SkillsFutureJobDetailExtractor(BaseJobDetailExtractor):
    """Extract job details from SkillsFuture (MyCareersFuture)."""
    
    def extract(self, url: str, browser, job_role: str = "") -> JobDetails:
        """Extract job details from SkillsFuture URL."""
        logger.info(f"Extracting SkillsFuture job details from: {url}")
        
        job_details = JobDetails(
            url=url,
            website="SkillsFuture",
            job_role=job_role,
            extracted_at=datetime.now(),
        )
        
        try:
            # Navigate to URL
            browser.navigate_to(url)
            browser.wait(5)  # Wait longer for JavaScript to load
            
            # Extract using data-testid selectors (most reliable)
            extracted_data = {}
            
            for field, selector in self.config.skillsfuture_selectors.items():
                if field.endswith("_fallback"):
                    continue  # Skip fallback selectors for now
                
                try:
                    element = browser.page.query_selector(selector)
                    if element:
                        text = element.inner_text().strip()
                        if text:
                            extracted_data[field] = self._clean_text(text)
                            logger.debug(f"Extracted {field}: {text[:50]}...")
                except Exception as e:
                    logger.debug(f"Could not extract {field}: {e}")
            
            # Try fallback selectors if primary failed
            if not extracted_data.get("job_title"):
                try:
                    elem = browser.page.query_selector(self.config.skillsfuture_selectors["job_title_fallback"])
                    if elem:
                        extracted_data["job_title"] = self._clean_text(elem.inner_text())
                except:
                    pass
            
            if not extracted_data.get("salary_range"):
                try:
                    elem = browser.page.query_selector(self.config.skillsfuture_selectors["salary_fallback"])
                    if elem:
                        extracted_data["salary_range"] = self._clean_text(elem.inner_text())
                except:
                    pass
            
            # Extract company name from URL or page
            company_name = self._extract_company_from_url(url)
            if company_name:
                extracted_data["company"] = company_name
            
            # Process skills - remove prefix and convert to list
            if extracted_data.get("skills"):
                skills_text = extracted_data["skills"]
                # Remove "Add these skills if you have them" prefix
                skills_text = skills_text.replace("Add these skills if you have them", "").strip()
                
                # Skills on MyCareersFuture appear to be separated by newlines or spaces
                # Try splitting by newlines first
                skills_list = []
                lines = skills_text.split("\n")
                
                if len(lines) > 1:
                    # Multiple lines - each line is likely a skill
                    skills_list = [line.strip() for line in lines if line.strip()]
                else:
                    # Single line - skills might be space-separated
                    # Common skill names are usually 1-3 words, capitalize first letter
                    # Split by spaces and try to identify individual skills
                    words = skills_text.split()
                    current_skill = []
                    
                    for word in words:
                        # If word starts with capital or is an acronym, might be new skill
                        if word[0].isupper() or word.isupper():
                            if current_skill:
                                skills_list.append(" ".join(current_skill))
                            current_skill = [word]
                        else:
                            current_skill.append(word)
                    
                    # Add last skill
                    if current_skill:
                        skills_list.append(" ".join(current_skill))
                
                extracted_data["skills_list"] = skills_list if skills_list else None
            
            # Map to JobDetails model
            job_details.job_title = extracted_data.get("job_title")
            job_details.company = extracted_data.get("company")
            job_details.location = extracted_data.get("location")
            job_details.date_posted = extracted_data.get("date_posted")
            job_details.application_deadline = extracted_data.get("expiry_date")
            job_details.job_type = extracted_data.get("employment_type")
            job_details.seniority_level = extracted_data.get("seniority")
            job_details.experience_level = extracted_data.get("experience")
            job_details.salary_range = extracted_data.get("salary_range")
            job_details.category = extracted_data.get("category")
            job_details.description = extracted_data.get("description")
            job_details.skills = extracted_data.get("skills_list")  # Store as list
            
            # Extract job sector from URL
            if "information-technology" in url:
                job_details.job_sector = "Information Technology"
            elif "engineering" in url:
                job_details.job_sector = "Engineering"
            
            if job_details.category:
                job_details.industry = job_details.category
            
            # Try to extract job role from title
            if job_details.job_title:
                job_details.job_role = self._extract_job_role_from_title(job_details.job_title)
            elif not job_details.job_role:
                # Fallback if no job_role provided and no title extracted
                job_details.job_role = "Unknown"
            
            job_details.success = True
            job_details.raw_data = extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting SkillsFuture job details: {e}")
            job_details.error_message = str(e)
            job_details.success = False
        
        return job_details
    
    def _extract_company_from_url(self, url: str) -> Optional[str]:
        """Extract company name from URL."""
        # MyCareersFuture URL format: .../job-title-company-name-hash
        try:
            parts = url.split("/")
            if len(parts) >= 4:
                job_part = parts[-1].split("?")[0]  # Remove query params
                # Remove hash at the end
                job_part = "-".join(job_part.split("-")[:-1])
                # Company is usually the last part before hash
                company_parts = job_part.split("-")
                if len(company_parts) > 2:
                    # Take last 2-3 words as company name
                    company = " ".join(company_parts[-2:]).title()
                    return company
        except:
            pass
        return None
    
    def _extract_job_role_from_title(self, title: str) -> str:
        """Extract job role from title."""
        # Common job roles to look for
        common_roles = [
            "Software Engineer", "Data Analyst", "AI Engineer", "Machine Learning Engineer",
            "Product Manager", "Business Analyst", "Full Stack Developer", "Data Scientist",
            "Frontend Developer", "Backend Developer", "DevOps Engineer", "Cloud Engineer",
        ]
        
        title_lower = title.lower()
        for role in common_roles:
            if role.lower() in title_lower:
                return role
        
        # Return first few words as fallback
        words = title.split()
        if len(words) >= 2:
            return f"{words[0]} {words[1]}"
        
        return title


class JobDetailExtractorFactory:
    """Factory to create appropriate job detail extractor."""
    
    @staticmethod
    def create_extractor(url: str, config: Optional[JobDetailExtractorConfig] = None) -> BaseJobDetailExtractor:
        """Create appropriate extractor based on URL."""
        if "linkedin.com" in url:
            return LinkedInJobDetailExtractor(config)
        elif "mycareersfuture.gov.sg" in url:
            return SkillsFutureJobDetailExtractor(config)
        else:
            raise ValueError(f"No extractor available for URL: {url}")