import re
from typing import List, Dict, Any
from backend.app.profile_builder import normalize_skill

def parse_job_description(job_description: str) -> List[Dict[str, Any]]:
    """
    Parses a Job Description string to extract required/preferred skills and experience.
    Returns a list of requirement dictionaries.
    Supports parsing lines and splitting them by sentences (using periods/semicolons)
    to handle multiple constraints on a single line.
    """
    # Safeguard for empty or whitespace-only JD
    if not job_description or not job_description.strip():
        return []

    lines = job_description.splitlines()
    requirements = []
    seen_skills = set()
    
    current_importance = "REQUIRED"
    
    skill_idx = 1
    exp_idx = 1
    
    # Controlled vocabulary mapping to standard display name
    vocab_patterns = {
        "Python": r'\bpython\b',
        "Java": r'\bjava\b',
        "JavaScript": r'\bjavascript\b|\bjs\b',
        "TypeScript": r'\btypescript\b|\bts\b',
        "SQL": r'\bsql\b',
        "AWS": r'\baws\b',
        "Azure": r'\bazure\b',
        "GCP": r'\bgcp\b|\bgoogle cloud\b',
        "Docker": r'\bdocker\b',
        "Kubernetes": r'\bkubernetes\b|\bk8s\b',
        "Git": r'\bgit\b',
        "FastAPI": r'\bfastapi\b',
        "Django": r'\bdjango\b',
        "Flask": r'\bflask\b',
        "React": r'\breact(?:js)?\b',
        "Node.js": r'\bnode(?:\.js)?\b',
        "MongoDB": r'\bmongo(?:db)?\b',
        "PostgreSQL": r'\bpostgres(?:ql)?\b',
        "MySQL": r'\bmysql\b',
        "Machine Learning": r'\bmachine learning\b|\bml\b',
        "PyTorch": r'\bpytorch\b',
        "TensorFlow": r'\btensorflow\b',
        "Pandas": r'\bpandas\b',
        "NumPy": r'\bnumpy\b'
    }
    
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        lower_line = cleaned_line.lower()
        
        # Check if the line is a block header setting the context for subsequent lines
        is_header = False
        if len(cleaned_line) < 30 and (cleaned_line.endswith(":") or not any(char.isalnum() for char in cleaned_line if char not in ':- ')):
            if any(k in lower_line for k in ["nice to have", "preferred", "good to have", "bonus", "plus"]):
                current_importance = "PREFERRED"
                is_header = True
            elif any(k in lower_line for k in ["required", "must have", "mandatory"]):
                current_importance = "REQUIRED"
                is_header = True
                
        if is_header:
            continue
            
        # Split line into sentence-level clauses (by period or semicolon)
        segments = re.split(r'[\.;]', cleaned_line)
        for segment in segments:
            cleaned_segment = segment.strip()
            if not cleaned_segment:
                continue
                
            lower_segment = cleaned_segment.lower()
            
            # Determine segment-level importance
            segment_importance = current_importance
            if any(k in lower_segment for k in ["nice to have", "preferred", "good to have", "bonus", "plus"]):
                segment_importance = "PREFERRED"
            elif any(k in lower_segment for k in ["required", "must have", "mandatory"]):
                segment_importance = "REQUIRED"
                
            # Extract skills from segment
            matches_on_segment = []
            for skill, pattern in vocab_patterns.items():
                match = re.search(pattern, lower_segment)
                if match:
                    matches_on_segment.append((match.start(), skill))
                    
            # Sort skills by occurrence index
            matches_on_segment.sort(key=lambda x: x[0])
            
            for _, skill in matches_on_segment:
                skill_normalized = normalize_skill(skill)
                if skill_normalized not in seen_skills:
                    seen_skills.add(skill_normalized)
                    requirements.append({
                        "requirement_id": f"REQ-SKILL-{skill_idx:03d}",
                        "category": "SKILL",
                        "requirement": skill,
                        "normalized_value": skill_normalized,
                        "importance": segment_importance
                    })
                    skill_idx += 1
                    
            # Extract experience from segment
            exp_match = re.search(r'(\d+)\s*(?:\+|-)?\s*years?\s*(?:of\s*)?(?:experience|exp)?', lower_segment)
            if exp_match:
                years = exp_match.group(1)
                display_phrase = f"{years}+ years experience" if '+' in exp_match.group(0) or 'plus' in lower_segment else f"{years} years experience"
                requirements.append({
                    "requirement_id": f"REQ-EXP-{exp_idx:03d}",
                    "category": "EXPERIENCE",
                    "requirement": display_phrase,
                    "normalized_value": years,
                    "importance": segment_importance
                })
                exp_idx += 1
                
    return requirements
