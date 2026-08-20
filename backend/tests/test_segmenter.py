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

def test_segment_text_spacing_normalization():
    input_text = """  TECHNICAL   SKILLS  
Python, SQL"""
    result = segment_text(input_text)
    assert "TECHNICAL SKILLS" in result
    assert result["TECHNICAL SKILLS"] == "Python, SQL"

def test_segment_text_markdown_headings():
    input_text = """## SUMMARY
Python developer."""
    result = segment_text(input_text)
    assert "SUMMARY" in result
    assert result["SUMMARY"] == "Python developer."

def test_segment_text_bullet_headings():
    input_text = """• SKILLS
Python, SQL

▪ EXPERIENCE
Software Engineer.

- EDUCATION
B.Tech in CS."""
    result = segment_text(input_text)
    assert "SKILLS" in result
    assert "EXPERIENCE" in result
    assert "EDUCATION" in result
    assert result["SKILLS"] == "Python, SQL"
    assert result["EXPERIENCE"] == "Software Engineer."
    assert result["EDUCATION"] == "B.Tech in CS."

def test_segment_text_numbered_headings():
    input_text = """1. EDUCATION
B.Tech

A. EXPERIENCE
Software Engineer."""
    result = segment_text(input_text)
    assert "EDUCATION" in result
    assert "EXPERIENCE" in result
    assert result["EDUCATION"] == "B.Tech"
    assert result["EXPERIENCE"] == "Software Engineer."

def test_segment_text_ignore_normal_sentences():
    # Sentences containing key words should not be treated as headings
    input_text = """John Doe

SUMMARY
I have experience working with Python and SQL. My education is in computer science.

SKILLS
Python, SQL"""
    result = segment_text(input_text)
    
    # "experience" or "education" in the summary sentence must not create extra section keys
    assert "SUMMARY" in result
    assert "SKILLS" in result
    assert "EXPERIENCE" not in result
    assert "EDUCATION" not in result
    assert "experience working with Python" in result["SUMMARY"]
