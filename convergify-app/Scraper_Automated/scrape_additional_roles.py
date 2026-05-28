"""Scrape additional job roles with suffix expansion."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from scrape_linkedin_with_suffixes import scrape_with_suffixes


# Additional job roles to scrape
JOB_ROLES = [
    'Data Analyst',
    'AI Engineer', 
    'Full Stack Developer',
    'Business Analyst',
    'Product Manager'
]


def scrape_all_roles():
    """Scrape all additional job roles."""
    for i, role in enumerate(JOB_ROLES, 1):
        logger.info(f'\n\n{"#"*80}')
        logger.info(f'# SCRAPING {i}/{len(JOB_ROLES)}: {role}')
        logger.info(f'{"#"*80}\n')
        
        results = scrape_with_suffixes(role)
        
        logger.info(f'\nCompleted {role}: {results["total_new"]} new, {results["total_existing"]} existing')
        logger.info(f'{"="*80}\n')


if __name__ == "__main__":
    scrape_all_roles()
