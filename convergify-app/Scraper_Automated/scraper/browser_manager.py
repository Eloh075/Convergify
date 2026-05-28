"""Browser manager using Playwright for web scraping."""

from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout
from typing import Optional, List
from loguru import logger


class BrowserManager:
    """Manages browser automation using Playwright."""
    
    def __init__(self, headless: bool = True, timeout: int = 60000):
        """Initialize browser manager.
        
        Args:
            headless: Whether to run browser in headless mode
            timeout: Default timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
    
    def start(self) -> None:
        """Start the browser with advanced stealth options."""
        self.playwright = sync_playwright().start()
        
        # Launch browser with extensive anti-detection args
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials'
            ]
        )
        
        # Create context with realistic user agent, viewport, and permissions
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-SG',
            timezone_id='Asia/Singapore',
            permissions=['geolocation'],
            geolocation={'latitude': 1.3521, 'longitude': 103.8198},  # Singapore coordinates
            color_scheme='light',
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
            java_script_enabled=True
        )
        
        # Add comprehensive anti-detection scripts
        self.context.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins to appear more real
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'en-SG']
            });
            
            // Override chrome property
            window.chrome = {
                runtime: {}
            };
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Add realistic screen properties
            Object.defineProperty(screen, 'availWidth', {
                get: () => 1920
            });
            Object.defineProperty(screen, 'availHeight', {
                get: () => 1040
            });
        """)
        
        self.page = self.context.new_page()
        
        # Set extra HTTP headers
        self.page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9,en-SG;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        })
        
        logger.info("Browser started with advanced stealth mode")
    
    def stop(self) -> None:
        """Stop the browser."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser stopped")
    
    def navigate_to(self, url: str) -> bool:
        """Navigate to a URL.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
            logger.info(f"Navigated to {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def get_page_html(self) -> str:
        """Get the current page HTML content.
        
        Returns:
            The page HTML as a string
        """
        return self.page.content()
    
    def wait(self, seconds: float) -> None:
        """Wait for a specified number of seconds.
        
        Args:
            seconds: Number of seconds to wait
        """
        self.page.wait_for_timeout(seconds * 1000)
    
    def click_element(self, selector: str) -> bool:
        """Click an element by CSS selector.
        
        Args:
            selector: CSS selector for the element
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.page.click(selector, timeout=self.timeout)
            logger.info(f"Clicked element: {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {e}")
            return False
    
    def fill_input(self, selector: str, value: str) -> bool:
        """Fill an input field.
        
        Args:
            selector: CSS selector for the input
            value: Value to fill
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.page.fill(selector, value, timeout=self.timeout)
            logger.info(f"Filled input {selector} with value")
            return True
        except Exception as e:
            logger.error(f"Failed to fill input {selector}: {e}")
            return False
    
    def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Wait for an element to appear.
        
        Args:
            selector: CSS selector for the element
            timeout: Timeout in milliseconds (uses default if not specified)
            
        Returns:
            True if element found, False otherwise
        """
        try:
            actual_timeout = timeout or self.timeout
            # Wait for the element to be attached to the DOM
            self.page.wait_for_selector(selector, state="attached", timeout=actual_timeout)
            return True
        except PlaywrightTimeout:
            logger.error(f"Timeout waiting for selector: {selector}")
            return False
        except Exception as e:
            logger.error(f"Error waiting for selector {selector}: {e}")
            return False
    
    def get_element_text(self, selector: str) -> List[str]:
        """Get text content of all elements matching selector."""
        try:
            elements = self.page.query_selector_all(selector)
            return [el.text_content() or "" for el in elements]
        except Exception as e:
            logger.error(f"Error getting element text: {e}")
            return []
    
    def get_element_attribute(self, selector: str, attribute: str) -> List[str]:
        """Get attribute value of all elements matching selector."""
        try:
            elements = self.page.query_selector_all(selector)
            return [el.get_attribute(attribute) or "" for el in elements]
        except Exception as e:
            logger.error(f"Error getting element attribute: {e}")
            return []