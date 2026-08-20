#!/usr/bin/env python3
"""
Direct verification script - bypasses pytest interactive prompt
"""
import json
import sys
import os
from pathlib import Path

# Fix Unicode encoding on Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding='utf-8')
from fastapi.testclient import TestClient
from backend.app.api import app

client = TestClient(app)

def test_health_check():
    """Test GET /api/health"""
    response = client.get("/api/health")
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    data = response.json()
    assert data["status"] == "operational"
    print("[PASS] Health check works")

def test_frontend():
    """Test GET /"""
    response = client.get("/")
    assert response.status_code == 200, f"Frontend failed: {response.status_code}"
    assert "text/html" in response.headers["content-type"]
    print("[PASS] Frontend served at GET /")

def test_txt_upload():
    """Test TXT upload and temp file cleanup"""
    sample_path = Path("data/uploads/sample_resume.txt")
    if not sample_path.exists():
        print("[SKIP] Sample resume not found, skipping TXT upload test")
        return
    
    upload_dir = Path("data/uploads")
    before = set(upload_dir.iterdir())
    
    with open(sample_path, "rb") as f:
        response = client.post(
            "/api/analyze",
            data={"job_description": "Python, SQL, AWS required. 3+ years experience."},
            files={"resume": ("sample_resume.txt", f, "text/plain")}
        )
    
    assert response.status_code == 200, f"Upload failed: {response.status_code}"
    data = response.json()
    
    # Verify Phase 1+2 structure
    assert "candidate" in data
    assert "sections" in data
    assert "job_description" in data
    assert "profile" in data
    assert "requirements" in data
    assert "fit_score" in data
    assert "fit_report" in data
    
    # Verify candidate
    assert "name" in data["candidate"]
    assert "email" in data["candidate"]
    assert "phone" in data["candidate"]
    
    # Verify fit score
    assert 0 <= data["fit_score"]["score"] <= 100
    
    # Verify temp file cleanup
    after = set(upload_dir.iterdir())
    new_files = after - before
    assert len(new_files) == 0, f"Temp files not cleaned up: {new_files}"
    
    print("[PASS] TXT upload works and temp files cleaned up")
    return data

def test_empty_jd():
    """Test empty job description"""
    sample_path = Path("data/uploads/sample_resume.txt")
    if not sample_path.exists():
        print("[SKIP] Sample resume not found, skipping empty JD test")
        return
    
    with open(sample_path, "rb") as f:
        response = client.post(
            "/api/analyze",
            data={"job_description": ""},
            files={"resume": ("sample_resume.txt", f, "text/plain")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["requirements"] == []
    assert data["fit_score"]["score"] == 0
    print("[PASS] Empty JD handled correctly")

def test_invalid_file():
    """Test invalid file format"""
    response = client.post(
        "/api/analyze",
        data={"job_description": "Python required"},
        files={"resume": ("resume.exe", b"fake", "application/octet-stream")}
    )
    
    assert response.status_code == 400
    print("[PASS] Invalid file format rejected")

def test_determinism():
    """Test deterministic output"""
    sample_path = Path("data/uploads/sample_resume.txt")
    if not sample_path.exists():
        print("[SKIP] Sample resume not found, skipping determinism test")
        return
    
    jd = "Python, SQL, AWS required"
    
    responses = []
    for _ in range(2):
        with open(sample_path, "rb") as f:
            response = client.post(
                "/api/analyze",
                data={"job_description": jd},
                files={"resume": ("sample_resume.txt", f, "text/plain")}
            )
        responses.append(json.dumps(response.json(), sort_keys=True))
    
    assert responses[0] == responses[1], "Output not deterministic"
    print("[PASS] Deterministic output verified")

def test_json_serializable():
    """Test response is JSON serializable"""
    sample_path = Path("data/uploads/sample_resume.txt")
    if not sample_path.exists():
        print("[SKIP] Sample resume not found, skipping JSON test")
        return
    
    with open(sample_path, "rb") as f:
        response = client.post(
            "/api/analyze",
            data={"job_description": "Python"},
            files={"resume": ("sample_resume.txt", f, "text/plain")}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should be able to convert back to JSON
    json_str = json.dumps(data)
    parsed_back = json.loads(json_str)
    assert parsed_back == data
    print("[PASS] Response is JSON serializable")

def main():
    print("=" * 60)
    print("FINAL VERIFICATION - ALIGNHIRE RESUME ANALYZER")
    print("=" * 60)
    
    try:
        test_health_check()
        test_frontend()
        test_invalid_file()
        analysis_data = test_txt_upload()
        test_empty_jd()
        test_json_serializable()
        test_determinism()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL VERIFICATION TESTS PASSED")
        print("=" * 60)
        
        if analysis_data:
            print("\nResponse Structure Verified:")
            print(f"  - Candidate: {list(analysis_data['candidate'].keys())}")
            print(f"  - Profile fields: {len(analysis_data['profile']['fields'])}")
            print(f"  - Requirements: {len(analysis_data['requirements'])}")
            print(f"  - Fit report: {len(analysis_data['fit_report'])}")
            print(f"  - Fit score: {analysis_data['fit_score']['score']}")
        
        return 0
    
    except AssertionError as e:
        print(f"\n[FAILED] VERIFICATION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

