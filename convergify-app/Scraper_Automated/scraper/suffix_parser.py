"""Utility to parse job roles and extract suffixes."""

from typing import Tuple, Optional


# Known suffixes that should be separated
KNOWN_SUFFIXES = [
    " Intern",
    " Internship", 
    " Graduate",
    " Junior",
    " Associate",
    " Senior",
    " Lead",
    " Principal",
    " Staff",
    " Entry Level",
    " Mid Level",
    " Senior Level"
]


def parse_job_role_and_suffix(full_job_role: str) -> Tuple[str, Optional[str]]:
    """
    Parse a full job role into base role and suffix.
    
    Args:
        full_job_role: Full job role like "Software Engineer Intern"
        
    Returns:
        Tuple of (base_role, suffix) where suffix can be None
    """
    # Check for known suffixes
    for suffix in KNOWN_SUFFIXES:
        if full_job_role.endswith(suffix):
            base_role = full_job_role[:-len(suffix)].strip()
            return base_role, suffix.strip()
    
    # No suffix found
    return full_job_role, None


def combine_job_role_and_suffix(base_role: str, suffix: Optional[str]) -> str:
    """
    Combine base role and suffix back into full job role.
    
    Args:
        base_role: Base job role like "Software Engineer"
        suffix: Suffix like "Intern" or None
        
    Returns:
        Full job role like "Software Engineer Intern"
    """
    if suffix:
        return f"{base_role} {suffix}"
    return base_role