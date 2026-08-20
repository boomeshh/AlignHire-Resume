from typing import Dict

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
            
        # Clean heading candidates: strip common punctuation like colons, dashes, asterisks
        clean_candidate = stripped_line.rstrip(":").strip("*-#_ ").lower()
        
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
