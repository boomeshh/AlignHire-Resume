"""
Models Module

Defines the structure of the data processed and output by ProofResume.
Ensures strict adherence to schema constraints and types.
"""

from dataclasses import dataclass, asdict

@dataclass
class CandidateField:
    field_id: str
    category: str
    status: str  # "FOUND" | "NOT_FOUND" | "AMBIGUOUS"
    value: str   # Extracted value, or "NOT_FOUND" if not found
    evidence: str  # The exact sentence/context containing the field value
    source_section: str  # The name of the section this was extracted from

@dataclass
class CandidateProfile:
    full_name: CandidateField
    email: CandidateField
    phone: CandidateField
    skills: CandidateField
    education: CandidateField

    def to_dict(self) -> dict:
        """
        Converts the CandidateProfile instance to a serializable dictionary.
        """
        return asdict(self)
