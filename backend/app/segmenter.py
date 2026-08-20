import re
from typing import Dict

def clean_heading(line: str) -> str:
    """
    Cleans a heading candidate by:
    1. Stripping surrounding whitespace.
    2. Removing common markdown heading markers (e.g., #, ##).
    3. Removing leading bullets (e.g., •, ▪, -, *).
    4. Removing list numbering (e.g., 1., A., I.).
    5. Stripping leading/trailing punctuation and markdown elements.
    6. Collapsing internal whitespace.
    7. Converting to lowercase.
    """
    cleaned = line.strip()
    
    # Remove common markdown heading markers from the beginning
    cleaned = re.sub(r'^#+\s*', '', cleaned)
    
    # Remove leading bullets and list numbering
    # Matches bullet chars or number/letter followed by period/dash/parenthesis
    cleaned = re.sub(
        r'^(?:\s*(?:[•▪\-\*o\u2022\u25aa\u25fe\u25fc\u25fb]|\b(?:[0-9]+|[a-zA-Z]|[ivxIVX]+)[\.\-\)]))\s*',
        '',
        cleaned
    )
    
    # Strip leading/trailing punctuation and formatting
    cleaned = cleaned.strip("*-#_ :")
    
    # Normalize internal whitespace
    cleaned = " ".join(cleaned.split())
    
    return cleaned.lower()

def segment_text(text: str) -> Dict[str, str]:
    """
    Segments the resume text into standard sections based on keywords.
    Case-insensitive, tolerant of trailing colons and extra spacing.
    """
    # Heading mappings to normalized section names
    HEADINGS_VARIANTS = {
        "SUMMARY": ["summary", "professional summary", "about me", "profile", "personal summary"],
        "OBJECTIVE": ["objective", "career objective"],
        "TECHNICAL SKILLS": ["technical skills", "tech skills", "technical expertise", "technologies"],
        "SKILLS": ["skills", "core skills", "key skills", "skills & expertise", "skills and expertise"],
        "WORK EXPERIENCE": ["work experience", "professional experience"],
        "EMPLOYMENT": ["employment", "employment history"],
        "EXPERIENCE": ["experience", "work history", "professional background"],
        "EDUCATION": ["education", "academic qualification", "academic qualifications", "academics", "education background"],
        "PROJECTS": ["projects", "key projects", "personal projects", "academic projects"],
        "CERTIFICATIONS": ["certifications", "licenses & certifications", "certifications & licenses", "courses"]
    }

    # Flatten mapping for quick lookup
    lookup = {}
    for normalized_key, variants in HEADINGS_VARIANTS.items():
        for variant in variants:
            lookup[variant.lower()] = normalized_key

    sections: Dict[str, list] = {}
    current_section = None
    
    # Split input text into lines
    lines = text.splitlines()
    
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            if current_section:
                sections[current_section].append("")
            continue
            
        # Clean heading candidates using robust normalization
        clean_candidate = clean_heading(stripped_line)
        
        # Check if the line is a section heading
        if clean_candidate in lookup and len(clean_candidate) < 30:
            current_section = lookup[clean_candidate]
            if current_section not in sections:
                sections[current_section] = []
        else:
            if current_section:
                sections[current_section].append(stripped_line)
                
    # Format and clean the collected section texts
    final_sections: Dict[str, str] = {}
    for section_name, line_list in sections.items():
        # Clean trailing empty lines or spaces in each section
        section_text = "\n".join(line_list).strip()
        if section_text:
            final_sections[section_name] = section_text
            
    return final_sections
