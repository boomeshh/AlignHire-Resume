from backend.app.parser import parse_candidate

def test_parse_candidate_full():
    input_text = """John Doe
john.doe@example.com
+91 9876543210"""

    result = parse_candidate(input_text)

    assert result["name"] == "John Doe"
    assert result["email"] == "john.doe@example.com"
    assert result["phone"] == "+91 9876543210"

def test_parse_candidate_missing_email():
    input_text = """John Doe
+91 9876543210"""

    result = parse_candidate(input_text)

    assert result["name"] == "John Doe"
    assert result["email"] is None
    assert result["phone"] == "+91 9876543210"

def test_parse_candidate_missing_phone():
    input_text = """John Doe
john.doe@example.com"""

    result = parse_candidate(input_text)

    assert result["name"] == "John Doe"
    assert result["email"] == "john.doe@example.com"
    assert result["phone"] is None

def test_parse_candidate_empty():
    result = parse_candidate("")
    assert result["name"] is None
    assert result["email"] is None
    assert result["phone"] is None
