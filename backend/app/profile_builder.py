import re
from typing import Dict, Any, List

def normalize_skill(skill: str) -> str:
    """
    Unified skill normalization contract.
    Used by profile_builder, jd_parser, and matcher.
    """
    cleaned = skill.strip().lower()
    # Collapse internal spaces
    cleaned = " ".join(cleaned.split())
    # Normalize common aliases
    aliases = {
        "js": "javascript",
        "ts": "typescript",
        "google cloud": "gcp",
        "postgres": "postgresql",
        "reactjs": "react",
        "nodejs": "node.js",
        "mongo": "mongodb",
    }
    return aliases.get(cleaned, cleaned)

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extracts vocabulary skills from a text block.
    Uses case-insensitive regex matching with word boundaries,
    removes duplicates, and preserves display format and first-occurrence order.
    """
    vocab_patterns = {
        "Python": [r'\bpython\b'],
        "Java": [r'\bjava\b'],
        "JavaScript": [r'\bjavascript\b', r'\bjs\b'],
        "TypeScript": [r'\btypescript\b', r'\bts\b'],
        "SQL": [r'\bsql\b'],
        "AWS": [r'\baws\b'],
        "Azure": [r'\bazure\b'],
        "GCP": [r'\bgcp\b', r'\bgoogle cloud\b'],
        "Docker": [r'\bdocker\b'],
        "Kubernetes": [r'\bkubernetes\b', r'\bk8s\b'],
        "Git": [r'\bgit\b'],
        "FastAPI": [r'\bfastapi\b'],
        "Django": [r'\bdjango\b'],
        "Flask": [r'\bflask\b'],
        "React": [r'\breact(?:js)?\b'],
        "Node.js": [r'\bnode(?:\.js)?\b'],
        "MongoDB": [r'\bmongo(?:db)?\b'],
        "PostgreSQL": [r'\bpostgres(?:ql)?\b'],
        "MySQL": [r'\bmysql\b'],
        "Machine Learning": [r'\bmachine learning\b', r'\bml\b'],
        "PyTorch": [r'\bpytorch\b'],
        "TensorFlow": [r'\btensorflow\b'],
        "Pandas": [r'\bpandas\b'],
        "NumPy": [r'\bnumpy\b']
    }
    
    lower_text = text.lower()
    skill_first_index = {}
    
    for skill, patterns in vocab_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, lower_text)
            if match:
                idx = match.start()
                if skill not in skill_first_index or idx < skill_first_index[skill]:
                    skill_first_index[skill] = idx
                    
    # Return sorted by first occurrence index to satisfy deterministic order
    return sorted(skill_first_index.keys(), key=lambda x: skill_first_index[x])

def build_profile(candidate: dict, sections: dict) -> dict:
    """
    Main entry point to construct candidate profiles.
    Generates evidence-backed fields for Candidate Info, Skills, Experience, and Education.
    Asserts uniqueness of all field IDs before returning.
    """
    fields = []
    
    # 1. CANDIDATE-NAME
    name = candidate.get("name")
    fields.append({
        "field_id": "CANDIDATE-NAME",
        "category": "Candidate Info",
        "status": "FOUND" if name else "NOT_FOUND",
        "value": name if name else None,
        "evidence": name if name else None,
        "source_section": "HEADER"
    })
    
    # 2. CANDIDATE-EMAIL
    email = candidate.get("email")
    fields.append({
        "field_id": "CANDIDATE-EMAIL",
        "category": "Candidate Info",
        "status": "FOUND" if email else "NOT_FOUND",
        "value": email if email else None,
        "evidence": email if email else None,
        "source_section": "HEADER"
    })
    
    # 3. CANDIDATE-PHONE
    phone = candidate.get("phone")
    fields.append({
        "field_id": "CANDIDATE-PHONE",
        "category": "Candidate Info",
        "status": "FOUND" if phone else "NOT_FOUND",
        "value": phone if phone else None,
        "evidence": phone if phone else None,
        "source_section": "HEADER"
    })
    
    # 4. SKILLS-LIST
    skills_sec = None
    if "SKILLS" in sections:
        skills_sec = "SKILLS"
    elif "TECHNICAL SKILLS" in sections:
        skills_sec = "TECHNICAL SKILLS"
        
    skills_text = ""
    if skills_sec:
        skills_text = sections[skills_sec]
    else:
        # Fallback: scan all sections
        skills_text = "\n".join(sections.values())
        
    extracted_skills = extract_skills_from_text(skills_text) if skills_text else []
    
    if extracted_skills:
        evidence = sections[skills_sec] if skills_sec else ", ".join(extracted_skills)
        source_section = skills_sec if skills_sec else "SUMMARY"
        
        fields.append({
            "field_id": "SKILLS-LIST",
            "category": "Skills",
            "status": "FOUND",
            "value": extracted_skills,
            "evidence": evidence,
            "source_section": source_section
        })
    else:
        fields.append({
            "field_id": "SKILLS-LIST",
            "category": "Skills",
            "status": "NOT_FOUND",
            "value": None,
            "evidence": None,
            "source_section": "SKILLS"
        })
        
    # 5. EXPERIENCE-TEXT
    exp_sec = None
    for s in ("EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT"):
        if s in sections:
            exp_sec = s
            break
            
    if exp_sec:
        fields.append({
            "field_id": "EXPERIENCE-TEXT",
            "category": "Experience",
            "status": "FOUND",
            "value": sections[exp_sec],
            "evidence": sections[exp_sec],
            "source_section": exp_sec
        })
    else:
        fields.append({
            "field_id": "EXPERIENCE-TEXT",
            "category": "Experience",
            "status": "NOT_FOUND",
            "value": None,
            "evidence": None,
            "source_section": "EXPERIENCE"
        })
        
    # 6. EDUCATION-TEXT
    if "EDUCATION" in sections:
        fields.append({
            "field_id": "EDUCATION-TEXT",
            "category": "Education",
            "status": "FOUND",
            "value": sections["EDUCATION"],
            "evidence": sections["EDUCATION"],
            "source_section": "EDUCATION"
        })
    else:
        fields.append({
            "field_id": "EDUCATION-TEXT",
            "category": "Education",
            "status": "NOT_FOUND",
            "value": None,
            "evidence": None,
            "source_section": "EDUCATION"
        })
        
    # Ensure all field IDs are unique
    field_ids = [field["field_id"] for field in fields]
    assert len(field_ids) == len(set(field_ids)), "Duplicate field IDs detected in profile"
        
    return {"fields": fields}
