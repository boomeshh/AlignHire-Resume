from backend.app.segmenter import segment_text

def test_segment_text_basic():
    input_text = """John Doe

SUMMARY
Python developer.

SKILLS
Python, SQL, AWS

EXPERIENCE
Software Engineer."""

    result = segment_text(input_text)

    assert "SUMMARY" in result
    assert "SKILLS" in result
    assert "EXPERIENCE" in result

    assert result["SUMMARY"] == "Python developer."
    assert result["SKILLS"] == "Python, SQL, AWS"
    assert result["EXPERIENCE"] == "Software Engineer."

def test_segment_text_case_insensitivity():
    input_text = """skills:
Python, SQL"""

    result = segment_text(input_text)

    assert "SKILLS" in result
    assert result["SKILLS"] == "Python, SQL"
