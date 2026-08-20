from typing import List, Dict, Any

def calculate_fit_score(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes a deterministic fit score (0 to 100) based on matched requirements.
    REQUIRED requirements are weighted at 80%, and PREFERRED requirements at 20%.
    Handles edge cases (e.g. only required, only preferred, or no requirements) safely.
    """
    # Initialize counts for breakdown
    req_counts = {"matched": 0, "partial": 0, "not_matched": 0, "not_found": 0}
    pref_counts = {"matched": 0, "partial": 0, "not_matched": 0, "not_found": 0}
    
    weights = {
        "MATCHED": 1.0,
        "PARTIAL": 0.5,
        "NOT_MATCHED": 0.0,
        "NOT_FOUND": 0.0
    }
    
    req_total_points = 0.0
    pref_total_points = 0.0
    
    req_count = 0
    pref_count = 0
    
    for m in matches:
        importance = m.get("importance", "REQUIRED")
        status = m.get("match_status", "NOT_FOUND")
        
        status_key = status.lower()
        if importance == "REQUIRED":
            req_count += 1
            if status_key in req_counts:
                req_counts[status_key] += 1
            req_total_points += weights.get(status, 0.0)
        else:
            pref_count += 1
            if status_key in pref_counts:
                pref_counts[status_key] += 1
            pref_total_points += weights.get(status, 0.0)
            
    # Calculate fit score avoiding division by zero
    if req_count > 0 and pref_count > 0:
        req_score = req_total_points / req_count
        pref_score = pref_total_points / pref_count
        final_score = (req_score * 0.8) + (pref_score * 0.2)
        score = round(final_score * 100)
    elif req_count > 0:
        req_score = req_total_points / req_count
        score = round(req_score * 100)
    elif pref_count > 0:
        pref_score = pref_total_points / pref_count
        score = round(pref_score * 100)
    else:
        score = 0
        
    return {
        "score": int(score),
        "breakdown": {
            "required": req_counts,
            "preferred": pref_counts
        }
    }
