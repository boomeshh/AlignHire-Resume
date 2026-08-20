# Phase 2 Quick Reference Guide

## API Usage

```python
from backend.app.pipeline import analyze_resume

result = analyze_resume(
    resume_path="path/to/resume.txt",  # str or pathlib.Path
    job_description="Python, SQL required. 3+ years experience."
)

# Returns dict with:
# {
#   "candidate": {"name": str, "email": str, "phone": str},
#   "sections": {section_name: content, ...},
#   "job_description": str,
#   "profile": {
#     "fields": [
#       {
#         "field_id": str,
#         "category": str,
#         "status": "FOUND" | "NOT_FOUND",
#         "value": Any,
#         "evidence": str | None,
#         "source_section": str | None
#       },
#       ...
#     ]
#   },
#   "requirements": [
#     {
#       "requirement_id": "REQ-SKILL-001" | "REQ-EXP-001",
#       "category": "SKILL" | "EXPERIENCE",
#       "requirement": str,
#       "normalized_value": str,
#       "importance": "REQUIRED" | "PREFERRED"
#     },
#     ...
#   ],
#   "fit_score": {
#     "score": 0-100,
#     "breakdown": {
#       "required": {"matched": int, "partial": int, "not_matched": int, "not_found": int},
#       "preferred": {"matched": int, "partial": int, "not_matched": int, "not_found": int}
#     }
#   },
#   "fit_report": [
#     {
#       "requirement": str,
#       "requirement_id": str,
#       "match_status": "MATCHED" | "PARTIAL" | "NOT_MATCHED" | "NOT_FOUND",
#       "explanation": str,
#       "evidence_ref": str | None,
#       "evidence": str | None,
#       "confidence": "high" | "medium" | "low"
#     },
#     ...
#   ]
# }
```

## CLI Usage

```bash
uv run python backend/main.py <resume_file> "<job_description>"

# Example:
uv run python backend/main.py data/uploads/sample_resume.txt \
  "Python, SQL, AWS required. Docker preferred. 3+ years experience required."
```

## Key Concepts

### Profile Fields
The profile contains 6 standard fields:
1. **CANDIDATE-NAME** - Candidate name
2. **CANDIDATE-EMAIL** - Email address
3. **CANDIDATE-PHONE** - Phone number
4. **SKILLS-LIST** - Array of extracted skills
5. **EXPERIENCE-TEXT** - Experience section text
6. **EDUCATION-TEXT** - Education section text

### Requirement IDs
- Format: `REQ-{CATEGORY}-{NUMBER}`
- Examples: `REQ-SKILL-001`, `REQ-EXP-001`
- Categories: SKILL, EXPERIENCE
- Deterministic: same JD always produces identical IDs

### Match Status
| Status | Meaning |
|--------|---------|
| **MATCHED** | Requirement directly supported by profile |
| **PARTIAL** | Partial support (weighted 0.5 in scoring) |
| **NOT_MATCHED** | Evidence exists, requirement not met |
| **NOT_FOUND** | Relevant profile info missing |

### Fit Score
- Range: 0-100
- Calculation: 80% of required requirements + 20% of preferred requirements
- Each requirement weighted by match status (1.0 for MATCHED, 0.5 for PARTIAL, 0 otherwise)

## Examples

### Example 1: Full Match
```
Resume Skills: Python, SQL, Docker
JD: Python required, SQL required, Docker preferred
Result: 
  - Python: MATCHED
  - SQL: MATCHED  
  - Docker: MATCHED
  - fit_score: 100
```

### Example 2: Partial Match
```
Resume Skills: Python, SQL
JD: Python required, SQL required, AWS required
Result:
  - Python: MATCHED
  - SQL: MATCHED
  - AWS: NOT_MATCHED
  - fit_score: 67 (2 matched, 1 not_matched out of 3 required)
```

### Example 3: No Match
```
Resume Skills: Python, JavaScript
JD: Java required, C++ required
Result:
  - Java: NOT_MATCHED
  - C++: NOT_MATCHED
  - fit_score: 0
```

### Example 4: Missing Skills Section
```
Resume: No SKILLS section
JD: Python required
Result:
  - Python: NOT_FOUND (no SKILLS-LIST field)
  - fit_score: 0
```

### Example 5: Experience Safety
```
Resume: "Worked from 2021 to 2024"
JD: 3+ years experience required
Result:
  - 3+ years: NOT_FOUND (no explicit duration like "3 years")
  - fit_score: 0
  
Resume: "4 years of experience"
JD: 3+ years experience required
Result:
  - 3+ years: MATCHED
  - fit_score: 100
```

## Testing

### Run all tests
```bash
uv run python -m pytest backend/tests/ -v
```

### Run specific test file
```bash
uv run python -m pytest backend/tests/test_pipeline.py -v
```

### Run specific test
```bash
uv run python -m pytest backend/tests/test_matcher.py::test_experience_year_safety_no_date_misinterpretation -v
```

## Important Notes

### Determinism
- Same resume + same JD = **always** identical output
- Verified by file hash comparison
- Safe for caching and comparison operations

### Evidence Integrity
- All `evidence_ref` values in `fit_report` are validated
- Must correspond to actual `field_id` in `profile.fields`
- Orphan references raise `ValueError`

### Experience Extraction
- Only explicit patterns recognized: "3 years", "4+yrs", "5 yrs experience"
- Date ranges like "2021-2024" are NOT interpreted as years
- When no explicit duration found: match_status = NOT_FOUND

### Skill Normalization
- Applied consistently across all modules
- "Python", "python", " PYTHON " → all normalize to "python"
- Aliases resolved: "js" → "javascript", "postgres" → "postgresql"

### Edge Cases Handled
- ✅ Empty resume files
- ✅ Empty job descriptions
- ✅ Missing sections (SKILLS, EXPERIENCE, etc.)
- ✅ Missing candidate info (name, email, phone)
- ✅ Duplicate skills in JD
- ✅ Multiple experience years in resume text
- ✅ Date ranges without explicit duration

## Performance

- Single resume analysis: ~100ms
- Test suite: 56 tests in <1s
- No external dependencies (local analysis only)

## Error Handling

```python
try:
    result = analyze_resume(resume_path, jd)
except TypeError as e:
    # Invalid resume_path type or job_description type
    pass
except ValueError as e:
    # Empty resume_path or other validation error
    pass
except FileNotFoundError as e:
    # Resume file not found
    pass
except Exception as e:
    # Parsing or processing error (detailed in message)
    pass
```

## Compatibility

- ✅ 100% backward compatible with Phase 1
- ✅ Phase 1 API unchanged
- ✅ Phase 1 tests still passing
- ✅ Phase 2 additions are strictly additive
- ✅ All Phase 1 functionality preserved

## Next Steps / Future Extensions

Possible future enhancements:
- [ ] Additional requirement categories (e.g., EDUCATION, CERTIFICATIONS)
- [ ] Weighted skill importance (e.g., "expert Python" vs "basic Python")
- [ ] Semantic matching (related skills, technology stacks)
- [ ] Batch processing for multiple resumes
- [ ] REST API wrapper
- [ ] Web UI for interactive analysis

## Support & Documentation

- **Implementation Details**: See `PHASE2_IMPLEMENTATION_SUMMARY.md`
- **Verification Checklist**: See `IMPLEMENTATION_CHECKLIST.md`
- **Test Coverage**: See `backend/tests/` directory
- **Code Comments**: See individual module files

---

**Version**: Phase 2 Complete  
**Status**: Production Ready  
**Last Updated**: August 20, 2026
