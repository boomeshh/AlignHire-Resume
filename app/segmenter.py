"""
Segmenter Module

Responsible for:
1. Defining a fixed allowlist of section headings (e.g., "Education", "Skills", "Experience", "Contact").
2. Scanning the extracted raw text to locate these section headers.
3. Segmenting the text into a dictionary mapping section names to their text content.
4. Normalizing the section keys to ensure deterministic output.
"""

from typing import Dict

# TODO: Define fixed section allowlist (e.g., contact, education, skills, experience, summary)
SECTION_ALLOWLIST = [
    "contact",
    "education",
    "skills",
    "experience",
    "summary",
    "projects"
]

def segment_text(raw_text: str) -> Dict[str, str]:
    """
    Segments the raw resume text into distinct sections based on the allowlist.
    
    TODO:
    - Normalize text lines (strip whitespace, lowercase for header matching).
    - Detect lines that look like section headers from the allowlist.
    - Group text content between detected headers into respective sections.
    - Return a dictionary mapping normalized section name to section text.
    """
    # TODO: Implement segmentation logic
    pass
