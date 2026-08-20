from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class EvidenceField:
    value: Optional[str] = None
    evidence: Optional[str] = None
    source_section: Optional[str] = None

@dataclass
class FitRequirement:
    # Placeholder for Phase 2 compatibility
    requirement: str
    is_met: bool
    evidence: Optional[str] = None

@dataclass
class AnalysisResult:
    candidate: Dict[str, Any]  # contains name, email, phone
    sections: Dict[str, str]
    job_description: str

    def to_dict(self) -> Dict[str, Any]:
        """Converts the AnalysisResult structure to a JSON-compatible dict."""
        return asdict(self)
