"""
Diff Generator

Generates change highlights between original and optimized resumes.
"""
import logging
import difflib
from typing import List, Tuple

from .models import Change

logger = logging.getLogger(__name__)


class DiffGenerator:
    """Generate change highlights"""
    
    def generate_diff(
        self,
        original: str,
        optimized: str,
        change_reasons: List[dict] = None
    ) -> List[Change]:
        """
        Generate list of changes with reasons
        
        Args:
            original: Original resume text
            optimized: Optimized resume text
            change_reasons: Optional list of change reasons from LLM
            
        Returns:
            List of Change objects
        """
        logger.info("Generating diff between original and optimized resume")
        
        changes = []
        
        # Split into sections for better diff
        original_sections = self._split_into_sections(original)
        optimized_sections = self._split_into_sections(optimized)
        
        # Compare sections
        for section_name in set(list(original_sections.keys()) + list(optimized_sections.keys())):
            original_text = original_sections.get(section_name, "")
            optimized_text = optimized_sections.get(section_name, "")
            
            if original_text != optimized_text:
                # Find specific changes within section
                section_changes = self._identify_changes_in_section(
                    original_text,
                    optimized_text,
                    section_name,
                    change_reasons
                )
                changes.extend(section_changes)
        
        logger.info(f"Generated {len(changes)} changes")
        return changes
    
    def _split_into_sections(self, text: str) -> dict:
        """
        Split resume into sections
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary mapping section name to text
        """
        sections = {}
        current_section = "Header"
        current_text = []
        
        lines = text.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check if this is a section header
            if self._is_section_header(line_stripped):
                # Save previous section
                if current_text:
                    sections[current_section] = '\n'.join(current_text)
                
                # Start new section
                current_section = line_stripped
                current_text = []
            else:
                current_text.append(line)
        
        # Save last section
        if current_text:
            sections[current_section] = '\n'.join(current_text)
        
        return sections
    
    def _is_section_header(self, line: str) -> bool:
        """Check if line is a section header"""
        headers = [
            'experience', 'education', 'skills', 'projects',
            'certifications', 'summary', 'objective', 'awards'
        ]
        return any(header in line.lower() for header in headers) and len(line) < 50
    
    def _identify_changes_in_section(
        self,
        original: str,
        optimized: str,
        section_name: str,
        change_reasons: List[dict] = None
    ) -> List[Change]:
        """
        Identify specific changes within a section
        
        Args:
            original: Original section text
            optimized: Optimized section text
            section_name: Name of the section
            change_reasons: Optional change reasons from LLM
            
        Returns:
            List of Change objects
        """
        changes = []
        
        # Use difflib to find differences
        original_lines = original.split('\n')
        optimized_lines = optimized.split('\n')
        
        matcher = difflib.SequenceMatcher(None, original_lines, optimized_lines)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                # Text was modified
                original_text = '\n'.join(original_lines[i1:i2])
                optimized_text = '\n'.join(optimized_lines[j1:j2])
                
                # Determine change type
                change_type = self._determine_change_type(original_text, optimized_text)
                
                # Find matching reason from LLM if available
                reason = self._find_matching_reason(
                    original_text,
                    optimized_text,
                    change_reasons
                )
                
                if not reason:
                    reason = self._generate_default_reason(change_type, original_text, optimized_text)
                
                change = Change(
                    change_type=change_type,
                    original_text=original_text[:200],  # Limit length
                    optimized_text=optimized_text[:200],
                    reason=reason,
                    location=section_name,
                    confidence=0.8
                )
                changes.append(change)
            
            elif tag == 'insert':
                # New content added
                optimized_text = '\n'.join(optimized_lines[j1:j2])
                
                reason = "Added new content to strengthen this section"
                
                change = Change(
                    change_type="Enhancement",
                    original_text="",
                    optimized_text=optimized_text[:200],
                    reason=reason,
                    location=section_name,
                    confidence=0.7
                )
                changes.append(change)
            
            elif tag == 'delete':
                # Content removed (should be rare with no-fabrication rule)
                original_text = '\n'.join(original_lines[i1:i2])
                
                reason = "Removed redundant or less relevant content"
                
                change = Change(
                    change_type="Formatting",
                    original_text=original_text[:200],
                    optimized_text="",
                    reason=reason,
                    location=section_name,
                    confidence=0.6
                )
                changes.append(change)
        
        return changes
    
    def _determine_change_type(self, original: str, optimized: str) -> str:
        """Determine the type of change"""
        original_lower = original.lower()
        optimized_lower = optimized.lower()
        
        # Check if it's mostly the same words (formatting)
        original_words = set(original_lower.split())
        optimized_words = set(optimized_lower.split())
        
        overlap = len(original_words & optimized_words) / max(len(original_words), 1)
        
        if overlap > 0.8:
            return "Formatting"
        elif overlap > 0.5:
            return "Enhancement"
        else:
            return "Clarification"
    
    def _find_matching_reason(
        self,
        original: str,
        optimized: str,
        change_reasons: List[dict] = None
    ) -> str:
        """Find matching reason from LLM-provided reasons"""
        if not change_reasons:
            return ""
        
        # Try to find a reason that mentions similar text
        for reason_data in change_reasons:
            if 'original' in reason_data and 'reason' in reason_data:
                if reason_data['original'][:50] in original[:50]:
                    return reason_data['reason']
        
        return ""
    
    def _generate_default_reason(
        self,
        change_type: str,
        original: str,
        optimized: str
    ) -> str:
        """Generate a default reason based on change type"""
        if change_type == "Enhancement":
            return "Enhanced description with more specific details and quantifiable achievements"
        elif change_type == "Formatting":
            return "Improved formatting and structure for better readability"
        elif change_type == "Clarification":
            return "Clarified and strengthened the description"
        elif change_type == "Reordering":
            return "Reordered content to prioritize most relevant information"
        else:
            return "Optimized content for better impact"
