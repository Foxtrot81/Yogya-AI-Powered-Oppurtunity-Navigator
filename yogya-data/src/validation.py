"""
Deterministic validation engine for Yogya Opportunity records.
Performs JSON Schema verification, logical rule checks, evidence audits,
date sanity, operator consistency, and anti-hallucination verification enforcement.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
from urllib.parse import urlparse
import jsonschema

from src.config import config
from src.evidence import audit_opportunity_evidence

logger = logging.getLogger(__name__)

ALLOWED_OPERATORS = {
    "equals",
    "not_equals",
    "less_than",
    "less_than_or_equal",
    "greater_than",
    "greater_than_or_equal",
    "in",
    "not_in",
    "between",
    "contains",
    "requires_document",
    "unknown_or_manual_review",
}

VALID_STATUSES = {"draft", "needs_review", "reviewed", "verified", "stale", "rejected"}


class ValidationErrorItem:
    def __init__(self, field: str, message: str, severity: str = "ERROR"):
        self.field = field
        self.message = message
        self.severity = severity  # "ERROR" or "WARNING"

    def to_dict(self) -> Dict[str, str]:
        return {"field": self.field, "message": self.message, "severity": self.severity}


class OpportunityValidator:
    def __init__(self, schema_path: Optional[Path] = None):
        self.schema_path = schema_path or config.opportunity_schema_path
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        self.validator_cls = jsonschema.validators.validator_for(self.schema)
        self.validator = self.validator_cls(self.schema)

    def validate_schema(self, opp: Dict[str, Any]) -> List[ValidationErrorItem]:
        """Validates record against the JSON Schema."""
        errors = []
        for err in self.validator.iter_errors(opp):
            field_path = ".".join(str(p) for p in err.path) or "root"
            errors.append(ValidationErrorItem(field=field_path, message=err.message, severity="ERROR"))
        return errors

    def validate_dates(self, opp: Dict[str, Any]) -> List[ValidationErrorItem]:
        """Validates date formats, chronological logic, and application period."""
        issues = []
        app_period = opp.get("application_period", {})
        open_date_str = app_period.get("opening_date")
        deadline_str = app_period.get("deadline")
        status = app_period.get("status")

        open_dt = None
        dead_dt = None

        if open_date_str:
            try:
                open_dt = datetime.strptime(open_date_str, "%Y-%m-%d")
            except ValueError:
                issues.append(ValidationErrorItem("application_period.opening_date", f"Invalid date format '{open_date_str}', expected YYYY-MM-DD", "ERROR"))

        if deadline_str:
            try:
                dead_dt = datetime.strptime(deadline_str, "%Y-%m-%d")
            except ValueError:
                issues.append(ValidationErrorItem("application_period.deadline", f"Invalid deadline format '{deadline_str}', expected YYYY-MM-DD", "ERROR"))

        if open_dt and dead_dt and open_dt > dead_dt:
            issues.append(ValidationErrorItem("application_period", f"Opening date {open_date_str} is after deadline {deadline_str}", "ERROR"))

        if status == "open" and not deadline_str and not app_period.get("notes"):
            issues.append(ValidationErrorItem("application_period", "Application status is 'open' but deadline is null without explanation in notes", "WARNING"))

        return issues

    def validate_urls(self, opp: Dict[str, Any]) -> List[ValidationErrorItem]:
        """Validates syntax and schemes for official and application URLs."""
        issues = []
        official_urls = opp.get("official_source_urls", [])
        if not official_urls:
            issues.append(ValidationErrorItem("official_source_urls", "At least one official source URL is required", "ERROR"))

        for idx, u in enumerate(official_urls):
            parsed = urlparse(u)
            if not parsed.scheme or parsed.scheme not in ["http", "https", "file"]:
                issues.append(ValidationErrorItem(f"official_source_urls[{idx}]", f"Invalid URL or unsupported scheme: '{u}'", "ERROR"))
            if not parsed.netloc and parsed.scheme in ["http", "https"]:
                issues.append(ValidationErrorItem(f"official_source_urls[{idx}]", f"Missing domain in URL: '{u}'", "ERROR"))

        app_url = opp.get("application_url")
        if app_url:
            parsed_app = urlparse(app_url)
            if not parsed_app.scheme or parsed_app.scheme not in ["http", "https"]:
                issues.append(ValidationErrorItem("application_url", f"Invalid application URL scheme: '{app_url}'", "ERROR"))

        return issues

    def validate_criteria_and_operators(self, opp: Dict[str, Any]) -> List[ValidationErrorItem]:
        """Validates eligibility criteria operators, value types, and logical consistency."""
        issues = []
        criteria = opp.get("eligibility_criteria", [])
        seen_crit_ids: Set[str] = set()

        for idx, c in enumerate(criteria):
            c_id = c.get("criterion_id", f"crit_{idx}")
            if c_id in seen_crit_ids:
                issues.append(ValidationErrorItem(f"eligibility_criteria[{idx}].criterion_id", f"Duplicate criterion_id '{c_id}' within opportunity", "ERROR"))
            seen_crit_ids.add(c_id)

            op = c.get("operator")
            if op not in ALLOWED_OPERATORS:
                issues.append(ValidationErrorItem(f"eligibility_criteria[{idx}].operator", f"Unsupported operator '{op}'. Allowed: {sorted(list(ALLOWED_OPERATORS))}", "ERROR"))

            field_name = c.get("field", "")
            val = c.get("value")
            unit = c.get("unit")

            # Check numeric value & unit consistency
            if field_name == "annual_family_income":
                if op in ["less_than", "less_than_or_equal", "equals", "greater_than"]:
                    if not isinstance(val, (int, float)) or val < 0:
                        issues.append(ValidationErrorItem(f"eligibility_criteria[{idx}].value", f"Income threshold must be a non-negative number, got {val}", "ERROR"))
                    if unit != "INR/year":
                        issues.append(ValidationErrorItem(f"eligibility_criteria[{idx}].unit", f"Expected unit 'INR/year' for annual_family_income, got '{unit}'", "WARNING"))

            if field_name == "min_marks_percentage":
                if isinstance(val, (int, float)):
                    if val < 0 or val > 100:
                        issues.append(ValidationErrorItem(f"eligibility_criteria[{idx}].value", f"Percentage marks must be between 0 and 100, got {val}", "ERROR"))

            if op == "between":
                if not isinstance(val, list) or len(val) != 2 or val[0] > val[1]:
                    issues.append(ValidationErrorItem(f"eligibility_criteria[{idx}].value", f"Operator 'between' requires a 2-element array [min, max] where min <= max", "ERROR"))

            if op in ["in", "not_in"] and not isinstance(val, list):
                issues.append(ValidationErrorItem(f"eligibility_criteria[{idx}].value", f"Operator '{op}' requires a list value", "ERROR"))

        return issues

    def validate_verification_integrity(self, opp: Dict[str, Any]) -> List[ValidationErrorItem]:
        """
        Enforces state machine rules and anti-hallucination standards.
        A record marked 'verified' MUST have confirmed review status and no unresolved evidence gaps.
        """
        issues = []
        status = opp.get("verification_status")
        if status not in VALID_STATUSES:
            issues.append(ValidationErrorItem("verification_status", f"Invalid verification_status '{status}'", "ERROR"))

        # Rule: A record cannot be 'verified' without human review sign-off
        if status == "verified":
            evidence_items = opp.get("evidence", [])
            has_pending = any(ev.get("review_status") == "pending_review" for ev in evidence_items)
            if has_pending:
                issues.append(ValidationErrorItem("verification_status", "Record marked 'verified' but contains evidence with 'pending_review' status", "ERROR"))

            review_notes = opp.get("review_notes", [])
            if not review_notes:
                issues.append(ValidationErrorItem("verification_status", "Record marked 'verified' without documented human review in review_notes", "ERROR"))

            # Check if all mandatory criteria have verified evidence
            for c in opp.get("eligibility_criteria", []):
                if c.get("required") and c.get("review_status") != "confirmed":
                    issues.append(ValidationErrorItem("eligibility_criteria", f"Mandatory criterion '{c.get('criterion_id')}' is not confirmed, but record is marked verified", "ERROR"))

        return issues

    def validate_opportunity(self, opp: Dict[str, Any], full_source_text: Optional[str] = None) -> Dict[str, Any]:
        """Full deterministic audit of an opportunity record."""
        issues: List[ValidationErrorItem] = []

        # 1. Schema check
        issues.extend(self.validate_schema(opp))

        # 2. Date checks
        issues.extend(self.validate_dates(opp))

        # 3. URL checks
        issues.extend(self.validate_urls(opp))

        # 4. Criteria & operator checks
        issues.extend(self.validate_criteria_and_operators(opp))

        # 5. Evidence audit
        ev_errors, ev_warnings = audit_opportunity_evidence(opp, full_source_text)
        for e in ev_errors:
            issues.append(ValidationErrorItem("evidence", e, "ERROR"))
        for w in ev_warnings:
            issues.append(ValidationErrorItem("evidence", w, "WARNING"))

        # 6. Verification integrity
        issues.extend(self.validate_verification_integrity(opp))

        # Compile report
        errors = [item.to_dict() for item in issues if item.severity == "ERROR"]
        warnings = [item.to_dict() for item in issues if item.severity == "WARNING"]

        is_valid = len(errors) == 0
        needs_human_review = len(warnings) > 0 or opp.get("verification_status") in ["draft", "needs_review"]

        return {
            "opportunity_id": opp.get("opportunity_id", "unknown"),
            "name": opp.get("name", "Unknown"),
            "verification_status": opp.get("verification_status", "draft"),
            "is_valid": is_valid,
            "needs_human_review": needs_human_review,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
        }


def validate_dataset(
    opportunities: List[Dict[str, Any]],
    schema_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Validates an entire dataset of opportunities, checking individual records
    and dataset-wide uniqueness constraints.
    """
    validator = OpportunityValidator(schema_path)
    results = []
    seen_ids: Dict[str, str] = {}
    valid_count = 0
    invalid_count = 0
    needs_review_count = 0
    total_errors = 0
    total_warnings = 0

    for opp in opportunities:
        res = validator.validate_opportunity(opp)
        opp_id = opp.get("opportunity_id", "")

        # Dataset-level unique ID check
        if opp_id in seen_ids:
            res["is_valid"] = False
            res["error_count"] += 1
            res["errors"].append({
                "field": "opportunity_id",
                "message": f"Duplicate opportunity_id '{opp_id}' found across dataset (first seen in scheme '{seen_ids[opp_id]}')",
                "severity": "ERROR",
            })
        else:
            seen_ids[opp_id] = opp.get("name", "")

        if res["is_valid"]:
            valid_count += 1
        else:
            invalid_count += 1

        if res["needs_human_review"]:
            needs_review_count += 1

        total_errors += res["error_count"]
        total_warnings += res["warning_count"]
        results.append(res)

    return {
        "total_records_processed": len(opportunities),
        "valid_records": valid_count,
        "invalid_records": invalid_count,
        "records_requiring_human_review": needs_review_count,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "record_results": results,
    }
