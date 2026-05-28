"""Sample extractor for validating job data extraction before full scraping."""

import asyncio
import logging
import re
from typing import Optional, List
from datetime import datetime
from bs4 import BeautifulSoup

from .browser_manager import BrowserManager
from .models import JobListing, Skill


class SampleExtractor:
    """Extracts the first job listing as a sample for user validation."""
    
    def __init__(self, browser_manager: BrowserManager):
        """Initialize sample extractor with browser manager."""
        self.browser_manager = browser_manager
        self.logger = logging.getLogger(__name__)
    
    async def extract_first_job(self) -> Optional[JobListing]:
        """Extract the first job listing by navigating to its detail page via URL."""
        try:
            self.logger.info("Extracting first job listing as sample...")
            
            page = self.browser_manager.page
            if not page:
                self.logger.error("Browser page not available")
                return None
            
            # Get the current search results URL to return to later
            search_results_url = page.url
            
            # Collect all job URLs from the current page
            job_urls = await self._collect_job_urls()
            if not job_urls:
                self.logger.error("Could not find any job URLs on the search results page")
                return None
            
            self.logger.info(f"Found {len(job_urls)} job URLs, extracting first one")
            
            # Navigate to the first job URL
            first_job_url = job_urls[0]
            full_job_url = f"https://www.mycareersfuture.gov.sg{first_job_url}"
            
            self.logger.info(f"Navigating to job: {full_job_url}")
            await page.goto(full_job_url)
            await asyncio.sleep(3)
            await self.browser_manager.wait_for_content_load()
            
            # Extract job data from the detailed page
            job_listing = await self._extract_job_data_from_detail_page()
            
            if job_listing:
                job_listing.original_url = full_job_url
                job_listing.calculate_completeness_score()
                self.logger.info(f"Sample job extracted: {job_listing.title} at {job_listing.company_name}")
                self.logger.info(f"Data completeness: {job_listing.data_completeness_score:.1%}")
                
                # Return to search results page
                await page.goto(search_results_url)
                await asyncio.sleep(2)
                
                return job_listing
            else:
                self.logger.error("Failed to extract job data from detail page")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to extract first job: {e}")
            return None
    
    async def _collect_job_urls(self) -> List[str]:
        """Collect all job URLs from the current search results page, excluding recommended jobs."""
        page = self.browser_manager.page
        job_urls = []
        
        try:
            # Wait a bit for the page to fully load after search
            await asyncio.sleep(3)
            
            # Use a more comprehensive approach to filter out recommended jobs
            all_job_links = await page.query_selector_all('a[href*="/job/"]')
            self.logger.info(f"Found {len(all_job_links)} total job links")
            
            for link in all_job_links:
                try:
                    href = await link.get_attribute('href')
                    if href and '/job/' in href:
                        # Check if this is a recommended job using multiple methods
                        is_recommended = await self._is_recommended_job(link)
                        
                        if is_recommended:
                            self.logger.debug(f"Skipping recommended job: {href}")
                            continue
                        
                        if href not in job_urls:
                            job_urls.append(href)
                            self.logger.debug(f"Added job URL: {href}")
                            
                except Exception as e:
                    self.logger.debug(f"Error checking link: {e}")
                    continue
            
            # Remove duplicates while preserving order
            unique_urls = []
            seen = set()
            for url in job_urls:
                if url not in seen:
                    unique_urls.append(url)
                    seen.add(url)
            
            self.logger.info(f"Collected {len(unique_urls)} unique job URLs (excluding recommended jobs)")
            
            # If still no URLs, inform user that only recommended jobs were found
            if not unique_urls:
                self.logger.warning("⚠️  Only recommended jobs found - no actual search results available")
                self.logger.info("This may happen when there are very few jobs matching your search criteria")
                
                # Don't take any recommended jobs - let the user know the situation
                return []
            
            return unique_urls
            
        except Exception as e:
            self.logger.error(f"Failed to collect job URLs: {e}")
            return []
    
    async def _is_recommended_job(self, link) -> bool:
        """Check if a job link is a recommended job using multiple detection methods."""
        try:
            # Method 1: Check URL parameters for recommendation indicators
            href = await link.get_attribute('href')
            if href and any(param in href.lower() for param in ['suggested', 'recommended', 'event=suggestedjob']):
                self.logger.debug(f"Recommended job detected by URL: {href}")
                return True
            
            # Method 2: Check link text content
            link_text = await link.evaluate('el => el.textContent || ""')
            if any(keyword in link_text.lower() for keyword in ['recommended', 'suggested', 'based on your skills']):
                self.logger.debug(f"Recommended job detected by link text: {link_text}")
                return True
            
            # Method 3: Check parent element text content
            parent_text = await link.evaluate('el => el.parentElement ? el.parentElement.textContent || "" : ""')
            if any(keyword in parent_text.lower() for keyword in ['recommended', 'suggested', 'based on your skills', 'job applications']):
                self.logger.debug(f"Recommended job detected by parent text: {parent_text}")
                return True
            
            # Method 4: Check for CSS classes that indicate recommended jobs
            parent_classes = await link.evaluate('''
                el => {
                    let current = el;
                    let classes = [];
                    // Check current element and up to 3 parent levels
                    for (let i = 0; i < 4 && current; i++) {
                        if (current.className) {
                            classes.push(current.className);
                        }
                        current = current.parentElement;
                    }
                    return classes.join(' ').toLowerCase();
                }
            ''')
            
            if any(keyword in parent_classes for keyword in ['suggested', 'recommended', 'recommendation']):
                self.logger.debug(f"Recommended job detected by CSS classes: {parent_classes}")
                return True
            
            # Method 5: Check for data attributes that might indicate recommendations
            data_attrs = await link.evaluate('''
                el => {
                    let current = el;
                    let attrs = [];
                    // Check current element and up to 2 parent levels
                    for (let i = 0; i < 3 && current; i++) {
                        for (let attr of current.attributes) {
                            if (attr.name.startsWith('data-')) {
                                attrs.push(attr.name + '=' + attr.value);
                            }
                        }
                        current = current.parentElement;
                    }
                    return attrs.join(' ').toLowerCase();
                }
            ''')
            
            if any(keyword in data_attrs for keyword in ['suggested', 'recommended', 'recommendation']):
                self.logger.debug(f"Recommended job detected by data attributes: {data_attrs}")
                return True
            
            # Method 6: Check surrounding text context (siblings)
            context_text = await link.evaluate('''
                el => {
                    let context = '';
                    let parent = el.parentElement;
                    if (parent) {
                        // Get text from previous and next siblings
                        let prev = parent.previousElementSibling;
                        let next = parent.nextElementSibling;
                        if (prev) context += prev.textContent || '';
                        if (next) context += next.textContent || '';
                        
                        // Also check grandparent context
                        let grandparent = parent.parentElement;
                        if (grandparent) {
                            context += grandparent.textContent || '';
                        }
                    }
                    return context.toLowerCase();
                }
            ''')
            
            if any(keyword in context_text for keyword in ['recommended based on', 'suggested for you', 'you might like']):
                self.logger.debug(f"Recommended job detected by context: {context_text[:100]}...")
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking if job is recommended: {e}")
            return False  # If we can't determine, assume it's not recommended
    
    async def _extract_job_data_from_detail_page(self) -> Optional[JobListing]:
        """Extract comprehensive job data from the detailed job page."""
        try:
            page = self.browser_manager.page
            
            # Wait for the page to fully load and render
            await asyncio.sleep(5)
            
            # Wait for specific elements that indicate the job description is loaded
            try:
                await page.wait_for_selector('h1', timeout=10000)
                await page.wait_for_selector('div', timeout=10000)
            except:
                pass  # Continue even if specific selectors aren't found
            
            # Get page content after everything has loaded
            html_content = await page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Initialize job listing with defaults
            job_listing = JobListing(
                job_id=self._generate_job_id(),
                title="",
                company_name="",
                original_url=await self._get_current_url()
            )
            
            # Extract comprehensive data from detail page
            job_listing.title = self._extract_title_from_detail(soup)
            job_listing.company_name = self._extract_company_from_detail(soup)
            job_listing.description = await self._extract_full_job_description_js(page)  # Use JS extraction
            job_listing.location = self._extract_location_from_detail(soup)
            job_listing.employment_type = self._extract_employment_type_from_detail(soup)
            
            # Extract salary information
            salary_min, salary_max = self._extract_salary_from_detail(soup)
            job_listing.salary_min = salary_min
            job_listing.salary_max = salary_max
            
            # Extract skills and requirements
            job_listing.required_skills = self._extract_skills_from_detail(soup)
            job_listing.requirements = self._extract_requirements_from_detail(soup)
            job_listing.responsibilities = self._extract_full_roles_responsibilities(soup)
            
            # Extract additional details
            job_listing.experience_years = self._extract_experience_from_detail(soup)
            job_listing.education_requirements = self._extract_education_from_detail(soup)
            job_listing.posting_date = self._extract_posting_date_from_detail(soup)
            
            # Set extraction confidence
            job_listing.extraction_confidence = self._calculate_confidence(job_listing)
            
            return job_listing
            
        except Exception as e:
            self.logger.error(f"Failed to extract job data from detail page: {e}")
            return None
    
    async def _extract_full_job_description_js(self, page) -> str:
        """Extract job description using JavaScript to get rendered content."""
        try:
            # Wait a bit more for dynamic content to load
            await asyncio.sleep(3)
            
            # Try to get the largest text content from the page using JavaScript
            description = await page.evaluate('''
                () => {
                    // Look for common job description containers
                    const selectors = [
                        '.job-description',
                        '[class*="job-description"]',
                        '[class*="description"]',
                        '.w-100.v-top.relative',
                        'div[class*="w-100"]',
                        'main',
                        'article',
                        '[role="main"]'
                    ];
                    
                    let bestContent = '';
                    let maxLength = 0;
                    
                    // Try each selector
                    for (const selector of selectors) {
                        try {
                            const elements = document.querySelectorAll(selector);
                            for (const element of elements) {
                                const text = element.innerText || element.textContent || '';
                                if (text.length > maxLength && text.length > 200) {
                                    maxLength = text.length;
                                    bestContent = text;
                                }
                            }
                        } catch (e) {
                            continue;
                        }
                    }
                    
                    // If no good content found, get all visible text
                    if (!bestContent || bestContent.length < 500) {
                        const allDivs = document.querySelectorAll('div');
                        for (const div of allDivs) {
                            // Skip if element is not visible
                            const style = window.getComputedStyle(div);
                            if (style.display === 'none' || style.visibility === 'hidden') {
                                continue;
                            }
                            
                            const text = div.innerText || div.textContent || '';
                            if (text.length > maxLength && text.length > 200) {
                                maxLength = text.length;
                                bestContent = text;
                            }
                        }
                    }
                    
                    return bestContent;
                }
            ''')
            
            if description and len(description) > 100:
                # Clean the description text for better JSON readability - remove ALL newlines
                cleaned_description = self._clean_text_for_json(description)
                self.logger.info(f"Found job description using JavaScript ({len(cleaned_description)} chars)")
                return cleaned_description
            
            # Fallback to HTML parsing
            return self._extract_full_job_description(BeautifulSoup(await page.content(), 'html.parser'))
            
        except Exception as e:
            self.logger.error(f"Failed to extract job description with JavaScript: {e}")
            # Fallback to HTML parsing
            return self._extract_full_job_description(BeautifulSoup(await page.content(), 'html.parser'))
    
    def _extract_title_from_detail(self, soup: BeautifulSoup) -> str:
        """Extract job title from detailed job page."""
        title_selectors = [
            'h1',  # Most common for job titles
            '.job-title',
            '[data-testid*="title"]',
            '.position-title',
            '.job-header h1',
            '.job-header h2',
            'h2',  # Sometimes job title is in h2
            '.title'
        ]
        
        for selector in title_selectors:
            try:
                if selector.startswith('.'):
                    found = soup.find(class_=selector[1:])
                elif selector.startswith('['):
                    found = soup.find(attrs={'data-testid': lambda x: x and 'title' in x.lower()})
                else:
                    found = soup.find(selector)
                
                if found:
                    title = found.get_text().strip()
                    # Clean up the title - remove extra whitespace and newlines
                    title = ' '.join(title.split())
                    if title and len(title) > 3 and len(title) < 200:  # Reasonable title length
                        self.logger.info(f"Found job title using selector: {selector}")
                        return title
            except Exception as e:
                self.logger.debug(f"Error with title selector {selector}: {e}")
                continue
        
        return ""
    
    def _extract_company_from_detail(self, soup: BeautifulSoup) -> str:
        """Extract company name from detailed job page."""
        company_selectors = [
            '.company-name',
            '.employer',
            '[data-testid*="company"]',
            '.job-company',
            'h2',  # Often company name is in h2
            '.organization',
            '.company',
            'a[href*="company"]',  # Company links
            '.employer-name'
        ]
        
        for selector in company_selectors:
            try:
                if selector.startswith('.'):
                    found = soup.find(class_=selector[1:])
                elif selector.startswith('['):
                    found = soup.find(attrs={'data-testid': lambda x: x and 'company' in x.lower()})
                elif selector.startswith('a['):
                    found = soup.find('a', href=re.compile('company'))
                else:
                    found = soup.find(selector)
                
                if found:
                    company = found.get_text().strip()
                    # Clean up company name
                    company = ' '.join(company.split())
                    if company and len(company) > 2 and len(company) < 150:  # Reasonable company name length
                        # Skip if it looks like a job title or description
                        skip_words = ['looking', 'seeking', 'responsible', 'experience', 'required', 'job', 'position']
                        if not any(word in company.lower() for word in skip_words):
                            self.logger.info(f"Found company name using selector: {selector}")
                            return company
            except Exception as e:
                self.logger.debug(f"Error with company selector {selector}: {e}")
                continue
        
        return ""
    
    def _extract_location_from_detail(self, soup: BeautifulSoup) -> str:
        """Extract location from detailed job page."""
        location_selectors = [
            '.location',
            '.job-location',
            '[data-testid*="location"]',
            '.address',
            '.workplace'
        ]
        
        for selector in location_selectors:
            try:
                if selector.startswith('.'):
                    found = soup.find(class_=selector[1:])
                elif selector.startswith('['):
                    found = soup.find(attrs={'data-testid': lambda x: x and 'location' in x.lower()})
                else:
                    found = soup.find(selector)
                
                if found:
                    location = found.get_text().strip()
                    if location and len(location) > 2:
                        return location
            except:
                continue
        
        return ""
    
    def _extract_employment_type_from_detail(self, soup: BeautifulSoup) -> str:
        """Extract employment type from detailed page."""
        text_content = soup.get_text().lower()
        
        # Reorder to prioritize internship since we filtered for it
        employment_types = {
            'internship': ['internship', 'intern', 'attachment', 'trainee'],
            'part-time': ['part-time', 'part time', 'parttime'],
            'contract': ['contract', 'contractor'],
            'temporary': ['temporary', 'temp'],
            'full-time': ['full-time', 'full time', 'permanent', 'fulltime']
        }
        
        for emp_type, keywords in employment_types.items():
            for keyword in keywords:
                if keyword in text_content:
                    return emp_type
        
        return 'internship'  # Default to internship since we filtered for it
    
    def _extract_salary_from_detail(self, soup: BeautifulSoup) -> tuple:
        """Extract salary range from detailed page."""
        text_content = soup.get_text()
        
        # Singapore salary patterns
        salary_patterns = [
            r'S?\$\s*(\d{1,3}(?:,\d{3})*)\s*-\s*S?\$\s*(\d{1,3}(?:,\d{3})*)',
            r'(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)\s*SGD',
            r'SGD\s*(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text_content)
            if match:
                try:
                    min_salary = float(match.group(1).replace(',', ''))
                    max_salary = float(match.group(2).replace(',', ''))
                    return min_salary, max_salary
                except:
                    continue
        
        return None, None
    
    def _extract_skills_from_detail(self, soup: BeautifulSoup) -> List[str]:
        """Extract skills from 'Tell employers what skills you have' section."""
        skills = []
        
        try:
            # Method 1: Extract from the full page text using the pattern we can see
            page_text = soup.get_text()
            
            # Look for the "Add these skills if you have them" section
            if "Add these skills if you have them" in page_text:
                # Find the section after "Add these skills if you have them"
                start_idx = page_text.find("Add these skills if you have them")
                if start_idx != -1:
                    # Get text after this point
                    skills_section = page_text[start_idx:start_idx + 2000]  # Get next 2000 chars
                    
                    # Split by lines and extract skills
                    lines = skills_section.split('\n')
                    for line in lines[1:]:  # Skip the first line which is "Add these skills if you have them"
                        line = line.strip()
                        if line and len(line) > 1 and len(line) < 50:
                            # Stop when we hit other sections
                            if any(stop_word in line.lower() for stop_word in ['grow your skills', 'similar jobs', 'about the company', 'log in to apply']):
                                break
                            # Skip empty lines and non-skill text
                            if not any(skip in line.lower() for skip in ['skills', 'matched', 'grow', 'career', 'explore', 'recommended']):
                                skills.append(line)
                    
                    if skills:
                        self.logger.info(f"Found {len(skills)} skills using text pattern method")
                        return skills[:20]
            
            # Method 2: Look for the skills-needed section specifically
            skills_section = soup.find(id="skills-needed") or soup.find(attrs={"data-testid": "skills-needed"})
            
            if skills_section:
                # Look for all label elements within the skills section
                skill_labels = skills_section.find_all('label')
                for label in skill_labels:
                    skill_text = label.get_text().strip()
                    if skill_text and len(skill_text) > 1 and len(skill_text) < 50:
                        # Clean up the skill text
                        skill_text = skill_text.replace('==', '').replace('$0', '').replace('::before', '').strip()
                        if skill_text and skill_text not in skills:
                            skills.append(skill_text)
                
                if skills:
                    self.logger.info(f"Found {len(skills)} skills in skills-needed section")
                    return skills[:20]
            
            # Method 3: Look for common skill patterns in labels
            all_labels = soup.find_all('label')
            for label in all_labels:
                skill_text = label.get_text().strip()
                # Check if this looks like a skill (common tech skills)
                if any(tech_skill in skill_text.lower() for tech_skill in [
                    'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
                    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'html', 'css',
                    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'jenkins',
                    'c++', 'c#', '.net', 'php', 'ruby', 'go', 'rust', 'swift',
                    'agile', 'scrum', 'devops', 'ci/cd', 'testing', 'debugging',
                    'version control', 'defence', 'virtual training', 'public safety',
                    'aerospace', 'software simulation', 'strategy', 'value creation',
                    'software development', 'marketing', 'communication', 'business development'
                ]):
                    skill_text = skill_text.replace('==', '').replace('$0', '').replace('::before', '').strip()
                    if skill_text and skill_text not in skills and len(skill_text) < 50:
                        skills.append(skill_text)
            
            self.logger.info(f"Extracted {len(skills)} skills from job page")
            return skills[:20]
            
        except Exception as e:
            self.logger.error(f"Error extracting skills: {e}")
            return []
    
    def _extract_full_roles_responsibilities(self, soup: BeautifulSoup) -> str:
        """Extract the complete 'Roles & Responsibilities' section as one text block."""
        try:
            # Look for the "Roles & Responsibilities" heading
            roles_heading = soup.find(text=re.compile(r'roles?\s*&\s*responsibilities', re.IGNORECASE))
            
            if roles_heading:
                # Find the container that holds all the roles & responsibilities content
                container = roles_heading.parent
                
                # Look for the main content container - usually a few levels up
                for _ in range(5):
                    if container:
                        # Check if this container has substantial content
                        container_text = container.get_text(separator=' ', strip=True)
                        
                        # If we found a container with substantial content (more than just the heading)
                        if len(container_text) > 200:
                            # Clean up the text - remove ALL newlines and format as single readable paragraph
                            cleaned_text = self._clean_text_for_json(container_text)
                            
                            # Make sure we got the roles & responsibilities content
                            if 'roles' in cleaned_text.lower() and len(cleaned_text) > 500:
                                self.logger.info(f"Extracted roles & responsibilities section ({len(cleaned_text)} chars)")
                                return cleaned_text
                        
                        container = container.parent
                    else:
                        break
            
            # Fallback: look for any large text block that might contain roles & responsibilities
            all_text_blocks = soup.find_all(['div', 'section'], 
                                          text=re.compile(r'(about|role|responsibilit|duties|qualit)', re.IGNORECASE))
            
            for block in all_text_blocks:
                parent = block.parent
                if parent:
                    text_content = parent.get_text(separator=' ', strip=True)
                    if len(text_content) > 1000:  # Substantial content
                        cleaned_text = self._clean_text_for_json(text_content)
                        self.logger.info(f"Extracted roles & responsibilities using fallback ({len(cleaned_text)} chars)")
                        return cleaned_text
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error extracting roles & responsibilities: {e}")
            return ""
    
    def _clean_text_for_json(self, text: str) -> str:
        """Clean text to make it more readable in JSON format with line breaks for readability."""
        if not text:
            return ""
        
        import re
        
        # First normalize all whitespace - remove all newlines and tabs
        text = re.sub(r'[\n\r\t]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('  ', ' ')  # Double spaces
        text = text.strip()
        
        # Add proper sentence spacing after periods for better readability
        text = re.sub(r'\.([A-Z])', r'. \1', text)
        
        # Add line breaks before major section headers for better JSON readability
        section_headers = [
            'About ST Engineering',
            'About our Business', 
            'About the Company',
            'Together, We Can Make A Significant Impact',
            'Be Part of Our Success',
            'Qualities We Value',
            'Our Commitment That Goes Beyond the Norm'
        ]
        
        for section in section_headers:
            if section in text:
                text = text.replace(section, f'\n\n{section}')
        
        # Add line breaks after long sentences (every ~150 characters at sentence boundaries)
        sentences = text.split('. ')
        formatted_sentences = []
        current_line_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Add the sentence
            if current_line_length + len(sentence) > 150 and current_line_length > 0:
                formatted_sentences.append('\n' + sentence)
                current_line_length = len(sentence)
            else:
                formatted_sentences.append(sentence)
                current_line_length += len(sentence)
        
        # Join sentences back together
        text = '. '.join(formatted_sentences)
        
        # Clean up formatting
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Clean up multiple newlines
        text = re.sub(r'^\n+', '', text)  # Remove leading newlines
        text = text.strip()
        
        return text
    
    def _clean_text_simple(self, text: str) -> str:
        """Clean text and return as simple string for better JSON readability."""
        if not text:
            return ""
        
        import re
        
        # Normalize whitespace but keep single spaces
        text = re.sub(r'[\n\r\t]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Ensure proper sentence spacing
        text = re.sub(r'\.([A-Z])', r'. \1', text)
        
        # Remove trailing periods that might be doubled
        text = re.sub(r'\.+', '.', text)
        
        return text.strip()
    
    def _extract_requirements_from_detail(self, soup: BeautifulSoup) -> List[str]:
        """Extract job requirements from detailed page."""
        requirements = []
        
        # Look for requirements sections
        req_keywords = ['requirements', 'qualifications', 'must have', 'essential']
        
        for keyword in req_keywords:
            sections = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for section in sections:
                parent = section.parent
                if parent:
                    # Look for lists
                    lists = parent.find_next_siblings(['ul', 'ol']) or parent.find_all(['ul', 'ol'])
                    for list_elem in lists:
                        items = list_elem.find_all('li')
                        for item in items:
                            req_text = item.get_text().strip()
                            if req_text and len(req_text) > 10:
                                requirements.append(req_text)
        
        return requirements[:5]  # Limit to first 5
    
    def _extract_experience_from_detail(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract years of experience required."""
        text_content = soup.get_text()
        
        # Look for experience patterns
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'minimum\s*(\d+)\s*years?',
            r'at least\s*(\d+)\s*years?'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    continue
        
        return None
    
    def _extract_education_from_detail(self, soup: BeautifulSoup) -> List[str]:
        """Extract education requirements."""
        education = []
        text_content = soup.get_text().lower()
        
        education_keywords = [
            'bachelor', 'degree', 'diploma', 'masters', 'phd',
            'university', 'college', 'certification'
        ]
        
        for keyword in education_keywords:
            if keyword in text_content:
                education.append(keyword.title())
        
        return list(set(education))  # Remove duplicates
    
    def _extract_posting_date_from_detail(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract posting date from detailed page."""
        # This would need more specific implementation based on the actual page structure
        return None
    
    def _extract_full_job_description(self, soup: BeautifulSoup) -> str:
        """Extract the complete job description from the page."""
        # First try the specific selector you mentioned
        desc_selectors = [
            '.job-description.w-100.v-top.relative',
            '.w-100.v-top.relative',
            '.job-description',
            'div[class*="job-description"]',
            'div[class*="description"]'
        ]
        
        for selector in desc_selectors:
            try:
                if '.' in selector and selector.startswith('.'):
                    # Handle multiple classes
                    classes = selector[1:].split('.')
                    found = soup.find(class_=lambda x: x and all(cls in x.split() for cls in classes))
                elif selector.startswith('div[class*='):
                    # Handle contains selector
                    class_name = selector.split('"')[1]
                    found = soup.find('div', class_=lambda x: x and class_name in ' '.join(x) if x else False)
                else:
                    found = soup.find(class_=selector[1:] if selector.startswith('.') else selector)
                
                if found:
                    # Get all text content, preserving structure
                    desc = found.get_text(separator=' ', strip=True)
                    if desc and len(desc) > 100:  # Must be substantial content
                        cleaned_desc = self._clean_text_for_json(desc)
                        self.logger.info(f"Found job description using selector: {selector} ({len(cleaned_desc)} chars)")
                        return cleaned_desc
            except Exception as e:
                self.logger.debug(f"Error with description selector {selector}: {e}")
                continue
        
        # Fallback: Look for the largest text block that's likely the job description
        all_divs = soup.find_all('div')
        candidates = []
        
        for div in all_divs:
            text = div.get_text(separator=' ', strip=True)
            if len(text) > 500:  # Substantial content
                # Skip if it's likely navigation, header, or footer content
                classes = div.get('class', [])
                class_str = ' '.join(classes).lower()
                
                # Skip common non-content areas
                skip_classes = ['nav', 'header', 'footer', 'menu', 'sidebar', 'breadcrumb', 'pagination']
                if any(skip_class in class_str for skip_class in skip_classes):
                    continue
                
                candidates.append((text, len(text), div))
        
        # Sort by length and return the longest one
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            longest_text = candidates[0][0]
            cleaned_text = self._clean_text_for_json(longest_text)
            self.logger.info(f"Found job description using fallback method ({len(cleaned_text)} chars)")
            return cleaned_text
        
        # Final fallback: Get all text from the page and try to extract meaningful content
        page_text = soup.get_text(separator=' ', strip=True)
        if len(page_text) > 200:
            cleaned_text = self._clean_text_for_json(page_text)
            self.logger.info(f"Using full page text as fallback ({len(cleaned_text)} chars)")
            return cleaned_text
        
        return ""
    
    def _calculate_confidence(self, job_listing: JobListing) -> float:
        """Calculate extraction confidence based on data completeness."""
        score = 0.0
        
        if job_listing.title:
            score += 0.3
        if job_listing.company_name:
            score += 0.3
        if job_listing.description:
            score += 0.2
        if job_listing.location:
            score += 0.1
        if job_listing.required_skills:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_job_id(self) -> str:
        """Generate a unique job ID for the sample."""
        import uuid
        return f"SAMPLE_{uuid.uuid4().hex[:8].upper()}"
    
    async def _get_current_url(self) -> str:
        """Get the current page URL."""
        try:
            if self.browser_manager.page:
                return self.browser_manager.page.url
        except:
            pass
        return ""