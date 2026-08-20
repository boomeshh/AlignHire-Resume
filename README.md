# AlignHire

### Deterministic Resume Intelligence and Parsing Backend

AlignHire is a lightweight, deterministic resume-processing engine designed to transform unstructured candidate resumes into clean, structured data.

**Phase 1** focuses on reliable document extraction, standardized resume section segmentation, and essential candidate information parsing from **PDF, DOCX, and TXT** files.

The backend is designed with a stable processing interface so future applications such as **Streamlit** or **FastAPI** can consume the same core pipeline without changing its internal parsing logic.

---

## ✨ Phase 1 Capabilities

* 📄 Extract text from PDF, DOCX, and UTF-8 TXT resumes
* 🧩 Segment resumes into standardized sections
* 👤 Extract candidate name
* 📧 Extract candidate email
* 📱 Extract Indian phone numbers
* 🔄 Preserve the supplied job description in the analysis result
* 🧱 Provide a clean, modular processing pipeline
* 🧪 Include unit and integration tests
* 🔌 Expose a stable `analyze_resume()` backend interface
* ⚡ Produce deterministic and JSON-serializable output

---

## 🏗️ Architecture

```text
                         AlignHire Phase 1

                     ┌───────────────────┐
                     │    Resume File    │
                     │  PDF / DOCX / TXT │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │     Extractor     │
                     │                   │
                     │   Raw Text        │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │     Segmenter     │
                     │                   │
                     │ Standard Sections │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │      Parser       │
                     │                   │
                     │ Name / Email /    │
                     │ Phone             │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │     Pipeline      │
                     │                   │
                     │ Structured Result │
                     └───────────────────┘
```

---

## 📁 Project Structure

```text
alignhire/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── extractor.py
│   │   ├── segmenter.py
│   │   ├── parser.py
│   │   └── pipeline.py
│   │
│   ├── tests/
│   │   ├── test_extractor.py
│   │   ├── test_segmenter.py
│   │   ├── test_parser.py
│   │   └── test_pipeline.py
│   │
│   ├── main.py
│   └── requirements.txt
│
├── data/
│   ├── uploads/
│   └── outputs/
│
├── frontend/
│   └── .gitkeep
│
├── .gitignore
└── README.md
```

---

## 🔧 Core Components

### Extractor

`backend/app/extractor.py`

Responsible for converting supported resume formats into raw text.

Supported formats:

```text
PDF
DOCX
TXT
```

The extractor uses deterministic document-specific processing and raises explicit errors for unsupported or missing files.

---

### Segmenter

`backend/app/segmenter.py`

Converts raw resume text into standardized sections such as:

```text
SUMMARY
OBJECTIVE
SKILLS
TECHNICAL SKILLS
EXPERIENCE
WORK EXPERIENCE
EMPLOYMENT
EDUCATION
PROJECTS
CERTIFICATIONS
```

The segmentation logic is deterministic and designed to tolerate common heading variations.

---

### Parser

`backend/app/parser.py`

Extracts essential candidate information:

```text
Name
Email
Phone
```

The parser uses deterministic regular expressions and conservative heuristics rather than an external AI model.

When information cannot be confidently identified, the parser returns `None` instead of inventing data.

---

### Pipeline

`backend/app/pipeline.py`

The pipeline orchestrates the complete Phase 1 workflow:

```text
Resume
  ↓
Extractor
  ↓
Segmenter
  ↓
Parser
  ↓
Structured Result
```

The stable public interface is:

```python
from backend.app.pipeline import analyze_resume

result = analyze_resume(
    resume_path="data/uploads/sample_resume.pdf",
    job_description="Python developer with SQL experience"
)
```

---

## 📦 Output Contract

The pipeline returns a JSON-serializable dictionary.

Example:

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

This output contract is intentionally independent of the UI layer.

Future applications can consume the same backend result through Streamlit, FastAPI, CLI tooling, or other interfaces.

---

## 🧪 Testing

AlignHire uses `pytest` for unit and integration testing.

Run the complete test suite:

```bash
pytest -q
```

The Phase 1 test suite verifies:

* TXT extraction
* Unsupported file handling
* Missing file handling
* Resume section detection
* Case-insensitive section headings
* Candidate name extraction
* Email extraction
* Indian phone number extraction
* Missing-field behavior
* End-to-end pipeline execution
* JSON serialization compatibility

---

## 💻 CLI Usage

The backend can also be executed directly from the command line.

```bash
python backend/main.py <resume_path> "<job_description>"
```

Example:

```bash
python backend/main.py \
  data/uploads/sample_resume.pdf \
  "Python developer with SQL experience"
```

The CLI prints the resulting structured analysis as formatted JSON.

---

## ⚙️ Installation

Clone the repository and install the Phase 1 dependencies:

```bash
pip install -r backend/requirements.txt
```

Run the test suite:

```bash
pytest -q
```

Run the CLI:

```bash
python backend/main.py <resume_path> "<job_description>"
```

---

## 🎯 Design Principles

### Deterministic

The same input should produce the same output.

### Modular

Extraction, segmentation, parsing, and orchestration are isolated into independent components.

### Testable

Core processing logic can be tested without requiring a frontend, database, or external service.

### Integration-Ready

The `analyze_resume()` interface provides a stable boundary for future UI and API integrations.

### Conservative Extraction

When information cannot be reliably identified, the system avoids fabricating values.

### Lightweight

Phase 1 intentionally avoids unnecessary infrastructure and external services.

---

## 🚧 Project Roadmap

### Phase 1 — Resume Intelligence Foundation

* [x] PDF extraction
* [x] DOCX extraction
* [x] TXT extraction
* [x] Resume section segmentation
* [x] Candidate contact extraction
* [x] Deterministic processing pipeline
* [x] CLI execution
* [x] Automated tests

### Phase 2 — Requirement Matching

Planned:

* Job description requirement extraction
* Evidence-backed field mapping
* Requirement-to-resume matching
* Deterministic fit scoring
* Structured evidence reporting
* Persistent result storage

### Phase 3 — Application Integration

Planned:

* Streamlit interface
* Backend/frontend integration
* Candidate analysis interface
* Result visualization
* End-to-end local demo

---

## 🔐 Current Scope

AlignHire Phase 1 is intentionally local and lightweight.

It currently does **not** include:

* Cloud deployment
* Authentication
* External databases
* LLM-based parsing
* Candidate ranking
* Fit scoring
* Job matching
* Production hosting

These capabilities are reserved for subsequent development phases.

---

## 📌 Project Status

**Phase 1 — Backend Foundation**

The current implementation establishes the deterministic document-processing core and its stable integration contract for subsequent phases.

---
