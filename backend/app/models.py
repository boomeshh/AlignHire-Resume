from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List

@dataclass
class EvidenceField:
    value: Optional[Any] = None
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
    profile: Dict[str, Any] = field(default_factory=lambda: {"fields": []})
    requirements: List[Dict[str, Any]] = field(default_factory=list)
    fit_score: Dict[str, Any] = field(default_factory=lambda: {"score": 0, "breakdown": {}})
    fit_report: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the AnalysisResult structure to a JSON-compatible dict."""
        return asdict(self)
