"""
ProofResume Pipeline Orchestrator (Phase 1)

Main entry point for ProofResume.
Pipeline Flow: Extractor -> Segmenter -> Parser -> profile.json
"""

import os
import json
from dotenv import load_dotenv

# TODO: Import functions from app module after they are implemented
# from app.extractor import extract_text
# from app.segmenter import segment_text
# from app.parser import parse_profile

def run_pipeline(resume_path: str, jd_path: str, output_path: str):
    """
    Orchestrates the entire ProofResume Phase 1 extraction pipeline.
    
    TODO:
    1. Extract raw text from the resume file.
    2. Segment raw text into defined sections.
    3. Parse candidate fields (Name, Email, Phone, Skills, Education) from the sections.
    4. Validate structure and write the output CandidateProfile as JSON to output_path.
    """
    load_dotenv()
    
    print(f"Starting ProofResume extraction pipeline for: {resume_path}")
    
    # TODO: Implement step-by-step pipeline execution
    # raw_text = extract_text(resume_path)
    # sections = segment_text(raw_text)
    # profile = parse_profile(sections)
    # 
    # Write profile.to_dict() to output_path
    pass

if __name__ == "__main__":
    # Example local run
    resume_file = os.path.join("input", "resume.pdf")
    jd_file = os.path.join("input", "jd.txt")
    output_file = os.path.join("output", "profile.json")
    
    run_pipeline(resume_file, jd_file, output_file)
