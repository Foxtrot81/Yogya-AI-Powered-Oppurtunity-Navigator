"""
Core domain data models for Yogya Opportunities, Eligibility Criteria, and Evidence.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


@dataclass
class EvidenceItem:
    evidence_id: str
    field_path: str
    source_url: str
    supporting_excerpt: str
    retrieved_at: str
    extraction_method: str  # "manual", "rule_based", "llm_gemini", "llm_openai", "llm_fallback"
    review_status: str  # "pending_review", "verified", "rejected", "flagged"
    source_title: Optional[str] = None
    page_number: Optional[int] = None
    section_heading: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EligibilityCriterion:
    criterion_id: str
    field: str  # e.g., "annual_family_income", "caste_category", "min_marks_percentage", "gender", "domicile_state"
    operator: str  # "equals", "less_than_or_equal", "in", etc.
    condition_type: str  # "mandatory", "optional", "disqualification", "preference"
    required: bool
    value: Any = None
    unit: Optional[str] = None
    evidence_reference: Optional[str] = None  # matches evidence_id
    review_status: str = "unreviewed"  # "unreviewed", "confirmed", "flagged", "rejected"
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RequiredDocument:
    document_name: str
    document_type: str
    mandatory: bool
    description: Optional[str] = None
    evidence_reference: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Benefits:
    type: str  # "financial", "stipend", "tuition_waiver", "in_kind", "composite", "training_and_certification"
    description: str
    financial_amount: Optional[float] = None
    currency: Optional[str] = "INR"
    frequency: Optional[str] = None  # "annual", "monthly", "one_time", "course_duration", "variable"
    non_financial_benefits: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ApplicationPeriod:
    status: str  # "open", "closed", "upcoming", "unknown"
    opening_date: Optional[str] = None  # ISO 8601 YYYY-MM-DD
    deadline: Optional[str] = None  # ISO 8601 YYYY-MM-DD
    academic_year: Optional[str] = None
    status_verification_date: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GeographicScope:
    type: str  # "national", "state", "district"
    states: List[str] = field(default_factory=list)
    districts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Opportunity:
    schema_version: str
    opportunity_id: str
    name: str
    category: str
    provider: str
    description: str
    education_levels: List[str]
    geographic_scope: GeographicScope
    eligibility_criteria: List[EligibilityCriterion]
    required_documents: List[RequiredDocument]
    benefits: Benefits
    application_period: ApplicationPeriod
    application_status: str
    official_source_urls: List[str]
    evidence: List[EvidenceItem]
    last_checked_at: str
    verification_status: str  # "draft", "needs_review", "reviewed", "verified", "stale", "rejected"
    application_url: Optional[str] = None
    review_notes: List[str] = field(default_factory=list)
    synthetic: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Opportunity":
        # Parse nested dataclasses safely
        geo_data = data.get("geographic_scope", {})
        geographic_scope = GeographicScope(
            type=geo_data.get("type", "national"),
            states=geo_data.get("states", []),
            districts=geo_data.get("districts", []),
        )

        criteria = []
        for c in data.get("eligibility_criteria", []):
            criteria.append(
                EligibilityCriterion(
                    criterion_id=c.get("criterion_id", ""),
                    field=c.get("field", ""),
                    operator=c.get("operator", "unknown_or_manual_review"),
                    condition_type=c.get("condition_type", "mandatory"),
                    required=c.get("required", True),
                    value=c.get("value"),
                    unit=c.get("unit"),
                    evidence_reference=c.get("evidence_reference"),
                    review_status=c.get("review_status", "unreviewed"),
                    notes=c.get("notes"),
                )
            )

        documents = []
        for doc in data.get("required_documents", []):
            documents.append(
                RequiredDocument(
                    document_name=doc.get("document_name", ""),
                    document_type=doc.get("document_type", "certificate"),
                    mandatory=doc.get("mandatory", True),
                    description=doc.get("description"),
                    evidence_reference=doc.get("evidence_reference"),
                )
            )

        b_data = data.get("benefits", {})
        benefits = Benefits(
            type=b_data.get("type", "financial"),
            description=b_data.get("description", ""),
            financial_amount=b_data.get("financial_amount"),
            currency=b_data.get("currency", "INR"),
            frequency=b_data.get("frequency"),
            non_financial_benefits=b_data.get("non_financial_benefits", []),
        )

        app_p = data.get("application_period", {})
        application_period = ApplicationPeriod(
            status=app_p.get("status", data.get("application_status", "unknown")),
            opening_date=app_p.get("opening_date"),
            deadline=app_p.get("deadline"),
            academic_year=app_p.get("academic_year"),
            status_verification_date=app_p.get("status_verification_date"),
            notes=app_p.get("notes"),
        )

        evidence_items = []
        for ev in data.get("evidence", []):
            evidence_items.append(
                EvidenceItem(
                    evidence_id=ev.get("evidence_id", ""),
                    field_path=ev.get("field_path", ""),
                    source_url=ev.get("source_url", ""),
                    supporting_excerpt=ev.get("supporting_excerpt", ""),
                    retrieved_at=ev.get(
                        "retrieved_at",
                        datetime.now(timezone.utc).isoformat(),
                    ),
                    extraction_method=ev.get("extraction_method", "manual"),
                    review_status=ev.get("review_status", "pending_review"),
                    source_title=ev.get("source_title"),
                    page_number=ev.get("page_number"),
                    section_heading=ev.get("section_heading"),
                )
            )

        return cls(
            schema_version=data.get("schema_version", "1.0.0"),
            opportunity_id=data.get("opportunity_id", ""),
            name=data.get("name", ""),
            category=data.get("category", "other"),
            provider=data.get("provider", ""),
            description=data.get("description", ""),
            education_levels=data.get("education_levels", []),
            geographic_scope=geographic_scope,
            eligibility_criteria=criteria,
            required_documents=documents,
            benefits=benefits,
            application_period=application_period,
            application_status=data.get("application_status", application_period.status),
            official_source_urls=data.get("official_source_urls", []),
            evidence=evidence_items,
            last_checked_at=data.get(
                "last_checked_at",
                datetime.now(timezone.utc).isoformat(),
            ),
            verification_status=data.get("verification_status", "draft"),
            application_url=data.get("application_url"),
            review_notes=data.get("review_notes", []),
            synthetic=data.get("synthetic", False),
        )
