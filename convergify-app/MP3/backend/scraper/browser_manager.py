"""Browser management using Playwright for dynamic content handling - Chrome Remote Debugging Version."""

import asyncio
import logging
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, Playwright, BrowserContext
from .config import ScraperConfig


class BrowserManager:
    """Manages Playwright browser instances and page lifecycle using Chrome Remote Debugging."""
    
    def __init__(self, config: ScraperConfig):
        """Initialize browser manager with configuration."""
        self.config = config
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize Playwright browser instance (managed Chrome instead of debug connection)."""
        try:
            self.logger.info("Initializing Playwright browser...")
            self.playwright = await async_playwright().start()
            
            # Launch browser with configuration (like V1)
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless,
                args=[
                    '--no-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--no-first-run',
                    '--disable-default-apps',
                    '--disable-extensions'
                ]
            )
            
            # Create new context and page
            self.context = await self.browser.new_context(
                viewport={
                    'width': self.config.viewport_width,
                    'height': self.config.viewport_height
                },
                user_agent=self.config.user_agent
            )
            
            self.page = await self.context.new_page()
            
            # Add stealth measures
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            # Set timeouts
            self.page.set_default_timeout(self.config.page_load_timeout * 1000)
            
            self.logger.info("Browser initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            await self.cleanup()
            raise
    
    async def navigate_to_url(self, url: str) -> None:
        """Navigate to a specific URL."""
        if not self.page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        
        try:
            self.logger.info(f"Navigating to: {url}")
            # Use a shorter timeout for faster navigation
            await self.page.goto(url, wait_until='domcontentloaded', timeout=15000)
            
            # Shorter manual wait - pages load quickly
            await asyncio.sleep(2)
            
            self.logger.info("Navigation completed")
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            raise
    
    async def navigate_to_search(self, base_url: str, search_term: str, employment_types: list) -> None:
        """Navigate to search results page with filters."""
        if not self.page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        
        try:
            # First navigate to the base URL
            await self.navigate_to_url(base_url)
            
            # Wait for page to load
            await self.wait_for_content_load()
            
            # Look for search input field
            search_selector = 'input[placeholder*="search" i], input[name*="search" i], input[id*="search" i]'
            await self.page.wait_for_selector(search_selector, timeout=10000)
            
            # Enter search term
            self.logger.info(f"Entering search term: {search_term}")
            await self.page.fill(search_selector, search_term)
            
            # Submit search (look for search button or press Enter)
            search_button_selectors = [
                'button[type="submit"]',
                'button:has-text("Search")',
                'input[type="submit"]',
                '.search-button',
                '[data-testid*="search"]'
            ]
            
            search_submitted = False
            for selector in search_button_selectors:
                try:
                    await self.page.click(selector, timeout=2000)
                    search_submitted = True
                    self.logger.info(f"Clicked search button: {selector}")
                    break
                except:
                    continue
            
            if not search_submitted:
                # Try pressing Enter on search field
                await self.page.press(search_selector, 'Enter')
                self.logger.info("Pressed Enter on search field")
            
            # Wait for search results to load
            await self.wait_for_content_load()
            
            # Apply employment type filters if specified
            if employment_types:
                await self.apply_employment_filters(employment_types)
            
            self.logger.info("Search navigation completed")
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to search: {e}")
            raise
    
    async def apply_employment_filters(self, employment_types: list) -> None:
        """Apply employment type filters on the search results page."""
        try:
            self.logger.info(f"Applying employment type filters: {employment_types}")
            
            # Common selectors for employment type filters
            filter_selectors = [
                'input[type="checkbox"]',
                '.filter-checkbox',
                '[data-testid*="filter"]',
                '.employment-type'
            ]
            
            for emp_type in employment_types:
                # Try to find and click the filter for this employment type
                for selector in filter_selectors:
                    try:
                        # Look for checkboxes with labels containing the employment type
                        elements = await self.page.query_selector_all(selector)
                        for element in elements:
                            # Get the associated label text
                            label_text = await element.evaluate('''
                                (el) => {
                                    const label = el.closest('label') || 
                                                 document.querySelector(`label[for="${el.id}"]`) ||
                                                 el.nextElementSibling ||
                                                 el.previousElementSibling;
                                    return label ? label.textContent.toLowerCase() : '';
                                }
                            ''')
                            
                            if emp_type.lower() in label_text:
                                await element.click()
                                self.logger.info(f"Applied filter: {emp_type}")
                                break
                    except:
                        continue
            
            # Wait for filters to be applied
            await asyncio.sleep(1)
            await self.wait_for_content_load()
            
        except Exception as e:
            self.logger.warning(f"Could not apply employment filters: {e}")
    
    async def wait_for_content_load(self) -> None:
        """Wait for JavaScript content to fully render."""
        if not self.page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        
        try:
            # Wait for network to be idle (but with much shorter timeout)
            try:
                await self.page.wait_for_load_state('networkidle', timeout=5000)
            except:
                # If networkidle fails, just wait for domcontentloaded
                await self.page.wait_for_load_state('domcontentloaded', timeout=3000)
            
            # Much shorter wait for dynamic content
            await asyncio.sleep(1)
            
            # Wait for common job listing elements to appear (shorter timeout)
            job_selectors = [
                '.job-card', '.job-listing', '.job-item',
                '[data-testid*="job"]', '.position', '.vacancy'
            ]
            
            for selector in job_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    self.logger.info(f"Content loaded - found elements: {selector}")
                    break
                except:
                    continue
            
        except Exception as e:
            self.logger.warning(f"Content loading wait completed with warnings: {e}")
    
    async def scroll_to_load_more(self) -> bool:
        """Scroll to trigger infinite scroll loading."""
        if not self.page:
            return False
        
        try:
            # Get current page height
            previous_height = await self.page.evaluate('document.body.scrollHeight')
            
            # Scroll to bottom
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            
            # Wait for potential new content
            await asyncio.sleep(3)
            
            # Check if new content loaded
            new_height = await self.page.evaluate('document.body.scrollHeight')
            
            if new_height > previous_height:
                self.logger.info("New content loaded via infinite scroll")
                await self.wait_for_content_load()
                return True
            else:
                self.logger.info("No new content loaded - reached end")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during scroll loading: {e}")
            return False
    
    async def get_page_content(self) -> str:
        """Get the current page HTML content."""
        if not self.page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        
        return await self.page.content()
    
    async def take_screenshot(self, filename: str) -> None:
        """Take a screenshot of the current page."""
        if not self.page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        
        try:
            await self.page.screenshot(path=filename, full_page=True)
            self.logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
    
    async def cleanup(self) -> None:
        """Clean up browser resources."""
        try:
            if self.page:
                await self.page.close()
                self.page = None
                self.logger.info("Page closed")
            
            if self.context:
                await self.context.close()
                self.context = None
                self.logger.info("Context closed")
            
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.logger.info("Browser closed")
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
                self.logger.info("Playwright stopped")
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()