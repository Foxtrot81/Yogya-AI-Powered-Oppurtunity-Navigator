"""
Unit tests for duplicate candidate detection in src/deduplication.py.
"""

import pytest
from src.deduplication import detect_duplicate_candidates, normalize_scheme_name


def test_normalize_scheme_name():
    name = "The National Means-cum-Merit Scholarship Scheme for Students in India!"
    normalized = normalize_scheme_name(name)
    assert "scholarship" not in normalized
    assert "scheme" not in normalized
    assert "means cum merit" in normalized


def test_detects_high_similarity_near_duplicates():
    opp_a = {
        "opportunity_id": "opp_nmms_a",
        "name": "National Means-cum-Merit Scholarship Scheme",
        "provider": "Department of School Education and Literacy",
        "official_source_urls": ["https://scholarships.gov.in/nmms"],
        "application_period": {"academic_year": "2025-2026"},
    }
    opp_b = {
        "opportunity_id": "opp_nmms_b",
        "name": "National Means cum Merit Scholarship (NMMSS)",
        "provider": "Department of School Education & Literacy",
        "official_source_urls": ["https://dsel.education.gov.in/scheme/nmmss"],
        "application_period": {"academic_year": "2025-2026"},
    }

    candidates = detect_duplicate_candidates([opp_a, opp_b], similarity_threshold=0.80)
    assert len(candidates) == 1
    cand = candidates[0]
    assert cand["confidence_score"] >= 0.80
    assert "opp_nmms_a" in [cand["opportunity_id_a"], cand["opportunity_id_b"]]


def test_highlights_different_academic_years():
    opp_2025 = {
        "opportunity_id": "opp_sc_2025",
        "name": "Pre-Matric Scholarship for SC Students",
        "provider": "Ministry of Social Justice and Empowerment",
        "official_source_urls": ["https://scholarships.gov.in/"],
        "application_period": {"academic_year": "2024-2025"},
    }
    opp_2026 = {
        "opportunity_id": "opp_sc_2026",
        "name": "Pre-Matric Scholarship for SC Students",
        "provider": "Ministry of Social Justice and Empowerment",
        "official_source_urls": ["https://scholarships.gov.in/"],
        "application_period": {"academic_year": "2025-2026"},
    }

    candidates = detect_duplicate_candidates([opp_2025, opp_2026], similarity_threshold=0.85)
    assert len(candidates) == 1
    cand = candidates[0]
    # Must flag the distinction in academic years
    assert any("Different academic years" in d for d in cand["distinctions"])
    assert "Keep separate" in cand["recommended_action"]


def test_distinct_schemes_not_flagged():
    opp_sc = {
        "opportunity_id": "opp_sc",
        "name": "Pre-Matric Scholarship for Scheduled Caste Students",
        "provider": "Ministry of Social Justice and Empowerment",
        "official_source_urls": ["https://socialjustice.gov.in/sc"],
    }
    opp_st = {
        "opportunity_id": "opp_st",
        "name": "Vocational Training Scheme for Craftsmen in ITI",
        "provider": "Directorate General of Training",
        "official_source_urls": ["https://bharatskill.gov.in/"],
    }

    candidates = detect_duplicate_candidates([opp_sc, opp_st])
    assert len(candidates) == 0
