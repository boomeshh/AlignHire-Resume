from backend.app.profile_builder import build_profile

def test_build_profile_full():
    candidate = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+91 9876543210"
    }
    sections = {
        "SKILLS": "Python, SQL, AWS, Python, Docker",
        "EXPERIENCE": "4 years experience as software developer.",
        "EDUCATION": "B.Tech Computer Science"
    }

    result = build_profile(candidate, sections)

    assert "fields" in result
    fields = result["fields"]
    assert len(fields) == 6

    # Verify unique field_ids and field schemas
    seen_ids = set()
    for field in fields:
        assert "field_id" in field
        assert "category" in field
        assert "status" in field
        assert "value" in field
        assert "evidence" in field
        assert "source_section" in field
        
        field_id = field["field_id"]
        assert field_id not in seen_ids
        seen_ids.add(field_id)

    # Verify skill extraction, deduplication, and deterministic ordering
    skills_field = next(f for f in fields if f["field_id"] == "SKILLS-LIST")
    assert skills_field["status"] == "FOUND"
    assert skills_field["value"] == ["Python", "SQL", "AWS", "Docker"]  # Python is not duplicated, Docker is last
    assert skills_field["source_section"] == "SKILLS"
    assert "Python, SQL, AWS" in skills_field["evidence"]

    # Verify other fields
    name_field = next(f for f in fields if f["field_id"] == "CANDIDATE-NAME")
    assert name_field["value"] == "John Doe"
    assert name_field["status"] == "FOUND"

    exp_field = next(f for f in fields if f["field_id"] == "EXPERIENCE-TEXT")
    assert exp_field["value"] == sections["EXPERIENCE"]
    assert exp_field["status"] == "FOUND"

    edu_field = next(f for f in fields if f["field_id"] == "EDUCATION-TEXT")
    assert edu_field["value"] == sections["EDUCATION"]
    assert edu_field["status"] == "FOUND"

def test_build_profile_missing_sections():
    candidate = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": None
    }
    # No EXPERIENCE or EDUCATION sections
    sections = {
        "SKILLS": "Python"
    }

    result = build_profile(candidate, sections)
    fields = result["fields"]

    phone_field = next(f for f in fields if f["field_id"] == "CANDIDATE-PHONE")
    assert phone_field["status"] == "NOT_FOUND"
    assert phone_field["value"] is None
    assert phone_field["evidence"] is None

    exp_field = next(f for f in fields if f["field_id"] == "EXPERIENCE-TEXT")
    assert exp_field["status"] == "NOT_FOUND"
    assert exp_field["value"] is None
    assert exp_field["evidence"] is None

    edu_field = next(f for f in fields if f["field_id"] == "EDUCATION-TEXT")
    assert edu_field["status"] == "NOT_FOUND"
    assert edu_field["value"] is None
    assert edu_field["evidence"] is None

def test_build_profile_field_id_uniqueness():
    """All profile field IDs must be unique."""
    candidate = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890"
    }
    sections = {
        "SKILLS": "Python, SQL",
        "EXPERIENCE": "3 years",
        "EDUCATION": "BS CS"
    }
    
    result = build_profile(candidate, sections)
    fields = result["fields"]
    field_ids = [f["field_id"] for f in fields]
    
    # Assert uniqueness
    assert len(field_ids) == len(set(field_ids)), "Duplicate field IDs detected"
    
    # Verify expected IDs
    expected_ids = {
        "CANDIDATE-NAME",
        "CANDIDATE-EMAIL",
        "CANDIDATE-PHONE",
        "SKILLS-LIST",
        "EXPERIENCE-TEXT",
        "EDUCATION-TEXT"
    }
    assert set(field_ids) == expected_ids

def test_build_profile_no_skills():
    """When candidate has no SKILLS field, SKILLS-LIST should be NOT_FOUND."""
    candidate = {"name": "Jane", "email": "jane@example.com", "phone": None}
    sections = {"EXPERIENCE": "2 years"}
    
    result = build_profile(candidate, sections)
    skills_field = next(f for f in result["fields"] if f["field_id"] == "SKILLS-LIST")
    
    assert skills_field["status"] == "NOT_FOUND"
    assert skills_field["value"] is None
    assert skills_field["evidence"] is None
