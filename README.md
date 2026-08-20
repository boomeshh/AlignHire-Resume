# ProofResume

## Tagline
**Evidence-Grounded Resume Intelligence Agent**

## Problem Statement
Recruiters waste significant time vetting resume details because traditional ATS systems often parse candidate fields inaccurately or invent details (hallucination) without verifiable evidence from the source document.

## Phase 1 Objective
Build a deterministic, reliable text extraction and segmentation pipeline that parses key candidate fields (Full Name, Email, Phone, Skills, Education) and attaches exact evidence/source context to each extracted value without using complex or non-deterministic AI models.

## Architecture
```
Extractor → Segmenter → Parser → profile.json
```

- **Extractor**: Extracts raw string content from PDF/DOCX files.
- **Segmenter**: Breaks the raw string down into a dictionary of defined sections.
- **Parser**: Applies deterministic logic (regex, dict matching) to extract fields with source context and output status.
- **profile.json**: The finalized structured data containing parsed fields and evidence.
