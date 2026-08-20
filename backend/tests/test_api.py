"""
Test suite for the FastAPI adapter.
Tests the API endpoints and integration with the existing pipeline.
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.api import app

# Initialize test client
client = TestClient(app)


@pytest.fixture
def sample_resume_path():
    """Provide path to sample resume"""
    return Path(__file__).parent.parent.parent / "data" / "uploads" / "sample_resume.txt"


class TestFrontendServing:
    """Tests for frontend serving"""
    
    def test_get_frontend(self):
        """Test GET / returns the frontend HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "ALIGNHIRE" in response.text or "AlignHire" in response.text or "alignhire" in response.text.lower()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "operational"


class TestAnalyzeAPI:
    """Tests for the /api/analyze endpoint"""
    
    def test_analyze_with_txt_resume(self, sample_resume_path):
        """Test analyze endpoint with TXT resume"""
        if not sample_resume_path.exists():
            pytest.skip(f"Sample resume not found at {sample_resume_path}")
        
        with open(sample_resume_path, "rb") as f:
            response = client.post(
                "/api/analyze",
                data={"job_description": "Python, SQL required"},
                files={"resume": ("resume.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify Phase 1 keys
        assert "candidate" in data
        assert "sections" in data
        assert "job_description" in data
        assert data["job_description"] == "Python, SQL required"
        
        # Verify Phase 2 keys
        assert "profile" in data
        assert "requirements" in data
        assert "fit_score" in data
        assert "fit_report" in data
        
        # Verify profile structure
        assert "fields" in data["profile"]
        assert len(data["profile"]["fields"]) > 0
        
        # Verify fit_score structure
        assert "score" in data["fit_score"]
        assert 0 <= data["fit_score"]["score"] <= 100
        assert "breakdown" in data["fit_score"]
    
    def test_analyze_unsupported_file_format(self):
        """Test analyze endpoint with unsupported file format"""
        response = client.post(
            "/api/analyze",
            data={"job_description": "Python required"},
            files={"resume": ("resume.exe", b"fake content", "application/octet-stream")}
        )
        
        assert response.status_code == 400
        assert "Unsupported" in response.json()["detail"] or "format" in response.json()["detail"].lower()
    
    def test_analyze_missing_resume(self):
        """Test analyze endpoint with missing resume file"""
        response = client.post(
            "/api/analyze",
            data={"job_description": "Python required"}
            # No resume file provided
        )
        
        assert response.status_code != 200  # Should fail validation
    
    def test_analyze_empty_job_description(self, sample_resume_path):
        """Test analyze endpoint with empty job description"""
        if not sample_resume_path.exists():
            pytest.skip(f"Sample resume not found at {sample_resume_path}")
        
        with open(sample_resume_path, "rb") as f:
            response = client.post(
                "/api/analyze",
                data={"job_description": ""},
                files={"resume": ("resume.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Empty JD should result in empty requirements and zero score
        assert data["requirements"] == []
        assert data["fit_score"]["score"] == 0
        assert data["fit_report"] == []
    
    def test_analyze_with_jd_and_resume(self, sample_resume_path):
        """Test analyze endpoint with real JD and resume"""
        if not sample_resume_path.exists():
            pytest.skip(f"Sample resume not found at {sample_resume_path}")
        
        jd = "Python, SQL, AWS required. Docker preferred. 3+ years experience required."
        
        with open(sample_resume_path, "rb") as f:
            response = client.post(
                "/api/analyze",
                data={"job_description": jd},
                files={"resume": ("resume.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify candidate info parsed
        assert data["candidate"]["name"] is not None or "name" in data["candidate"]
        
        # Verify requirements extracted
        assert len(data["requirements"]) > 0
        
        # Verify fit report matches requirements
        assert len(data["fit_report"]) == len(data["requirements"])
        
        # Verify fit score is valid
        assert 0 <= data["fit_score"]["score"] <= 100
        
        # Verify each fit report item has required fields
        for item in data["fit_report"]:
            assert "requirement" in item
            assert "match_status" in item
            assert item["match_status"] in ["MATCHED", "PARTIAL", "NOT_MATCHED", "NOT_FOUND"]
            assert "explanation" in item


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_analyze_invalid_file_extension(self):
        """Test that invalid file extensions are rejected"""
        response = client.post(
            "/api/analyze",
            data={"job_description": "Python required"},
            files={"resume": ("resume.xyz", b"fake content", "application/octet-stream")}
        )
        
        assert response.status_code == 400
        assert "Unsupported" in response.json()["detail"] or "format" in response.json()["detail"]


class TestDataMapping:
    """Tests for correct data mapping from backend to API"""
    
    def test_fit_report_evidence_references(self, sample_resume_path):
        """Test that fit_report evidence_ref values are valid"""
        if not sample_resume_path.exists():
            pytest.skip(f"Sample resume not found at {sample_resume_path}")
        
        jd = "Python required"
        
        with open(sample_resume_path, "rb") as f:
            response = client.post(
                "/api/analyze",
                data={"job_description": jd},
                files={"resume": ("resume.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Get valid field IDs from profile
        valid_field_ids = {field["field_id"] for field in data["profile"]["fields"]}
        
        # Verify all evidence_ref in fit_report are valid
        for item in data["fit_report"]:
            if item["evidence_ref"] is not None:
                assert item["evidence_ref"] in valid_field_ids, \
                    f"Orphan evidence reference: {item['evidence_ref']} not in profile fields"
    
    def test_profile_field_structure(self, sample_resume_path):
        """Test that profile fields have correct structure"""
        if not sample_resume_path.exists():
            pytest.skip(f"Sample resume not found at {sample_resume_path}")
        
        with open(sample_resume_path, "rb") as f:
            response = client.post(
                "/api/analyze",
                data={"job_description": "Python required"},
                files={"resume": ("resume.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify each field has required keys
        for field in data["profile"]["fields"]:
            assert "field_id" in field
            assert "category" in field
            assert "status" in field
            assert field["status"] in ["FOUND", "NOT_FOUND"]
            assert "value" in field
            assert "evidence" in field
            assert "source_section" in field
