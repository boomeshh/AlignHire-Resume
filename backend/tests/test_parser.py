from backend.app.parser import parse_candidate, extract_email, extract_phone, extract_name

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

def test_email_with_trailing_punctuation():
    text = "My email is john.doe@example.com. Please write there."
    assert extract_email(text) == "john.doe@example.com"
    
    text_bracket = "Contact (john.doe@example.co.in) for details."
    assert extract_email(text_bracket) == "john.doe@example.co.in"

def test_indian_phone_formats():
    # Test format: 9876543210
    assert extract_phone("My number is 9876543210") == "9876543210"
    # Test format: +91 9876543210
    assert extract_phone("My number is +91 9876543210") == "+91 9876543210"
    # Test format: +91-9876543210
    assert extract_phone("My number is +91-9876543210") == "+91-9876543210"
    # Test format: +91 98765 43210
    assert extract_phone("My number is +91 98765 43210") == "+91 98765 43210"
    # Test format: 98765 43210
    assert extract_phone("My number is 98765 43210") == "98765 43210"

def test_phone_longer_digit_exclusion():
    # Ensure longer digit sequences do not match as a 10-digit number
    text = "Transaction ID 1239876543210 finished."
    assert extract_phone(text) is None
    
    text_other = "Product serial 98765432100000 is invalid."
    assert extract_phone(text_other) is None

def test_name_extraction_heuristics():
    # Starting with a job title
    text = """Software Engineer
John Doe
john.doe@example.com"""
    assert extract_name(text) == "John Doe"

    # Starting with cv header
    text_cv = """CURRICULUM VITAE
Jane Smith
jane@example.com"""
    assert extract_name(text_cv) == "Jane Smith"

    # Line with colon should be skipped (e.g. Phone: ...) unless starting with Name:
    text_colon = """Phone: +91 9876543210
Name: Bobby Brown
Email: bobby@example.com"""
    assert extract_name(text_colon) == "Bobby Brown"

    # Multiple spaces collapse
    text_spaces = """  Alice    Wonderland  
alice@example.com"""
    assert extract_name(text_spaces) == "Alice Wonderland"

    # No reasonable name exists (e.g. only contact and headings)
    text_no_name = """Software Developer
john.doe@example.com
+91 9876543210
SUMMARY
Experienced developer."""
    assert extract_name(text_no_name) is None
