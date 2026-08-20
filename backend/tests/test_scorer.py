from backend.app.scorer import calculate_fit_score

def test_calculate_fit_score_all_matched():
    matches = [
        {"importance": "REQUIRED", "match_status": "MATCHED"},
        {"importance": "REQUIRED", "match_status": "MATCHED"},
        {"importance": "REQUIRED", "match_status": "MATCHED"},
        {"importance": "PREFERRED", "match_status": "MATCHED"},
        {"importance": "PREFERRED", "match_status": "MATCHED"}
    ]
    result = calculate_fit_score(matches)
    assert result["score"] == 100
    assert result["breakdown"]["required"]["matched"] == 3
    assert result["breakdown"]["preferred"]["matched"] == 2

def test_calculate_fit_score_all_unmatched():
    matches = [
        {"importance": "REQUIRED", "match_status": "NOT_MATCHED"},
        {"importance": "REQUIRED", "match_status": "NOT_FOUND"},
        {"importance": "PREFERRED", "match_status": "NOT_MATCHED"}
    ]
    result = calculate_fit_score(matches)
    assert result["score"] == 0

def test_calculate_fit_score_partial():
    # Required: 1 matched, 1 partial. Preferred: none.
    # Score = (1.0 + 0.5) / 2 = 0.75 -> 75%
    matches = [
        {"importance": "REQUIRED", "match_status": "MATCHED"},
        {"importance": "REQUIRED", "match_status": "PARTIAL"}
    ]
    result = calculate_fit_score(matches)
    assert result["score"] == 75
    assert result["breakdown"]["required"]["partial"] == 1

def test_calculate_fit_score_weighted():
    # Required: 3 matched, 1 unmatched -> 75% completion -> 0.75 * 80 = 60 points
    # Preferred: 1 matched -> 100% completion -> 1.0 * 20 = 20 points
    # Total = 80 points
    matches = [
        {"importance": "REQUIRED", "match_status": "MATCHED"},
        {"importance": "REQUIRED", "match_status": "MATCHED"},
        {"importance": "REQUIRED", "match_status": "MATCHED"},
        {"importance": "REQUIRED", "match_status": "NOT_MATCHED"},
        {"importance": "PREFERRED", "match_status": "MATCHED"}
    ]
    result = calculate_fit_score(matches)
    assert result["score"] == 80

def test_calculate_fit_score_only_required():
    matches = [
        {"importance": "REQUIRED", "match_status": "MATCHED"},
        {"importance": "REQUIRED", "match_status": "NOT_MATCHED"}
    ]
    # Represent 100% of score (1/2 = 50%)
    result = calculate_fit_score(matches)
    assert result["score"] == 50

def test_calculate_fit_score_only_preferred():
    matches = [
        {"importance": "PREFERRED", "match_status": "MATCHED"},
        {"importance": "PREFERRED", "match_status": "NOT_MATCHED"}
    ]
    # Represent 100% of score (1/2 = 50%)
    result = calculate_fit_score(matches)
    assert result["score"] == 50

def test_calculate_fit_score_empty():
    result = calculate_fit_score([])
    assert result["score"] == 0
    assert result["breakdown"]["required"]["matched"] == 0
    assert result["breakdown"]["preferred"]["matched"] == 0
