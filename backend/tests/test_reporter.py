from backend.app.reporter import build_fit_report

def test_build_fit_report_fields():
    matches = [
        {
            "requirement_id": "REQ-SKILL-001",
            "requirement": "Python",
            "category": "SKILL",
            "importance": "REQUIRED",
            "match_status": "MATCHED",
            "evidence_ref": "SKILLS-LIST",
            "evidence": "Python, SQL",
            "explanation": "Python was found in the candidate skills evidence."
        },
        {
            "requirement_id": "REQ-SKILL-002",
            "requirement": "Docker",
            "category": "SKILL",
            "importance": "PREFERRED",
            "match_status": "NOT_MATCHED",
            "evidence_ref": "SKILLS-LIST",
            "evidence": "Python, SQL",
            "explanation": "Docker was not found in the candidate skills evidence."
        },
        {
            "requirement_id": "REQ-EXP-001",
            "requirement": "3+ years experience",
            "category": "EXPERIENCE",
            "importance": "REQUIRED",
            "match_status": "NOT_FOUND",
            "evidence_ref": "EXPERIENCE-TEXT",
            "evidence": None,
            "explanation": "No years of experience could be determined."
        }
    ]

    report = build_fit_report(matches)
    assert len(report) == 3

    # Check fields are preserved
    item0 = report[0]
    assert item0["requirement_id"] == "REQ-SKILL-001"
    assert item0["requirement"] == "Python"
    assert item0["match_status"] == "MATCHED"
    assert item0["evidence_ref"] == "SKILLS-LIST"
    assert item0["evidence"] == "Python, SQL"
    assert item0["explanation"] == "Python was found in the candidate skills evidence."
    assert item0["confidence"] == "high"

    # Check confidence mapping rules
    item1 = report[1]
    assert item1["match_status"] == "NOT_MATCHED"
    assert item1["confidence"] == "high"

    item2 = report[2]
    assert item2["match_status"] == "NOT_FOUND"
    assert item2["confidence"] == "low"

def test_evidence_traceability():
    # Verify that evidence_ref maps to actual profile fields
    # Here we mock matches that specify SKILLS-LIST and EXPERIENCE-TEXT
    profile_field_ids = {"SKILLS-LIST", "EXPERIENCE-TEXT", "EDUCATION-TEXT", "CANDIDATE-NAME"}
    
    matches = [
        {
            "requirement_id": "REQ-SKILL-001",
            "requirement": "Python",
            "match_status": "MATCHED",
            "evidence_ref": "SKILLS-LIST",
            "evidence": "Python, SQL",
            "explanation": "Python was found."
        },
        {
            "requirement_id": "REQ-EXP-001",
            "requirement": "3+ years",
            "match_status": "NOT_FOUND",
            "evidence_ref": "EXPERIENCE-TEXT",
            "evidence": None,
            "explanation": "Not found."
        }
    ]

    report = build_fit_report(matches)
    for item in report:
        ref = item["evidence_ref"]
        # evidence_ref can be None if not found, but if it exists it must be in the profile field IDs
        if ref is not None:
            assert ref in profile_field_ids
