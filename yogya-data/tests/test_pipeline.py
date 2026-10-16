"""
Integration and end-to-end tests for the Yogya Pipeline components.
Covers ingestion, fallback extraction, review state machine, and database protection.
"""

import json
import tempfile
from pathlib import Path
import pytest

from src.source_ingestion import SourceIngestion
from src.extraction import get_extractor, RuleBasedFallbackExtractor
from src.review import ReviewManager, ReviewWorkflowError
from src.database import DatabaseImporter
from src.reporting import ReportGenerator


def test_source_ingestion_manual_text():
    ingestor = SourceIngestion()
    res = ingestor.ingest_manual_text(
        text="Official guidelines for National Scholarship Scheme. Income limit Rs. 2,50,000 p.a.",
        source_url="https://scholarships.gov.in/test-manual",
        source_title="Test Scheme",
    )
    assert res["retrieval_status"] == "success"
    assert res["extraction_status"] == "extracted"
    assert res["content_hash"] is not None
    assert len(res["text"]) > 10


def test_fallback_extractor_operates_without_llm():
    """Fallback extractor must operate deterministically without external LLM calls."""
    extractor = RuleBasedFallbackExtractor()
    text = """
    MINISTRY OF SOCIAL JUSTICE AND EMPOWERMENT
    Scholarship Scheme for Pre-Matric SC Students
    Parental income must not exceed Rs. 2,50,000/- per annum.
    Students studying in Class 9 and 10 are eligible.
    Scholarship amount of Rs. 3500 per annum will be disbursed.
    Last date to apply is 2026-11-30.
    """
    res = extractor.extract_from_text(
        text=text,
        source_url="https://scholarships.gov.in/test-sc",
        source_title="SC Pre-Matric Scheme",
    )

    opps = res.get("opportunities", [])
    assert len(opps) == 1
    opp = opps[0]
    assert opp["category"] == "scholarship"
    assert "class_9" in opp["education_levels"]
    assert opp["verification_status"] == "draft"  # Never verified directly!
    assert len(opp["evidence"]) >= 1


def test_review_manager_state_machine_enforcement():
    """State machine must block illegal transitions and prevent verifying records without human review."""
    mgr = ReviewManager()
    record = {
        "opportunity_id": "opp_test_sm",
        "name": "Test State Machine Scheme",
        "verification_status": "draft",
        "review_notes": [],
        "evidence": [],
        "eligibility_criteria": [],
    }

    # Attempting to jump directly from draft to verified must raise ReviewWorkflowError
    with pytest.raises(ReviewWorkflowError):
        mgr.apply_transition(record, new_status="verified", reviewer_id="qa_reviewer", notes="Trying shortcut")

    # Valid step 1: draft -> needs_review
    rec2 = mgr.apply_transition(record, new_status="needs_review", reviewer_id="qa_reviewer", notes="Ready for audit")
    assert rec2["verification_status"] == "needs_review"

    # Valid step 2: needs_review -> reviewed
    rec3 = mgr.apply_transition(rec2, new_status="reviewed", reviewer_id="senior_qa", notes="Audit complete")
    assert rec3["verification_status"] == "reviewed"


def test_database_importer_protects_verified_records_from_unreviewed_overwrites():
    """If a record is verified, incoming unreviewed drafts must be skipped rather than overwriting."""
    importer = DatabaseImporter()

    verified_opp = {
        "schema_version": "1.0.0",
        "opportunity_id": "opp_protected_1",
        "name": "Verified Scheme Name",
        "category": "scholarship",
        "provider": "Ministry of Education",
        "description": "Verified official record description.",
        "education_levels": ["class_9"],
        "geographic_scope": {"type": "national"},
        "eligibility_criteria": [
            {
                "criterion_id": "crit_p1",
                "field": "annual_family_income",
                "operator": "less_than_or_equal",
                "value": 350000.0,
                "unit": "INR/year",
                "condition_type": "mandatory",
                "required": True,
                "evidence_reference": "ev_p1",
                "review_status": "confirmed",
            }
        ],
        "required_documents": [
            {"document_name": "Income Cert", "document_type": "income_proof", "mandatory": True, "evidence_reference": "ev_p1"}
        ],
        "benefits": {"type": "financial", "financial_amount": 12000.0, "currency": "INR", "description": "12k"},
        "application_period": {"status": "closed", "deadline": "2025-11-30"},
        "application_status": "closed",
        "official_source_urls": ["https://scholarships.gov.in/p1"],
        "evidence": [
            {
                "evidence_id": "ev_p1",
                "field_path": "eligibility_criteria[0].value",
                "source_url": "https://scholarships.gov.in/p1",
                "supporting_excerpt": "Income must be less than 350000.",
                "retrieved_at": "2026-10-16T10:00:00Z",
                "extraction_method": "manual",
                "review_status": "verified",
            }
        ],
        "last_checked_at": "2026-10-16T10:00:00Z",
        "verification_status": "verified",
        "review_notes": ["Human verified"],
        "synthetic": False,
    }

    # First import: initial insertion as verified
    rep1 = importer.import_records([verified_opp], dry_run=True)
    assert rep1["inserted"] == 1

    # Incoming draft version with same opportunity_id
    incoming_draft = dict(verified_opp)
    incoming_draft["verification_status"] = "draft"
    incoming_draft["name"] = "Corrupted unreviewed overwrite attempt"

    rep2 = importer.import_records([verified_opp, incoming_draft], dry_run=True)
    # The verified record should be inserted/updated, but the incoming draft should be skipped!
    assert rep2["skipped"] == 1
    assert any("cannot overwrite" in d["reason"] for d in rep2["details"] if d["action"] == "skipped")


def test_reporting_generation():
    """Ensure report generator produces valid JSON and Markdown reports."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        rep_gen = ReportGenerator(output_dir=Path(tmp_dir))
        val_res = {
            "total_records_processed": 1,
            "valid_records": 1,
            "invalid_records": 0,
            "records_requiring_human_review": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "record_results": [],
        }
        opps = [
            {
                "opportunity_id": "opp_rep_test",
                "name": "Reporting Test Scheme",
                "category": "scholarship",
                "provider": "Ministry of Education",
                "verification_status": "verified",
                "application_period": {"status": "open", "deadline": "2026-11-30"},
            }
        ]
        res = rep_gen.generate_summary_report(
            validation_results=val_res,
            duplicate_candidates=[],
            opportunities=opps,
        )
        assert res["json"].exists()
        assert res["markdown"].exists()

        with open(res["markdown"], "r", encoding="utf-8") as f:
            md_text = f.read()
            assert "Yogya Opportunity Data Pipeline" in md_text
            assert "Reporting Test Scheme" in md_text
