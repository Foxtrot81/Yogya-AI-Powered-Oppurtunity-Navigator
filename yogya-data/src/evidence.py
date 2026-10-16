"""
Evidence management, excerpt validation, and traceability tracking.
"""

from typing import Any, Dict, List, Optional, Tuple
import re


def normalize_text_for_search(text: str) -> str:
    """Normalize whitespace and punctuation for excerpt presence check."""
    return re.sub(r"\s+", " ", text).strip().lower()


def check_excerpt_presence(excerpt: str, full_source_text: str) -> bool:
    """
    Check if the claimed evidence excerpt genuinely exists within the source document.
    Prevents hallucinated or invented quotes.
    """
    if not excerpt or not full_source_text:
        return False
    
    norm_excerpt = normalize_text_for_search(excerpt)
    norm_source = normalize_text_for_search(full_source_text)
    
    # Exact substring match
    if norm_excerpt in norm_source:
        return True
    
    # Prefix / suffix tolerance for minor boundary clipping
    words = norm_excerpt.split()
    if len(words) >= 6:
        # Check if first 5 words and last 5 words appear in source
        first_segment = " ".join(words[:5])
        last_segment = " ".join(words[-5:])
        return (first_segment in norm_source) and (last_segment in norm_source)
        
    return False


def audit_opportunity_evidence(opp: Dict[str, Any], full_source_text: Optional[str] = None) -> Tuple[List[str], List[str]]:
    """
    Audits an opportunity record for evidence integrity.
    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []

    evidence_list = opp.get("evidence", [])
    evidence_ids = {ev.get("evidence_id") for ev in evidence_list if ev.get("evidence_id")}

    # Check evidence format
    for idx, ev in enumerate(evidence_list):
        ev_id = ev.get("evidence_id", f"idx_{idx}")
        excerpt = ev.get("supporting_excerpt", "")
        if not excerpt or len(excerpt.strip()) < 5:
            errors.append(f"Evidence '{ev_id}' has an empty or trivial supporting excerpt.")
        elif full_source_text:
            if not check_excerpt_presence(excerpt, full_source_text):
                warnings.append(f"Evidence '{ev_id}' excerpt could not be verified in the supplied source text.")

        if not ev.get("source_url"):
            errors.append(f"Evidence '{ev_id}' lacks a source_url.")

    # Audit eligibility criteria evidence references
    criteria = opp.get("eligibility_criteria", [])
    for c in criteria:
        c_id = c.get("criterion_id", "unknown_criterion")
        ref = c.get("evidence_reference")
        is_mandatory = c.get("condition_type") == "mandatory" or c.get("required") is True

        if is_mandatory and not ref:
            warnings.append(f"Mandatory criterion '{c_id}' lacks an evidence_reference.")
        elif ref and ref not in evidence_ids:
            errors.append(f"Criterion '{c_id}' references non-existent evidence_id '{ref}'.")

    # Audit financial benefit evidence
    benefits = opp.get("benefits", {})
    if benefits.get("financial_amount") is not None and benefits.get("financial_amount") > 0:
        has_benefit_ev = any("benefit" in ev.get("field_path", "") or "financial" in ev.get("field_path", "") for ev in evidence_list)
        if not has_benefit_ev:
            warnings.append(f"Financial benefit amount ({benefits.get('financial_amount')} INR) does not have explicit evidence linked in field_path.")

    # Audit application deadline evidence
    app_period = opp.get("application_period", {})
    if app_period.get("deadline") and app_period.get("status") in ["open", "upcoming"]:
        has_deadline_ev = any("deadline" in ev.get("field_path", "") or "application_period" in ev.get("field_path", "") for ev in evidence_list)
        if not has_deadline_ev:
            warnings.append(f"Application deadline ({app_period.get('deadline')}) has no explicit evidence linked in field_path.")

    return errors, warnings
