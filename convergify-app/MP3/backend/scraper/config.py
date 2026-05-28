"""Configuration management for the MyCareersFuture scraper."""

import logging
from dataclasses import dataclass, field
from typing import List


@dataclass
class ScraperConfig:
    """Configuration class for the MyCareersFuture scraper."""
    
    # Rate Limiting
    delay_seconds: float = 2.0
    max_retries: int = 3
    backoff_multiplier: float = 2.0
    
    # Browser Settings
    headless: bool = True
    user_agent: str = "MyCareersFuture-Research-Scraper/1.0"
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # Content Loading
    page_load_timeout: int = 30
    element_wait_timeout: int = 10
    
    # Data Processing
    max_listings_per_session: int = 10000
    enable_skills_mapping: bool = True
    enable_data_validation: bool = True
    
    # Export Settings
    export_formats: List[str] = field(default_factory=lambda: ["csv", "json"])
    output_directory: str = "./scraped_data"
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.delay_seconds < 0:
            raise ValueError("delay_seconds must be non-negative")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.backoff_multiplier <= 0:
            raise ValueError("backoff_multiplier must be positive")
        if self.page_load_timeout <= 0:
            raise ValueError("page_load_timeout must be positive")
        if self.element_wait_timeout <= 0:
            raise ValueError("element_wait_timeout must be positive")


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )