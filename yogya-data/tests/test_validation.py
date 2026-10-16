"""
Unit tests for deterministic validation rules in src/validation.py.
"""

import copy
import pytest
from src.validation import OpportunityValidator, validate_dataset


@pytest.fixture
def base_valid_record():
    return {
        "schema_version": "1.0.0",
        "opportunity_id": "opp_val_test_2026",
        "name": "State Pre-Matric SC Assistance",
        "category": "scholarship",
        "provider": "Department of Social Welfare",
        "description": "Financial assistance for Class 9 and 10 Scheduled Caste students.",
        "education_levels": ["class_9", "class_10"],
        "geographic_scope": {"type": "national", "states": [], "districts": []},
        "eligibility_criteria": [
            {
                "criterion_id": "crit_val_inc",
                "field": "annual_family_income",
                "operator": "less_than_or_equal",
                "value": 250000.0,
                "unit": "INR/year",
                "condition_type": "mandatory",
                "required": True,
                "evidence_reference": "ev_val_1",
                "review_status": "confirmed",
                "notes": None,
            },
            {
                "criterion_id": "crit_val_caste",
                "field": "caste_category",
                "operator": "equals",
                "value": "SC",
                "unit": None,
                "condition_type": "mandatory",
                "required": True,
                "evidence_reference": "ev_val_1",
                "review_status": "confirmed",
                "notes": "Must belong to SC category (AND logic with income).",
            },
        ],
        "required_documents": [
            {
                "document_name": "Caste Certificate",
                "document_type": "caste_proof",
                "mandatory": True,
                "description": "Authorized certificate",
                "evidence_reference": "ev_val_1",
            }
        ],
        "benefits": {
            "type": "financial",
            "financial_amount": 3500.0,
            "currency": "INR",
            "frequency": "annual",
            "description": "Scholarship allowance of Rs. 3,500/- p.a.",
            "non_financial_benefits": [],
        },
        "application_period": {
            "opening_date": "2026-07-01",
            "deadline": "2026-11-30",
            "academic_year": "2026-2027",
            "status": "open",
            "status_verification_date": "2026-10-16",
            "notes": "Active window",
        },
        "application_status": "open",
        "official_source_urls": ["https://scholarships.gov.in/sc-prematric"],
        "application_url": "https://scholarships.gov.in/",
        "evidence": [
            {
                "evidence_id": "ev_val_1",
                "field_path": "eligibility_criteria[0].value",
                "source_url": "https://scholarships.gov.in/sc-prematric",
                "source_title": "Official Guidelines",
                "supporting_excerpt": "Parental income limit of Rs. 2,50,000/- per annum for Scheduled Caste students in Class IX and X.",
                "page_number": 2,
                "section_heading": "Eligibility",
                "retrieved_at": "2026-10-16T10:00:00Z",
                "extraction_method": "manual",
                "review_status": "verified",
            }
        ],
        "last_checked_at": "2026-10-16T10:00:00Z",
        "verification_status": "draft",
        "review_notes": ["Draft verified for test"],
        "synthetic": False,
    }


def test_validator_passes_valid_record(base_valid_record):
    validator = OpportunityValidator()
    result = validator.validate_opportunity(base_valid_record)
    assert result["is_valid"] is True
    assert result["error_count"] == 0


def test_validator_catches_invalid_dates(base_valid_record):
    """Opening date after deadline must fail validation."""
    validator = OpportunityValidator()
    opp = copy.deepcopy(base_valid_record)
    opp["application_period"]["opening_date"] = "2026-12-01"
    opp["application_period"]["deadline"] = "2026-11-30"

    result = validator.validate_opportunity(opp)
    assert result["is_valid"] is False
    assert any("Opening date" in e["message"] for e in result["errors"])


def test_validator_catches_unsupported_operator(base_valid_record):
    """Unsupported operators must be flagged as errors."""
    validator = OpportunityValidator()
    opp = copy.deepcopy(base_valid_record)
    opp["eligibility_criteria"][0]["operator"] = "regex_magic"

    result = validator.validate_opportunity(opp)
    assert result["is_valid"] is False
    assert any("Unsupported operator" in e["message"] for e in result["errors"])


def test_validator_catches_negative_income_and_marks(base_valid_record):
    """Income cannot be negative; percentage marks must be 0-100."""
    validator = OpportunityValidator()
    opp = copy.deepcopy(base_valid_record)
    opp["eligibility_criteria"][0]["value"] = -50000.0

    result = validator.validate_opportunity(opp)
    assert result["is_valid"] is False
    assert any("non-negative number" in e["message"] for e in result["errors"])


def test_validator_catches_invalid_between_operator(base_valid_record):
    """Operator 'between' requires a 2-element array [min, max] where min <= max."""
    validator = OpportunityValidator()
    opp = copy.deepcopy(base_valid_record)
    opp["eligibility_criteria"][0]["operator"] = "between"
    opp["eligibility_criteria"][0]["value"] = [500000.0, 100000.0]  # min > max

    result = validator.validate_opportunity(opp)
    assert result["is_valid"] is False
    assert any("between" in e["message"] for e in result["errors"])


def test_validator_flags_unauthorized_verified_status(base_valid_record):
    """A record cannot be marked 'verified' if evidence is still pending review or review notes empty."""
    validator = OpportunityValidator()
    opp = copy.deepcopy(base_valid_record)
    opp["verification_status"] = "verified"
    opp["evidence"][0]["review_status"] = "pending_review"  # Pending!
    opp["review_notes"] = []  # No reviewer sign-off!

    result = validator.validate_opportunity(opp)
    assert result["is_valid"] is False
    assert any("verification_status" in e["field"] for e in result["errors"])


def test_dataset_validation_detects_duplicate_ids(base_valid_record):
    """Dataset-level validation must detect duplicate opportunity_ids across multiple records."""
    rec1 = copy.deepcopy(base_valid_record)
    rec2 = copy.deepcopy(base_valid_record)
    rec2["name"] = "Different Scheme Name"

    res = validate_dataset([rec1, rec2])
    assert res["invalid_records"] >= 1
    assert any("Duplicate opportunity_id" in err["message"] for r in res["record_results"] for err in r["errors"])


def test_multiple_and_conditions_preserved(base_valid_record):
    """Multiple mandatory conditions joined by AND logic are validated cleanly."""
    validator = OpportunityValidator()
    # base_valid_record has both income <= 2.5 LPA AND caste == SC
    res = validator.validate_opportunity(base_valid_record)
    assert res["is_valid"] is True
    assert len(base_valid_record["eligibility_criteria"]) == 2
    assert all(c["condition_type"] == "mandatory" for c in base_valid_record["eligibility_criteria"])


def test_unknown_or_manual_review_operator_allowed(base_valid_record):
    """Operator 'unknown_or_manual_review' is valid for ambiguous source rules."""
    validator = OpportunityValidator()
    opp = copy.deepcopy(base_valid_record)
    opp["eligibility_criteria"].append({
        "criterion_id": "crit_domicile_review",
        "field": "domicile_state",
        "operator": "unknown_or_manual_review",
        "value": None,
        "unit": None,
        "condition_type": "optional",
        "required": False,
        "evidence_reference": None,
        "review_status": "unreviewed",
        "notes": "State domicile criteria varies by state quota; requires manual document verification.",
    })
    res = validator.validate_opportunity(opp)
    assert res["is_valid"] is True
