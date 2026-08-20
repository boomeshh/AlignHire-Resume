from backend.app.extractor import extract_text
from backend.app.segmenter import segment_text
from backend.app.parser import parse_candidate
from backend.app.models import AnalysisResult

def analyze_resume(resume_path: str, job_description: str) -> dict:
    """
    Main entry point for Phase 1 backend.
    Orchestrates: Validation -> Extraction -> Segmentation -> Parsing -> Dict Output
    """
    # 1. Input Validation
    if not resume_path:
        raise ValueError("Resume file path must be provided.")
    if job_description is None:
        raise ValueError("Job description must not be None.")

    # 2. Extract Text
    raw_text = extract_text(resume_path)

    # 3. Segment Text
    sections = segment_text(raw_text)

    # 4. Parse Candidate Info
    candidate = parse_candidate(raw_text)

    # 5. Build Result and Convert to Serializable Dict
    analysis_result = AnalysisResult(
        candidate=candidate,
        sections=sections,
        job_description=job_description
    )

    return analysis_result.to_dict()
