"""
Parser Module

Responsible for:
1. Extracting candidate fields from specific segmented sections:
   - Full Name (typically from top/Contact section)
   - Email (regex pattern matching, from Contact section)
   - Phone (regex pattern matching, from Contact section)
   - Skills (matching key skills against a dictionary or list, from Skills section)
   - Education (extracting degrees/institutions, from Education section)
2. Generating evidence strings for each field indicating exactly where the information came from.
3. Formatting the parsed output into CandidateProfile structure.
"""

from typing import Dict
from app.models import CandidateProfile

def parse_profile(segmented_data: Dict[str, str]) -> CandidateProfile:
    """
    Parses candidate profile fields from the segmented text.
    
    TODO:
    - Extract Full Name: Look in Contact/Header section, fall back to first line.
    - Extract Email: Regex-based match in contact/header section.
    - Extract Phone: Regex-based match for phone formats.
    - Extract Skills: Match raw skills text against allowed/known skills list or parse lines.
    - Extract Education: Parse degree, institution, graduation year from Education section.
    - Build CandidateField objects with status (FOUND/NOT_FOUND/AMBIGUOUS), evidence, and source section.
    - Construct and return CandidateProfile.
    """
    # TODO: Implement parser logic
    pass
