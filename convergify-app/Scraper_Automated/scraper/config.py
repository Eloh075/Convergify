"""Configuration management for the job scraper."""

import os
import yaml
from dataclasses import dataclass
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()


@dataclass
class ScraperConfig:
    """Configuration for the job scraper."""
    browser_type: str
    headless_mode: bool
    default_site: str
    max_pages: int
    delay_between_requests: int
    timeout_seconds: int
    supabase_url: str
    supabase_key: str
    database_table: str


@dataclass
class SiteConfig:
    """Configuration for a specific job site."""
    name: str
    base_url: str
    enabled: bool


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    # Get the directory where this config.py file is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try to find config file in multiple locations
    possible_paths = [
        config_path,  # Current working directory
        os.path.join(script_dir, "..", config_path),  # Parent directory (scraper/)
        os.path.join(script_dir, "..", "..", config_path),  # Project root
    ]
    
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            logger.info(f"Loading config from: {abs_path}")
            with open(abs_path, 'r') as f:
                return yaml.safe_load(f)
    
    # If not found, return default config
    logger.warning(f"Config file not found at {config_path}, using defaults")
    return {}


def get_site_config(config: Dict[str, Any], site_name: str) -> Optional[SiteConfig]:
    """Get configuration for a specific site."""
    sites = config.get('sites', {})
    
    # Try exact match first (case-insensitive)
    site_data = sites.get(site_name.lower())
    
    # If not found, try to match by site name field
    if not site_data:
        for key, value in sites.items():
            if isinstance(value, dict) and value.get('name', '').lower() == site_name.lower():
                site_data = value
                break
    
    if site_data:
        return SiteConfig(
            name=site_data.get('name', site_name),
            base_url=site_data.get('base_url', ''),
            enabled=site_data.get('enabled', True)
        )
    return None


def create_scraper_config() -> ScraperConfig:
    """Create scraper configuration from environment and config file."""
    config = load_config()
    
    scraping_config = config.get('scraping', {})
    database_config = config.get('database', {})
    
    return ScraperConfig(
        browser_type=os.getenv('BROWSER_TYPE', 'chromium'),
        headless_mode=os.getenv('HEADLESS_MODE', 'true').lower() == 'true',
        default_site=os.getenv('DEFAULT_SITE', 'LinkedIn'),
        max_pages=int(os.getenv('MAX_PAGES', scraping_config.get('max_pages_per_search', 10))),
        delay_between_requests=int(os.getenv('DELAY_BETWEEN_REQUESTS', scraping_config.get('delay_between_requests', 2))),
        timeout_seconds=int(os.getenv('TIMEOUT_SECONDS', scraping_config.get('timeout_seconds', 30))),
        supabase_url=os.getenv('SUPABASE_URL'),
        supabase_key=os.getenv('SUPABASE_KEY'),
        database_table=database_config.get('table_name', 'job_listings')
    )