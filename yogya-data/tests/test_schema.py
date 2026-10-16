"""
Unit tests for Yogya Opportunity JSON Schemas (opportunity.schema.json & extraction.schema.json).
"""

import copy
import json
import pytest
from jsonschema import validate, ValidationError

from src.config import config


@pytest.fixture
def valid_opportunity():
    return {
        "schema_version": "1.0.0",
        "opportunity_id": "opp_test_scheme_2026",
        "name": "National Test Merit Scholarship Scheme",
        "category": "scholarship",
        "provider": "Ministry of Education",
        "description": "Standard test scholarship scheme for secondary school students.",
        "education_levels": ["class_9", "class_10"],
        "geographic_scope": {
            "type": "national",
            "states": [],
            "districts": [],
        },
        "eligibility_criteria": [
            {
                "criterion_id": "crit_test_inc",
                "field": "annual_family_income",
                "operator": "less_than_or_equal",
                "value": 250000.0,
                "unit": "INR/year",
                "condition_type": "mandatory",
                "required": True,
                "evidence_reference": "ev_test_1",
                "review_status": "confirmed",
                "notes": None,
            }
        ],
        "required_documents": [
            {
                "document_name": "Income Certificate",
                "document_type": "income_proof",
                "mandatory": True,
                "description": "Valid revenue authority certificate",
                "evidence_reference": "ev_test_1",
            }
        ],
        "benefits": {
            "type": "financial",
            "financial_amount": 10000.0,
            "currency": "INR",
            "frequency": "annual",
            "description": "Direct financial scholarship of Rs. 10,000/- p.a.",
            "non_financial_benefits": [],
        },
        "application_period": {
            "opening_date": "2026-07-01",
            "deadline": "2026-10-31",
            "academic_year": "2026-2027",
            "status": "open",
            "status_verification_date": "2026-10-16",
            "notes": "Annual application window",
        },
        "application_status": "open",
        "official_source_urls": ["https://scholarships.gov.in/test-scheme"],
        "application_url": "https://scholarships.gov.in/",
        "evidence": [
            {
                "evidence_id": "ev_test_1",
                "field_path": "eligibility_criteria[0].value",
                "source_url": "https://scholarships.gov.in/test-scheme",
                "source_title": "Official Test Scheme Guidelines",
                "supporting_excerpt": "Annual family income must not exceed Rs. 2,50,000/- per annum.",
                "page_number": 1,
                "section_heading": "Eligibility Criteria",
                "retrieved_at": "2026-10-16T10:00:00Z",
                "extraction_method": "manual",
                "review_status": "verified",
            }
        ],
        "last_checked_at": "2026-10-16T10:00:00Z",
        "verification_status": "draft",
        "review_notes": ["Initial test record created"],
        "synthetic": False,
    }


@pytest.fixture
def opp_schema():
    with open(config.opportunity_schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_valid_opportunity_passes_schema(valid_opportunity, opp_schema):
    """Ensure a compliant opportunity passes JSON schema validation."""
    validate(instance=valid_opportunity, schema=opp_schema)


def test_missing_required_field_fails(valid_opportunity, opp_schema):
    """Ensure omitting required top-level fields raises ValidationError."""
    opp = copy.deepcopy(valid_opportunity)
    del opp["opportunity_id"]
    with pytest.raises(ValidationError):
        validate(instance=opp, schema=opp_schema)


def test_invalid_category_fails(valid_opportunity, opp_schema):
    """Ensure invalid categories are rejected by the schema enum."""
    opp = copy.deepcopy(valid_opportunity)
    opp["category"] = "unsupported_lottery"
    with pytest.raises(ValidationError):
        validate(instance=opp, schema=opp_schema)


def test_invalid_education_level_fails(valid_opportunity, opp_schema):
    """Ensure invalid education levels are rejected."""
    opp = copy.deepcopy(valid_opportunity)
    opp["education_levels"] = ["kindergarten_nonexistent"]
    with pytest.raises(ValidationError):
        validate(instance=opp, schema=opp_schema)


def test_invalid_date_format_fails(valid_opportunity, opp_schema):
    """Ensure dates not matching YYYY-MM-DD pattern fail schema validation."""
    opp = copy.deepcopy(valid_opportunity)
    opp["application_period"]["deadline"] = "31-10-2026"  # Non-ISO format
    with pytest.raises(ValidationError):
        validate(instance=opp, schema=opp_schema)
