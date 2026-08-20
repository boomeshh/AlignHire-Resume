import re
from typing import Optional, Dict, Any

# Reasonable deterministic regex for email with proper TLD boundary (no trailing periods)
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]*[a-zA-Z0-9-]')

# Indian phone format regex: supports 9876543210, +91 9876543210, +91-9876543210, +91 98765 43210, 98765 43210
# Uses (?<!\d) lookbehind to avoid matching internal digits of longer sequences
PHONE_REGEX = re.compile(r'(?<!\d)(?:\+?91[\s\-]*)?[6-9]\d{4}[\s\-]?\d{5}\b')

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
    1. Inspects the first several non-empty lines (up to 10).
    2. Skips lines with emails or phone numbers.
    3. Skips URLs.
    4. Skips known section headings and obvious job titles.
    5. Normalizes candidate name (collapsing spaces, stripping trailing punctuation).
    """
    if not text:
        return None

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None

    # Check the first 10 non-empty lines
    for line in lines[:10]:
        # Skip lines containing an email
        if "@" in line or EMAIL_REGEX.search(line):
            continue

        # Skip lines containing a phone number
        if PHONE_REGEX.search(line):
            continue

        # Skip URLs
        lower_line = line.lower()
        if any(url_indicator in lower_line for url_indicator in ("http://", "https://", "www.", "github.com", "linkedin.com")):
            continue

        # Handle lines starting with "Name:" or skip lines with other colons (usually metadata)
        name_matched = re.match(r'^(?:name)\s*:\s*(.*)$', line, re.IGNORECASE)
        candidate_line = line
        if name_matched:
            candidate_line = name_matched.group(1).strip()
            lower_line = candidate_line.lower()
        elif ":" in line:
            continue

        # Check for ignored section headings and job titles
        words = re.findall(r'[a-zA-Z]+', lower_line)
        ignore_words = {
            "resume", "curriculum", "vitae", "cv", "contact", 
            "email", "phone", "address", "page", "summary", 
            "objective", "skills", "experience", "education",
            "certifications", "projects", "engineer", "developer",
            "analyst", "manager", "consultant", "architect",
            "specialist", "intern", "student", "professional",
            "portfolio", "profile", "about", "tel", "mobile",
            "lead", "director", "associate", "university",
            "college", "school", "technologies"
        }
        if any(word in ignore_words for word in words):
            continue

        # Remove unwanted formatting characters (allow letters, spaces, dots, dashes)
        cleaned = re.sub(r'[^a-zA-Z\s\.-]', '', candidate_line).strip()
        if not cleaned:
            continue
            
        # Word count check: typically 1 to 4 words
        cleaned_words = cleaned.split()
        if not (1 <= len(cleaned_words) <= 4):
            continue

        # Collapse multiple spaces and strip trailing/leading punctuation
        final_name = " ".join(cleaned_words).strip(".- ")
        if len(final_name) < 2:
            continue

        return final_name

    return None
