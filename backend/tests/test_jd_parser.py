from backend.app.jd_parser import parse_job_description

def test_parse_job_description_basic():
    jd = """
    Required:
    Python, SQL, AWS
    
    Preferred:
    Docker, Kubernetes
    
    3+ years of experience required.
    """
    result = parse_job_description(jd)

    assert len(result) == 6

    # Verify ID structure and categories
    for r in result:
        assert "requirement_id" in r
        assert "category" in r
        assert "requirement" in r
        assert "normalized_value" in r
        assert "importance" in r

    # Verify required skills
    req_skills = [r for r in result if r["category"] == "SKILL" and r["importance"] == "REQUIRED"]
    assert len(req_skills) == 3
    assert {s["requirement"] for s in req_skills} == {"Python", "SQL", "AWS"}
    assert {s["normalized_value"] for s in req_skills} == {"python", "sql", "aws"}

    # Verify preferred skills
    pref_skills = [r for r in result if r["category"] == "SKILL" and r["importance"] == "PREFERRED"]
    assert len(pref_skills) == 2
    assert {s["requirement"] for s in pref_skills} == {"Docker", "Kubernetes"}

    # Verify experience
    exp_req = next(r for r in result if r["category"] == "EXPERIENCE")
    assert exp_req["importance"] == "REQUIRED"
    assert exp_req["normalized_value"] == "3"
    assert "3+" in exp_req["requirement"]

def test_parse_job_description_defaults_and_indicators():
    # Defaults to REQUIRED when no section/line indicator matches
    jd_default = "Python developer with SQL experience."
    res_default = parse_job_description(jd_default)
    assert len(res_default) == 2
    for r in res_default:
        assert r["importance"] == "REQUIRED"

    # Preferred and required phrase triggers
    jd_phrases = """
    We must have PyTorch.
    FastAPI is mandatory.
    Django is nice to have.
    Flask is a plus.
    Git experience is preferred.
    AWS is a bonus.
    """
    res_phrases = parse_job_description(jd_phrases)

    skills_importance = {r["requirement"]: r["importance"] for r in res_phrases if r["category"] == "SKILL"}
    assert skills_importance["PyTorch"] == "REQUIRED"
    assert skills_importance["FastAPI"] == "REQUIRED"
    assert skills_importance["Django"] == "PREFERRED"
    assert skills_importance["Flask"] == "PREFERRED"
    assert skills_importance["Git"] == "PREFERRED"
    assert skills_importance["AWS"] == "PREFERRED"

def test_parse_job_description_determinism():
    jd = "Python, SQL, AWS, Docker required. 5 years experience preferred."
    result1 = parse_job_description(jd)
    result2 = parse_job_description(jd)
    assert result1 == result2

def test_parse_job_description_empty_jd():
    """Empty JD should return empty requirements list."""
    result = parse_job_description("")
    assert result == []
    
def test_parse_job_description_whitespace_jd():
    """Whitespace-only JD should return empty requirements list."""
    result = parse_job_description("     \n  \t  ")
    assert result == []

def test_parse_job_description_duplicate_skills():
    """
    Duplicate skill requirements should be deduplicated.
    Only first occurrence is preserved.
    """
    jd = "Python required. Python experience required. SQL required."
    result = parse_job_description(jd)
    
    python_reqs = [r for r in result if r["normalized_value"] == "python"]
    assert len(python_reqs) == 1, "Duplicate Python skills should be deduplicated"
    
    sql_reqs = [r for r in result if r["normalized_value"] == "sql"]
    assert len(sql_reqs) == 1
    
    # Total should be 2 unique skills
    skills = [r for r in result if r["category"] == "SKILL"]
    assert len(skills) == 2

def test_parse_job_description_requirement_id_stability():
    """
    Requirement IDs must be deterministic.
    Same JD always produces identical IDs.
    """
    jd = "Python required. SQL required. 3 years experience required."
    
    result1 = parse_job_description(jd)
    result2 = parse_job_description(jd)
    
    # Extract requirement IDs
    ids1 = [r["requirement_id"] for r in result1]
    ids2 = [r["requirement_id"] for r in result2]
    
    assert ids1 == ids2
    
    # IDs should follow pattern REQ-CATEGORY-###
    for r in result1:
        req_id = r["requirement_id"]
        assert req_id.startswith("REQ-")
        if r["category"] == "SKILL":
            assert req_id.startswith("REQ-SKILL-")
        elif r["category"] == "EXPERIENCE":
            assert req_id.startswith("REQ-EXP-")
