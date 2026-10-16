"""
Unit tests for evidence tracking, excerpt verification, and anti-hallucination checks.
"""

import pytest
from src.evidence import check_excerpt_presence, audit_opportunity_evidence


def test_excerpt_presence_verification():
    source_doc = """
    GOVERNMENT OF INDIA SCHOLARSHIP NOTIFICATION
    Under the National Means-cum-Merit Scholarship Scheme, students whose parental income
    from all sources is not more than Rs. 3,50,000/- per annum are eligible to receive
    an annual scholarship of Rs. 12,000/- from Class 9 to 12.
    """

    genuine_excerpt = "parental income from all sources is not more than Rs. 3,50,000/- per annum"
    hallucinated_excerpt = "Students must score at least 98% in mathematics and physics to qualify."

    assert check_excerpt_presence(genuine_excerpt, source_doc) is True
    assert check_excerpt_presence(hallucinated_excerpt, source_doc) is False


def test_audit_flags_missing_criterion_evidence():
    opp = {
        "eligibility_criteria": [
            {
                "criterion_id": "crit_inc",
                "condition_type": "mandatory",
                "required": True,
                "evidence_reference": None,  # Missing!
            }
        ],
        "benefits": {"financial_amount": 0},
        "application_period": {"status": "closed"},
        "evidence": [],
    }

    errors, warnings = audit_opportunity_evidence(opp)
    assert any("crit_inc" in w and "lacks an evidence_reference" in w for w in warnings)


def test_audit_flags_nonexistent_evidence_reference():
    opp = {
        "eligibility_criteria": [
            {
                "criterion_id": "crit_inc",
                "condition_type": "mandatory",
                "required": True,
                "evidence_reference": "ev_non_existent",  # Does not exist in evidence array!
            }
        ],
        "benefits": {"financial_amount": 0},
        "application_period": {"status": "closed"},
        "evidence": [
            {
                "evidence_id": "ev_other",
                "supporting_excerpt": "Valid non-empty excerpt from official source.",
                "source_url": "https://scholarships.gov.in/",
            }
        ],
    }

    errors, warnings = audit_opportunity_evidence(opp)
    assert any("non-existent evidence_id" in e for e in errors)


def test_audit_flags_trivial_or_blank_excerpt():
    opp = {
        "eligibility_criteria": [],
        "benefits": {"financial_amount": 0},
        "application_period": {"status": "closed"},
        "evidence": [
            {
                "evidence_id": "ev_blank",
                "supporting_excerpt": "   ",  # Blank!
                "source_url": "https://scholarships.gov.in/",
            }
        ],
    }

    errors, warnings = audit_opportunity_evidence(opp)
    assert any("empty or trivial supporting excerpt" in e for e in errors)
