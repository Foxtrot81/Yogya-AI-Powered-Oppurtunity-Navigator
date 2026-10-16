"""
Duplicate opportunity detection module.
Calculates lexical, semantic, and structural similarity across scheme names,
providers, source URLs, and identifiers without blind auto-merging.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from rapidfuzz import fuzz

from src.config import config

logger = logging.getLogger(__name__)

STOPWORDS = {
    "scheme",
    "scholarship",
    "yojana",
    "programme",
    "program",
    "initiative",
    "for",
    "and",
    "the",
    "of",
    "in",
    "to",
    "students",
    "india",
    "national",
    "central",
    "state",
}


GENERIC_PORTAL_URLS = {
    "https://scholarships.gov.in/",
    "https://scholarships.gov.in",
    "https://www.skillindiadigital.gov.in/",
    "https://www.skillindiadigital.gov.in",
    "https://www.bharatskill.gov.in/",
    "https://www.bharatskill.gov.in",
    "https://data.gov.in/",
    "https://data.gov.in",
    "https://www.apprenticeshipindia.gov.in/",
    "https://www.apprenticeshipindia.gov.in",
}


def normalize_scheme_name(name: str) -> str:
    """Normalize a scheme name for robust comparison."""
    if not name:
        return ""
    # Lowercase & remove punctuation
    clean = re.sub(r"[^\w\s]", " ", name.lower())
    words = clean.split()
    filtered = [w for w in words if w not in STOPWORDS]
    return " ".join(filtered) if filtered else clean


def detect_duplicate_candidates(
    opportunities: List[Dict[str, Any]],
    similarity_threshold: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Compares all opportunities pairwise to identify potential duplicates.
    Never auto-merges; produces a structured report for human review.
    """
    threshold = (
        similarity_threshold
        or config.deduplication_config.get("name_similarity_threshold", 0.85)
    )
    # Convert threshold to 0-100 scale for rapidfuzz
    fuzz_threshold = threshold * 100 if threshold <= 1.0 else threshold

    candidates: List[Dict[str, Any]] = []
    n = len(opportunities)

    for i in range(n):
        opp_a = opportunities[i]
        id_a = opp_a.get("opportunity_id", f"opp_{i}")
        name_a = opp_a.get("name", "")
        norm_a = normalize_scheme_name(name_a)
        prov_a = opp_a.get("provider", "").lower()
        urls_a = set(opp_a.get("official_source_urls", []))
        app_url_a = opp_a.get("application_url")
        if app_url_a:
            urls_a.add(app_url_a)

        for j in range(i + 1, n):
            opp_b = opportunities[j]
            id_b = opp_b.get("opportunity_id", f"opp_{j}")
            name_b = opp_b.get("name", "")
            norm_b = normalize_scheme_name(name_b)
            prov_b = opp_b.get("provider", "").lower()
            urls_b = set(opp_b.get("official_source_urls", []))
            app_url_b = opp_b.get("application_url")
            if app_url_b:
                urls_b.add(app_url_b)

            match_reasons = []
            confidence = 0.0

            # 1. Exact ID match (error in dataset)
            if id_a == id_b:
                match_reasons.append("Identical opportunity_id")
                confidence = 1.0

            # 2. Exact URL intersection (excluding generic portal roots)
            specific_urls_a = {u for u in urls_a if u not in GENERIC_PORTAL_URLS}
            specific_urls_b = {u for u in urls_b if u not in GENERIC_PORTAL_URLS}
            shared_urls = specific_urls_a.intersection(specific_urls_b)
            if shared_urls:
                match_reasons.append(f"Shared official URL(s): {list(shared_urls)}")
                confidence = max(confidence, 0.90)

            # 3. Name similarity check
            ratio = fuzz.token_sort_ratio(norm_a, norm_b)
            if ratio >= fuzz_threshold:
                match_reasons.append(f"High name similarity ({ratio:.1f}%): '{name_a}' vs '{name_b}'")
                confidence = max(confidence, ratio / 100.0)

            # 4. Check provider similarity
            provider_ratio = fuzz.token_set_ratio(prov_a, prov_b)
            is_same_provider = provider_ratio >= 80

            if match_reasons and (is_same_provider or shared_urls or ratio >= 92):
                # Analyze potential differences in academic year or target groups
                period_a = opp_a.get("application_period", {}).get("academic_year")
                period_b = opp_b.get("application_period", {}).get("academic_year")
                diff_notes = []
                if period_a and period_b and period_a != period_b:
                    diff_notes.append(f"Different academic years: {period_a} vs {period_b} (may be distinct annual cohorts)")

                cat_a = opp_a.get("category")
                cat_b = opp_b.get("category")
                if cat_a != cat_b:
                    diff_notes.append(f"Different categories: {cat_a} vs {cat_b}")

                candidates.append({
                    "opportunity_id_a": id_a,
                    "opportunity_id_b": id_b,
                    "name_a": name_a,
                    "name_b": name_b,
                    "provider_a": opp_a.get("provider"),
                    "provider_b": opp_b.get("provider"),
                    "confidence_score": round(confidence, 2),
                    "reasons": match_reasons,
                    "distinctions": diff_notes,
                    "recommended_action": (
                        "Investigate: likely duplicate from different sources"
                        if not diff_notes
                        else "Keep separate: distinct cohorts or categories"
                    ),
                })

    return candidates
