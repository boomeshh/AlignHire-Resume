import json
import pytest
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
