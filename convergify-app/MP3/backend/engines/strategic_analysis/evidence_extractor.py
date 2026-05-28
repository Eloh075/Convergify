"""
Evidence Extractor

Extracts evidence of skills from resume text with section identification and timeline extraction.
"""
import logging
import re
from typing import Dict, List, Optional

from .models import Evidence

logger = logging.getLogger(__name__)


class EvidenceExtractor:
    """Extract evidence from resume text"""
    
    # Common resume section headers
    SECTION_PATTERNS = {
        'Experience': [
            r'(?i)^(work\s+)?experience',
            r'(?i)^professional\s+experience',
            r'(?i)^employment\s+history',
            r'(?i)^career\s+history'
        ],
        'Education': [
            r'(?i)^education',
            r'(?i)^academic\s+background',
            r'(?i)^qualifications'
        ],
        'Skills': [
            r'(?i)^(technical\s+)?skills',
            r'(?i)^competencies',
            r'(?i)^expertise'
        ],
        'Projects': [
            r'(?i)^projects',
            r'(?i)^portfolio'
        ],
        'Certifications': [
            r'(?i)^certifications?',
            r'(?i)^licenses?'
        ]
    }
    
    # Timeline patterns
    TIMELINE_PATTERNS = [
        r'(\d{4})\s*[-–]\s*(\d{4})',  # 2018-2023
        r'(\d{4})\s*[-–]\s*present',  # 2018-present
        r'(\d+)\+?\s*years?',  # 5+ years, 3 years
        r'over\s+(\d+)\s+years?',  # over 5 years
        r'more\s+than\s+(\d+)\s+years?',  # more than 3 years
    ]
    
    def extract_evidence(
        self,
        resume_text: str,
        skill_name: str
    ) -> Evidence:
        """
        Find evidence of skill in resume
        
        Args:
            resume_text: Full resume text
            skill_name: Skill to search for
            
        Returns:
            Evidence object with findings
        """
        # Identify resume sections
        sections = self._identify_sections(resume_text)
        
        # Search for skill mentions
        text_snippets = []
        origin_locations = []
        
        # Search in full text first
        skill_pattern = re.compile(rf'\b{re.escape(skill_name)}\b', re.IGNORECASE)
        matches = list(skill_pattern.finditer(resume_text))
        
        if not matches:
            # No evidence found
            return Evidence(
                found=False,
                text_snippets=[],
                origin_locations=[],
                timeline=None,
                confidence=0.0
            )
        
        # Extract context around matches
        for match in matches[:3]:  # Limit to 3 snippets
            start = max(0, match.start() - 50)
            end = min(len(resume_text), match.end() + 50)
            snippet = resume_text[start:end].strip()
            
            # Clean up snippet
            snippet = re.sub(r'\s+', ' ', snippet)
            if start > 0:
                snippet = '...' + snippet
            if end < len(resume_text):
                snippet = snippet + '...'
            
            text_snippets.append(snippet)
            
            # Determine which section this match is in
            location = self._find_section_for_position(match.start(), sections, resume_text)
            if location and location not in origin_locations:
                origin_locations.append(location)
        
        # Extract timeline
        timeline = self._extract_timeline_from_snippets(text_snippets)
        
        # Calculate confidence based on evidence strength
        confidence = self._calculate_evidence_confidence(
            len(text_snippets),
            len(origin_locations),
            timeline is not None
        )
        
        return Evidence(
            found=True,
            text_snippets=text_snippets,
            origin_locations=origin_locations,
            timeline=timeline,
            confidence=confidence
        )
    
    def _identify_sections(self, resume_text: str) -> Dict[str, tuple]:
        """
        Identify resume sections (Experience, Education, Skills)
        
        Args:
            resume_text: Full resume text
            
        Returns:
            Dictionary mapping section name to (start_pos, end_pos)
        """
        sections = {}
        lines = resume_text.split('\n')
        
        current_section = None
        section_start = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check if this line is a section header
            for section_name, patterns in self.SECTION_PATTERNS.items():
                for pattern in patterns:
                    if re.match(pattern, line_stripped):
                        # Save previous section
                        if current_section:
                            section_end = sum(len(l) + 1 for l in lines[:i])
                            sections[current_section] = (section_start, section_end)
                        
                        # Start new section
                        current_section = section_name
                        section_start = sum(len(l) + 1 for l in lines[:i])
                        break
        
        # Save last section
        if current_section:
            sections[current_section] = (section_start, len(resume_text))
        
        return sections
    
    def _find_section_for_position(
        self,
        position: int,
        sections: Dict[str, tuple],
        resume_text: str
    ) -> Optional[str]:
        """
        Find which section a position belongs to
        
        Args:
            position: Character position in resume
            sections: Dictionary of section ranges
            resume_text: Full resume text
            
        Returns:
            Section name or None
        """
        for section_name, (start, end) in sections.items():
            if start <= position < end:
                return section_name
        
        # If no section found, try to infer from context
        # Check if position is in first 20% of document (likely summary/header)
        if position < len(resume_text) * 0.2:
            return "Summary"
        
        return "Other"
    
    def _extract_timeline_from_snippets(
        self,
        snippets: List[str]
    ) -> Optional[str]:
        """
        Extract timeline from evidence text
        
        Args:
            snippets: List of text snippets
            
        Returns:
            Timeline string or None
        """
        for snippet in snippets:
            for pattern in self.TIMELINE_PATTERNS:
                match = re.search(pattern, snippet, re.IGNORECASE)
                if match:
                    return match.group(0)
        
        return None
    
    def _calculate_evidence_confidence(
        self,
        snippet_count: int,
        location_count: int,
        has_timeline: bool
    ) -> float:
        """
        Calculate confidence score based on evidence strength
        
        Args:
            snippet_count: Number of evidence snippets
            location_count: Number of different sections
            has_timeline: Whether timeline was found
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.0
        
        # Base confidence from snippet count
        if snippet_count >= 3:
            confidence += 0.4
        elif snippet_count == 2:
            confidence += 0.3
        elif snippet_count == 1:
            confidence += 0.2
        
        # Bonus for multiple locations
        if location_count >= 2:
            confidence += 0.3
        elif location_count == 1:
            confidence += 0.2
        
        # Bonus for timeline
        if has_timeline:
            confidence += 0.2
        
        # Additional bonus for strong evidence (3+ snippets + timeline)
        if snippet_count >= 3 and has_timeline:
            confidence += 0.1
        
        return min(confidence, 1.0)
