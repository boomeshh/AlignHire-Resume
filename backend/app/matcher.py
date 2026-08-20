import re
from typing import List, Dict, Any
from backend.app.profile_builder import normalize_skill

# Strict years of experience regex that matches "3 years", "4 yrs", etc., but NOT "2024"
EXP_DURATION_REGEX = re.compile(r'\b(\d+)\s*(?:\+|-)?\s*(?:years?|yrs?)\b')

def match_requirements(profile: dict, requirements: list[dict]) -> list[dict]:
    """
    Matches parsed Job Description requirements against candidate profile fields.
    Validates all evidence references to ensure no orphan references exist.
    """
    fields_lookup = {f["field_id"]: f for f in profile.get("fields", [])}
    profile_field_ids = set(fields_lookup.keys())
    
    matches = []
    
    for req in requirements:
        req_id = req["requirement_id"]
        category = req["category"]
        importance = req["importance"]
        req_value = req["normalized_value"]
        req_text = req["requirement"]
        
        match_status = "NOT_FOUND"
        evidence_ref = None
        evidence = None
        explanation = ""
        
        if category == "SKILL":
            if "SKILLS-LIST" in fields_lookup:
                evidence_ref = "SKILLS-LIST"
                skills_field = fields_lookup["SKILLS-LIST"]
                
                if skills_field["status"] == "NOT_FOUND":
                    match_status = "NOT_FOUND"
                    evidence = None
                    explanation = "Skills information was not found in the candidate profile."
                else:
                    candidate_skills = skills_field["value"] or []
                    candidate_skills_normalized = [normalize_skill(s) for s in candidate_skills]
                    evidence = skills_field["evidence"]
                    
                    if req_value in candidate_skills_normalized:
                        match_status = "MATCHED"
                        explanation = f"{req_text} was found in the candidate skills evidence."
                    else:
                        match_status = "NOT_MATCHED"
                        explanation = f"{req_text} was not found in the candidate skills evidence."
            else:
                evidence_ref = None
                match_status = "NOT_FOUND"
                evidence = None
                explanation = "Skills information was not found in the candidate profile."
                
        elif category == "EXPERIENCE":
            if "EXPERIENCE-TEXT" in fields_lookup:
                evidence_ref = "EXPERIENCE-TEXT"
                exp_field = fields_lookup["EXPERIENCE-TEXT"]
                
                if exp_field["status"] == "NOT_FOUND" or not exp_field["value"]:
                    match_status = "NOT_FOUND"
                    evidence = None
                    explanation = "Experience section was not found in the candidate profile."
                else:
                    exp_text = exp_field["value"]
                    
                    # Extract only explicit duration patterns (avoid date years)
                    exp_matches = EXP_DURATION_REGEX.findall(exp_text.lower())
                    
                    if exp_matches:
                        years_list = [int(y) for y in exp_matches]
                        candidate_years = max(years_list)
                        
                        try:
                            required_years = int(req_value)
                        except ValueError:
                            required_years = 0
                            
                        evidence = exp_field["evidence"]
                        if candidate_years >= required_years:
                            match_status = "MATCHED"
                            explanation = f"Candidate has {candidate_years} years of experience, which meets the requirement of {required_years}+ years."
                        else:
                            match_status = "NOT_MATCHED"
                            explanation = f"Candidate has {candidate_years} years of experience, which does not meet the requirement of {required_years}+ years."
                    else:
                        match_status = "NOT_FOUND"
                        # Preserve evidence when section exists but no explicit duration
                        evidence = exp_field["evidence"]
                        explanation = "Experience section is present but contains no explicit duration."
            else:
                evidence_ref = None
                match_status = "NOT_FOUND"
                evidence = None
                explanation = "Experience section was not found in the candidate profile."
                
        else:
            match_status = "NOT_FOUND"
            explanation = f"Category {category} matching is not implemented in Phase 2."
            
        matches.append({
            "requirement_id": req_id,
            "requirement": req_text,
            "category": category,
            "importance": importance,
            "match_status": match_status,
            "evidence_ref": evidence_ref,
            "evidence": evidence,
            "explanation": explanation
        })
        
    # Enforce strict validation of evidence references (no orphan references)
    for m in matches:
        ref = m["evidence_ref"]
        if ref is not None and ref not in profile_field_ids:
            raise ValueError(f"Orphan evidence reference detected: {ref} is not a valid profile field ID.")
            
    return matches
