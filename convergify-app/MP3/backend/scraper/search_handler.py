"""Search handler for MyCareersFuture website integration."""

import asyncio
import logging
from typing import List, Optional
from .browser_manager import BrowserManager


class SearchHandler:
    """Handles search operations on MyCareersFuture website."""
    
    def __init__(self, browser_manager: BrowserManager):
        """Initialize search handler with browser manager."""
        self.browser_manager = browser_manager
        self.logger = logging.getLogger(__name__)
    
    async def perform_search(self, base_url: str, search_term: str, employment_types: List[str] = None) -> bool:
        """Perform job search with specified parameters."""
        try:
            self.logger.info(f"Starting search for: {search_term}")
            
            # Navigate to the base URL first
            await self.browser_manager.navigate_to_url(base_url)
            await self.browser_manager.wait_for_content_load()
            
            # Find and interact with search elements
            search_success = await self._execute_search(search_term)
            
            if not search_success:
                self.logger.error("Failed to execute search")
                return False
            
            # Apply employment type filters if specified
            if employment_types:
                filter_success = await self._apply_filters(employment_types)
                if not filter_success:
                    self.logger.warning("Failed to apply some filters, continuing with search results")
            
            # Validate search results page
            results_found = await self._validate_search_results()
            
            if results_found:
                self.logger.info("Search completed successfully")
                return True
            else:
                self.logger.warning("Search completed but no results found")
                return True  # Still consider successful even if no results
                
        except Exception as e:
            self.logger.error(f"Search operation failed: {e}")
            return False
    
    async def _execute_search(self, search_term: str) -> bool:
        """Execute the search with the given term using human-like typing."""
        try:
            page = self.browser_manager.page
            if not page:
                return False
            
            import random
            
            # MyCareersFuture specific search input selectors based on actual HTML
            search_selectors = [
                'input[placeholder="Search Job by Title or Keyword"]',
                'input[placeholder*="Search Job" i]',
                'input[placeholder*="Title or Keyword" i]',
                'input[name*="search" i]',
                'input[id*="search" i]',
                '.search-input input',
                'input[type="text"]'  # Generic fallback
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = await page.wait_for_selector(selector, timeout=5000)
                    if search_input:
                        # Verify it's visible and enabled
                        is_visible = await search_input.is_visible()
                        is_enabled = await search_input.is_enabled()
                        
                        if is_visible and is_enabled:
                            self.logger.info(f"Found search input: {selector}")
                            break
                        else:
                            search_input = None
                except:
                    continue
            
            if not search_input:
                self.logger.error("Could not find search input field")
                return False
            
            # Human-like typing with variable speed
            text_entered = False
            try:
                self.logger.info("Typing search term with human-like speed...")
                await search_input.click()
                await asyncio.sleep(random.uniform(0.02, 0.08))  # Brief pause after clicking
                
                # Clear any existing content with variable timing
                await page.keyboard.press('Control+a')
                await asyncio.sleep(random.uniform(0.01, 0.05))
                await page.keyboard.press('Delete')
                await asyncio.sleep(random.uniform(0.02, 0.06))
                
                # Type each character with variable delay to simulate human typing
                for char in search_term:
                    await search_input.type(char)
                    # Very short variable delay between characters (10-100ms)
                    delay = random.uniform(0.01, 0.1)
                    await asyncio.sleep(delay)
                
                # Add a brief pause after typing (like humans do)
                await asyncio.sleep(random.uniform(0.05, 0.1))
                
                # Verify text was entered
                current_value = await search_input.input_value()
                if current_value == search_term:
                    text_entered = True
                    self.logger.info(f"Successfully typed '{search_term}' with human-like timing")
                else:
                    self.logger.warning(f"Typing verification failed: Expected '{search_term}', got '{current_value}'")
            except Exception as e:
                self.logger.warning(f"Human-like typing failed: {e}")
            
            # Fallback to faster typing if human-like typing failed
            if not text_entered:
                try:
                    self.logger.info("Trying fallback typing method...")
                    await search_input.click()
                    await asyncio.sleep(random.uniform(0.02, 0.05))
                    await search_input.fill(search_term)
                    await asyncio.sleep(random.uniform(0.03, 0.08))
                    
                    current_value = await search_input.input_value()
                    if current_value == search_term:
                        text_entered = True
                        self.logger.info(f"Fallback method success: Entered '{search_term}'")
                    else:
                        self.logger.warning(f"Fallback method failed: Expected '{search_term}', got '{current_value}'")
                except Exception as e:
                    self.logger.warning(f"Fallback method failed: {e}")
            
            if not text_entered:
                self.logger.error("Failed to enter search term")
                return False
            
            # Human-like pause before proceeding (like reading what you typed)
            await asyncio.sleep(random.uniform(0.03, 0.1))
            
            # DON'T press Enter yet - we need to set employment type first
            # Just return True, the employment type will be set in _apply_filters
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute search: {e}")
            return False
    
    async def _apply_filters(self, employment_types: List[str]) -> bool:
        """Apply employment type filters using simple tab navigation sequence."""
        try:
            page = self.browser_manager.page
            if not page:
                return False
            
            import random
            
            self.logger.info(f"Applying employment type filters: {employment_types}")
            
            # Make sure we're focused on the search input first
            search_input = await page.query_selector('input[placeholder*="Search Job" i]')
            if search_input:
                await search_input.click()
                await asyncio.sleep(0.2)
                self.logger.info("Clicked search input to ensure focus")
            
            # Now tab to the employment dropdown (2 tabs)
            self.logger.info("Tabbing to employment dropdown (2 tabs)...")
            await page.keyboard.down('Tab')
            await asyncio.sleep(random.uniform(0.05, 0.15))  # Random key press duration
            await page.keyboard.up('Tab')
            await asyncio.sleep(random.uniform(0.3, 0.7))
            await page.keyboard.down('Tab')
            await asyncio.sleep(random.uniform(0.05, 0.15))  # Random key press duration
            await page.keyboard.up('Tab')
            await asyncio.sleep(random.uniform(0.3, 0.7))
            
            # Try to open the dropdown to see if we're on the right element
            self.logger.info("Trying to open dropdown with Enter...")
            await page.keyboard.down('Enter')
            await asyncio.sleep(random.uniform(0.05, 0.12))  # Random key press duration
            await page.keyboard.up('Enter')
            await asyncio.sleep(random.uniform(0.4, 0.8))
            
            # Arrow down 8 times to reach Internship/Attachment
            self.logger.info("Navigating to Internship/Attachment (8 arrow downs)...")
            for i in range(8):
                await page.keyboard.down('ArrowDown')
                await asyncio.sleep(random.uniform(0.03, 0.08))  # Random key press duration
                await page.keyboard.up('ArrowDown')
                await asyncio.sleep(random.uniform(0.2, 0.4))
                self.logger.info(f"Arrow down {i+1}/8")
            
            # Select the option
            self.logger.info("Selecting Internship/Attachment with Enter...")
            await page.keyboard.down('Enter')
            await asyncio.sleep(random.uniform(0.05, 0.12))  # Random key press duration
            await page.keyboard.up('Enter')
            await asyncio.sleep(random.uniform(0.4, 0.8))
            
            # Now tab to search button (just once)
            self.logger.info("Tabbing to search button (1 tab)...")
            await page.keyboard.down('Tab')
            await asyncio.sleep(random.uniform(0.05, 0.15))  # Random key press duration
            await page.keyboard.up('Tab')
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # Press Enter to search
            self.logger.info("Pressing Enter to search...")
            await page.keyboard.down('Enter')
            await asyncio.sleep(random.uniform(0.05, 0.12))  # Random key press duration
            await page.keyboard.up('Enter')
            await asyncio.sleep(random.uniform(1.0, 2.0))
            await self.browser_manager.wait_for_content_load()
            
            self.logger.info("Search submitted successfully")
            return True
                
        except Exception as e:
            self.logger.error(f"Failed to apply filters: {e}")
            return False
    
    async def _apply_checkbox_filters(self, employment_types: List[str], employment_mappings: dict) -> int:
        """Fallback method to apply filters using checkboxes/radio buttons."""
        try:
            page = self.browser_manager.page
            filters_applied = 0
            
            # Look for checkboxes or radio buttons
            checkbox_selectors = [
                'input[type="checkbox"]',
                'input[type="radio"]',
                '.filter-checkbox',
                '.employment-filter input'
            ]
            
            for emp_type in employment_types:
                search_terms = employment_mappings.get(emp_type.lower(), [emp_type.lower()])
                
                for selector in checkbox_selectors:
                    try:
                        checkboxes = await page.query_selector_all(selector)
                        
                        for checkbox in checkboxes:
                            # Get associated label text
                            label_text = await checkbox.evaluate('''
                                (el) => {
                                    let label = el.closest('label') || 
                                               document.querySelector(`label[for="${el.id}"]`) ||
                                               el.nextElementSibling ||
                                               el.previousElementSibling ||
                                               el.parentElement;
                                    return label ? label.textContent.toLowerCase().trim() : '';
                                }
                            ''')
                            
                            # Check if any search term matches the label
                            for term in search_terms:
                                if term in label_text:
                                    is_checked = await checkbox.is_checked()
                                    if not is_checked:
                                        await checkbox.click()
                                        filters_applied += 1
                                        self.logger.info(f"Applied checkbox filter: {emp_type} (matched: {term})")
                                    break
                    except Exception as e:
                        self.logger.debug(f"Error checking selector {selector}: {e}")
                        continue
            
            return filters_applied
            
        except Exception as e:
            self.logger.error(f"Failed to apply checkbox filters: {e}")
            return 0
    
    async def _validate_search_results(self) -> bool:
        """Validate that search results are present on the page."""
        try:
            page = self.browser_manager.page
            if not page:
                return False
            
            # Common job listing selectors
            job_listing_selectors = [
                '.job-card',
                '.job-listing',
                '.job-item',
                '.position',
                '.vacancy',
                '[data-testid*="job"]',
                '.search-result',
                '.job-post'
            ]
            
            # Check for job listings
            for selector in job_listing_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        self.logger.info(f"Found {len(elements)} job listings using selector: {selector}")
                        return True
                except:
                    continue
            
            # Check for "no results" messages
            no_results_selectors = [
                ':has-text("no results")',
                ':has-text("no jobs")',
                ':has-text("0 results")',
                '.no-results',
                '.empty-state'
            ]
            
            for selector in no_results_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        self.logger.info("No search results found (empty results page)")
                        return False
                except:
                    continue
            
            # If we can't find job listings or no-results messages,
            # assume results might be present but with different selectors
            self.logger.warning("Could not definitively validate search results")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate search results: {e}")
            return False
    
    async def get_total_results_count(self) -> Optional[int]:
        """Get the total number of search results if displayed."""
        try:
            page = self.browser_manager.page
            if not page:
                return None
            
            # Common selectors for result counts
            count_selectors = [
                '.results-count',
                '.total-results',
                ':has-text("results")',
                ':has-text("jobs found")',
                '[data-testid*="count"]'
            ]
            
            for selector in count_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text:
                            # Extract number from text
                            import re
                            numbers = re.findall(r'\d+', text.replace(',', ''))
                            if numbers:
                                count = int(numbers[0])
                                self.logger.info(f"Found total results count: {count}")
                                return count
                except:
                    continue
            
            self.logger.info("Could not determine total results count")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get results count: {e}")
            return None