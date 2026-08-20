import json
import pytest
from pathlib import Path
from backend.app.pipeline import analyze_resume

def test_pipeline_execution(tmp_path):
    # Create temporary text resume
    resume_file = tmp_path / "resume.txt"
    content = """John Doe
john.doe@example.com
+91 9876543210

SUMMARY
Python developer.

SKILLS
Python, SQL, AWS

EXPERIENCE
Software Engineer."""
    resume_file.write_text(content, encoding="utf-8")

    jd = "Python developer with SQL experience"
    result = analyze_resume(str(resume_file), jd)

    # Verify return types and keys
    assert isinstance(result, dict)
    assert "candidate" in result
    assert "sections" in result
    assert "job_description" in result
    assert result["job_description"] == jd

    # Verify parsed candidate information
    assert result["candidate"]["name"] == "John Doe"
    assert result["candidate"]["email"] == "john.doe@example.com"
    assert result["candidate"]["phone"] == "+91 9876543210"

    # Verify segmented sections
    assert "SKILLS" in result["sections"]
    assert result["sections"]["SKILLS"] == "Python, SQL, AWS"
    assert "EXPERIENCE" in result["sections"]
    assert result["sections"]["EXPERIENCE"] == "Software Engineer."

    # Verify JSON compatibility
    serialized = json.dumps(result)
    assert isinstance(serialized, str)

def test_pipeline_input_validation(tmp_path):
    # Setup a valid resume file
    resume_file = tmp_path / "resume.txt"
    resume_file.write_text("John Doe\njohn@example.com\n9876543210", encoding="utf-8")
    
    # 1. Invalid resume_path type (e.g., int, dict)
    with pytest.raises(TypeError):
        analyze_resume(123, "job description")
        
    # 2. Empty resume_path
    with pytest.raises(ValueError):
        analyze_resume("", "job description")
        
    # 3. Whitespace-only resume_path
    with pytest.raises(ValueError):
        analyze_resume("   ", "job description")
        
    # 4. Invalid job_description type
    with pytest.raises(TypeError):
        analyze_resume(str(resume_file), 123)
        
    # 5. Empty job_description is allowed
    result = analyze_resume(str(resume_file), "")
    assert result["job_description"] == ""

    # 6. pathlib.Path works as resume_path
    result_path = analyze_resume(resume_file, "some jd")
    assert result_path["candidate"]["name"] == "John Doe"

def test_pipeline_determinism(tmp_path):
    # Setup resume file
    resume_file = tmp_path / "resume.txt"
    content = """John Doe
john@example.com
+91 9876543210

SUMMARY
Python developer.

SKILLS
Python, SQL, AWS"""
    resume_file.write_text(content, encoding="utf-8")
    
    jd = "Python developer"
    
    # Call twice with same input
    result1 = analyze_resume(str(resume_file), jd)
    result2 = analyze_resume(str(resume_file), jd)
    
    assert result1 == result2

def test_pipeline_phase2_execution(tmp_path):
    resume_file = tmp_path / "resume_p2.txt"
    content = """John Doe
john.doe@example.com
+91 9876543210

SKILLS
Python, SQL, AWS

EXPERIENCE
4 years of software development experience.

EDUCATION
B.Tech Computer Science"""
    resume_file.write_text(content, encoding="utf-8")

    jd = """
    Python and SQL required.
    AWS required.
    Docker preferred.
    3+ years of experience required.
    """

    result = analyze_resume(str(resume_file), jd)

    # 1. Verify compatibility keys exist
    assert "candidate" in result
    assert "sections" in result
    assert "job_description" in result
    assert result["candidate"]["name"] == "John Doe"
    assert result["candidate"]["email"] == "john.doe@example.com"
    assert result["candidate"]["phone"] == "+91 9876543210"

    # 2. Verify Phase 2 keys exist
    assert "profile" in result
    assert "fields" in result["profile"]
    assert "requirements" in result
    assert "fit_score" in result
    assert "fit_report" in result

    # 3. Verify match statuses
    matches = {m["requirement"]: m["match_status"] for m in result["fit_report"]}
    assert matches["Python"] == "MATCHED"
    assert matches["SQL"] == "MATCHED"
    assert matches["AWS"] == "MATCHED"
    assert matches["Docker"] == "NOT_MATCHED"
    assert matches["3+ years experience"] == "MATCHED"

    # 4. Verify fit score (Required: 4 matched / 4 = 100% -> 80 pts. Preferred: 0 matched / 1 = 0% -> 0 pts. Total = 80)
    assert result["fit_score"]["score"] == 80

    # 5. Verify all fit_report evidence_ref values correspond to actual profile field_ids
    profile_field_ids = {f["field_id"] for f in result["profile"]["fields"]}
    for report_item in result["fit_report"]:
        ref = report_item["evidence_ref"]
        if ref is not None:
            assert ref in profile_field_ids

    # 6. Verify JSON serializability
    serialized = json.dumps(result)
    assert isinstance(serialized, str)

def test_pipeline_experience_year_safety(tmp_path):
    resume_file = tmp_path / "resume_exp_safety.txt"
    content = """John Doe
john@example.com
+91 9876543210

EXPERIENCE
Worked at Company A from 2021 to 2024.
- Handled deployment."""
    resume_file.write_text(content, encoding="utf-8")

    # JD requires 3 years experience
    result = analyze_resume(str(resume_file), "3+ years of experience required.")
    
    # Verify no explicit experience duration detected -> NOT_FOUND (not MATCHED or interpreted as 2024)
    exp_report = next(r for r in result["fit_report"] if r["requirement_id"] == "REQ-EXP-001")
    assert exp_report["match_status"] == "NOT_FOUND"

def test_pipeline_duplicate_jd_skills(tmp_path):
    resume_file = tmp_path / "resume_dup.txt"
    resume_file.write_text("John Doe\nSKILLS\nPython", encoding="utf-8")

    jd = """
    Python required.
    Python experience required.
    SQL required.
    """
    result = analyze_resume(str(resume_file), jd)
    
    # Verify deduplication: Python is only added once as a requirement
    python_reqs = [r for r in result["requirements"] if r["normalized_value"] == "python"]
    assert len(python_reqs) == 1

def test_pipeline_empty_and_whitespace_jd(tmp_path):
    resume_file = tmp_path / "resume_empty_jd.txt"
    resume_file.write_text("John Doe\nSKILLS\nPython", encoding="utf-8")

    # Empty JD
    result_empty = analyze_resume(str(resume_file), "")
    assert result_empty["requirements"] == []
    assert result_empty["fit_score"]["score"] == 0
    assert result_empty["fit_report"] == []

    # Whitespace JD
    result_whitespace = analyze_resume(str(resume_file), "   \n   ")
    assert result_whitespace["requirements"] == []
    assert result_whitespace["fit_score"]["score"] == 0
    assert result_whitespace["fit_report"] == []

def test_pipeline_no_resume_skills(tmp_path):
    resume_file = tmp_path / "resume_no_skills.txt"
    # No SKILLS section and no vocabulary skills mentioned
    resume_file.write_text("John Doe\nSUMMARY\nWorking as a general employee.", encoding="utf-8")

    result = analyze_resume(str(resume_file), "Docker required.")
    
    # Expected match_status = NOT_FOUND (since no SKILLS-LIST field was populated or found in profile)
    match_item = result["fit_report"][0]
    assert match_item["match_status"] == "NOT_FOUND"

def test_pipeline_score_bounds(tmp_path):
    resume_file = tmp_path / "resume_score.txt"
    resume_file.write_text("John Doe\nSKILLS\nPython", encoding="utf-8")

    # 1. 0% matched -> Score 0
    res_0 = analyze_resume(str(resume_file), "Docker required. Kubernetes required.")
    assert res_0["fit_score"]["score"] == 0
    assert 0 <= res_0["fit_score"]["score"] <= 100

    # 2. 100% matched -> Score 100
    res_100 = analyze_resume(str(resume_file), "Python required.")
    assert res_100["fit_score"]["score"] == 100
    assert 0 <= res_100["fit_score"]["score"] <= 100
