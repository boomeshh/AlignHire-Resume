import re
from typing import Optional, Dict, Any

# Reasonable deterministic regex for email
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

# Indian phone format regex: supports 9876543210, +91 9876543210, +91-9876543210, 98765 43210
PHONE_REGEX = re.compile(r'(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b')

def parse_candidate(text: str) -> Dict[str, Any]:
    """
    Extracts name, email, and phone from the resume text.
    Returns a dictionary of fields (where values can be None if not found).
    """
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text)
    }

def extract_email(text: str) -> Optional[str]:
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    match = PHONE_REGEX.search(text)
    if match:
        return match.group(0).strip()
    return None

def extract_name(text: str) -> Optional[str]:
    """
    Uses a conservative heuristic to identify the candidate's name.
    Looks at the first few lines and applies exclusion filters.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None

    # Check the first 3 lines
    for line in lines[:3]:
        # Remove unwanted punctuation/formatting (like bullet points or brackets)
        cleaned = re.sub(r'[^a-zA-Z\s\.-]', '', line).strip()
        
        # Word count check: typically a name is 1 to 4 words
        words = cleaned.split()
        if not (1 <= len(words) <= 4):
            continue

        # Exclude if it looks like a label, contact info, or header variant
        lower_line = line.lower()
        ignore_keywords = [
            "resume", "curriculum", "vitae", "cv", "contact", 
            "email", "phone", "address", "page", "summary", 
            "objective", "skills", "experience", "education",
            "certifications", "projects"
        ]
        if any(keyword in lower_line for keyword in ignore_keywords):
            continue

        # Exclude lines with digits or email patterns
        if any(char.isdigit() for char in line) or "@" in line or ":" in line:
            continue

        # Return the cleaned name
        return cleaned

    return None
