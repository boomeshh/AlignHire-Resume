from typing import List, Dict, Any

def build_fit_report(matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Translates requirement matches into a structured fit report.
    Determines confidence levels deterministically based on the match status.
    """
    report = []
    
    confidence_map = {
        "MATCHED": "high",
        "PARTIAL": "medium",
        "NOT_MATCHED": "high",
        "NOT_FOUND": "low"
    }
    
    for m in matches:
        status = m.get("match_status", "NOT_FOUND")
        confidence = confidence_map.get(status, "low")
        
        report.append({
            "requirement": m["requirement"],
            "requirement_id": m["requirement_id"],
            "match_status": status,
            "explanation": m["explanation"],
            "evidence_ref": m["evidence_ref"],
            "evidence": m["evidence"],
            "confidence": confidence
        })
        
    return report
