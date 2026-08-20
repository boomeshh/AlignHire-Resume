import pytest
from pathlib import Path
from backend.app.extractor import extract_text

def test_extract_txt(tmp_path):
    # Create temporary text file
    txt_file = tmp_path / "resume.txt"
    content = "John Doe\njohn@example.com"
    txt_file.write_text(content, encoding="utf-8")

    result = extract_text(str(txt_file))

    assert isinstance(result, str)
    assert "John Doe" in result
    assert "john@example.com" in result

def test_unsupported_file():
    with pytest.raises(ValueError):
        extract_text("resume.xyz")

def test_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_text("missing.pdf")
