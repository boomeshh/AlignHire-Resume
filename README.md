# AlignHire (Phase 1)

## Tagline
**Deterministic Resume Intelligence and Parsing Backend**

## Overview
AlignHire is a lightweight, deterministic backend processing engine designed to parse candidate resumes (PDF, DOCX, TXT) and segment them into standardized sections. It extracts essential contact details (Name, Email, Phone) and maps them alongside the original job description.

## Architecture
```
[Resume File] 
      ↓
[Extractor] ──> Raw text string
      ↓
[Segmenter] ──> Structured dictionary of sections (SUMMARY, SKILLS, EXPERIENCE, etc.)
      ↓
[Parser]    ──> Extracted candidate details (Name, Email, Phone)
      ↓
[Pipeline]  ──> Clean, serializable dict output
```

- **Extractor (`extractor.py`)**: Safely parses text from PDF, DOCX, and UTF-8 TXT files.
- **Segmenter (`segmenter.py`)**: Uses deterministic rules to split resume text into standardized section headings.
- **Parser (`parser.py`)**: Uses regex and word-pattern heuristics to extract candidate name, email, and Indian phone formats.
- **Pipeline (`pipeline.py`)**: Orchestrates the modules into the stable main API `analyze_resume()`.

---

## Stable API Contract

Future applications or UIs (e.g. Streamlit or FastAPI) can invoke the processing logic via:

```python
from backend.app.pipeline import analyze_resume

result = analyze_resume(
    resume_path="data/uploads/sample_resume.pdf",
    job_description="Python developer with SQL experience"
)
```

### Output Schema:
```json
{
  "candidate": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+91 9876543210"
  },
  "sections": {
    "SUMMARY": "Python developer...",
    "SKILLS": "Python, SQL, AWS...",
    "EXPERIENCE": "Software Engineer at..."
  },
  "job_description": "Python developer with SQL experience"
}
```

---

## Development & Testing

### Running Tests
To run unit and integration tests:
```bash
pytest -q
```

### CLI Test Runner
Run a direct CLI test:
```bash
python backend/main.py <resume_path> "<job_description>"
```
