from pathlib import Path
from backend.app.extractor import extract_text
from backend.app.segmenter import segment_text
from backend.app.parser import parse_candidate
from backend.app.profile_builder import build_profile
from backend.app.jd_parser import parse_job_description
from backend.app.matcher import match_requirements
from backend.app.scorer import calculate_fit_score
from backend.app.reporter import build_fit_report
from backend.app.models import AnalysisResult

def analyze_resume(resume_path: str, job_description: str) -> dict:
    """
    Main entry point for Phase 1 and Phase 2 backend.
    Orchestrates:
    Validation -> Extraction -> Segmentation -> Parsing ->
    Profile Building -> JD Requirement Extraction -> Matching -> Scoring -> Reporting -> Dict Output
    """
    # 1. Input Validation
    # 1. resume_path must accept string or pathlib.Path.
    # 2. Invalid resume_path types must raise TypeError.
    if not isinstance(resume_path, (str, Path)):
        raise TypeError("resume_path must be a string or pathlib.Path.")

    # 3. Empty or whitespace-only resume_path must raise ValueError.
    resume_path_str = str(resume_path).strip()
    if not resume_path_str:
        raise ValueError("resume_path must not be empty or whitespace-only.")

    # 4. job_description must be a string.
    # 5. Invalid job_description type must raise TypeError.
    if not isinstance(job_description, str):
        raise TypeError("job_description must be a string.")

    # 6. Empty job_description is allowed in Phase 1 and 2.

    # 2. Extract Text
    raw_text = extract_text(resume_path_str)

    # 3. Segment Text
    sections = segment_text(raw_text)

    # 4. Parse Candidate Info
    candidate = parse_candidate(raw_text)

    # 5. Build Structured Profile
    profile = build_profile(candidate, sections)

    # 6. Parse JD Requirements
    requirements = parse_job_description(job_description)

    # 7. Match Profile Against Requirements
    matches = match_requirements(profile, requirements)

    # 8. Calculate Fit Score
    fit_score = calculate_fit_score(matches)

    # 9. Build Fit Report
    fit_report = build_fit_report(matches)

    # 10. Build Result and Convert to Serializable Dict
    analysis_result = AnalysisResult(
        candidate=candidate,
        sections=sections,
        job_description=job_description,
        profile=profile,
        requirements=requirements,
        fit_score=fit_score,
        fit_report=fit_report
    )

    result = analysis_result.to_dict()

    # Validate JSON-compatible output
    import json
    try:
        json.dumps(result)
    except Exception as e:
        raise TypeError(f"Pipeline output is not JSON serializable: {e}")

    return result
