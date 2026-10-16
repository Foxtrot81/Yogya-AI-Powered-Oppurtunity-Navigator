"""
Unit tests for export functionality (JSON and CSV) in src/exports.py.
"""

import csv
import json
import tempfile
from pathlib import Path
import pytest
from src.exports import OpportunityExporter


@pytest.fixture
def sample_opportunities():
    return [
        {
            "schema_version": "1.0.0",
            "opportunity_id": "opp_exp_1",
            "name": "Export Test Scheme 1",
            "category": "scholarship",
            "provider": "Ministry of Education",
            "description": "First export test scheme description.",
            "education_levels": ["class_9", "class_10"],
            "geographic_scope": {"type": "national"},
            "eligibility_criteria": [
                {"field": "annual_family_income", "operator": "less_than_or_equal", "value": 250000.0}
            ],
            "required_documents": [{"document_name": "Income Certificate"}],
            "benefits": {
                "type": "financial",
                "financial_amount": 10000.0,
                "currency": "INR",
                "frequency": "annual",
                "description": "Rs. 10000 annual scholarship",
            },
            "application_period": {"status": "open", "opening_date": "2026-07-01", "deadline": "2026-10-31"},
            "application_status": "open",
            "official_source_urls": ["https://scholarships.gov.in/test1"],
            "verification_status": "verified",
            "last_checked_at": "2026-10-16T10:00:00Z",
            "synthetic": False,
        },
        {
            "schema_version": "1.0.0",
            "opportunity_id": "opp_exp_2",
            "name": "Export Test Scheme 2",
            "category": "vocational_training",
            "provider": "MSDE",
            "description": "Second export test scheme description.",
            "education_levels": ["vocational"],
            "geographic_scope": {"type": "state", "states": ["Maharashtra"]},
            "eligibility_criteria": [],
            "required_documents": [],
            "benefits": {"type": "training_and_certification", "financial_amount": None, "currency": "INR", "description": "Free training"},
            "application_period": {"status": "upcoming"},
            "application_status": "upcoming",
            "official_source_urls": ["https://skillindiadigital.gov.in/test2"],
            "verification_status": "draft",
            "last_checked_at": "2026-10-16T10:00:00Z",
            "synthetic": False,
        },
    ]


def test_exporter_creates_partitioned_files(sample_opportunities):
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir)
        exporter = OpportunityExporter(output_dir=out_dir)
        paths = exporter.export_all(sample_opportunities)

        # Check all partitioned files exist
        assert paths["all_json"].exists()
        assert paths["all_csv"].exists()
        assert paths["verified_json"].exists()
        assert paths["drafts_json"].exists()

        # Check JSON contents
        with open(paths["verified_json"], "r", encoding="utf-8") as f:
            verified_list = json.load(f)
            assert len(verified_list) == 1
            assert verified_list[0]["opportunity_id"] == "opp_exp_1"

        with open(paths["drafts_json"], "r", encoding="utf-8") as f:
            drafts_list = json.load(f)
            assert len(drafts_list) == 1
            assert drafts_list[0]["opportunity_id"] == "opp_exp_2"

        # Check CSV contents
        with open(paths["all_csv"], "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["opportunity_id"] == "opp_exp_1"
            assert rows[0]["financial_amount"] == "10000.0"
            assert "annual_family_income less_than_or_equal 250000.0" in rows[0]["eligibility_summary"]


def test_safe_repeatable_exports(sample_opportunities):
    """Calling export repeatedly does not fail or produce malformed files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir)
        exporter = OpportunityExporter(output_dir=out_dir)
        exporter.export_all(sample_opportunities)
        # Second run
        paths2 = exporter.export_all(sample_opportunities)
        assert paths2["all_json"].exists()
        with open(paths2["all_json"], "r", encoding="utf-8") as f:
            data = json.load(f)
            assert len(data) == 2
