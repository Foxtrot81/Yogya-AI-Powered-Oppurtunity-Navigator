"""
Human-in-the-loop review workflow, state machine transition enforcement,
and review queue management.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.config import config
from src.validation import OpportunityValidator

logger = logging.getLogger(__name__)

ALLOWED_TRANSITIONS = {
    "draft": ["needs_review", "rejected"],
    "needs_review": ["reviewed", "rejected", "draft"],
    "reviewed": ["verified", "needs_review", "rejected"],
    "verified": ["stale", "needs_review"],
    "stale": ["needs_review", "draft", "verified"],
    "rejected": ["draft", "needs_review"],
}


class ReviewWorkflowError(Exception):
    """Raised when an illegal review state transition or unverified promotion is attempted."""
    pass


class ReviewManager:
    def __init__(
        self,
        drafts_dir: Optional[Path] = None,
        queue_dir: Optional[Path] = None,
        processed_dir: Optional[Path] = None,
    ):
        self.drafts_dir = drafts_dir or config.drafts_dir
        self.queue_dir = queue_dir or config.review_queue_dir
        self.processed_dir = processed_dir or config.processed_dir
        self.validator = OpportunityValidator()

    def build_review_queue(self) -> List[Dict[str, Any]]:
        """
        Scans drafts and populates the review queue with records requiring human intervention.
        """
        queue_records = []
        for draft_file in self.drafts_dir.glob("*.json"):
            with open(draft_file, "r", encoding="utf-8") as f:
                record = json.load(f)

            audit_res = self.validator.validate_opportunity(record)
            status = record.get("verification_status", "draft")

            # Place in review queue if in draft or needs_review, or if it has validation warnings
            if status in ["draft", "needs_review"] or audit_res["needs_human_review"]:
                if status == "draft":
                    # Transition draft -> needs_review
                    record["verification_status"] = "needs_review"
                    record.setdefault("review_notes", []).append(
                        f"Placed into review queue on {datetime.now(timezone.utc).isoformat()}"
                    )

                # Write into review_queue
                q_file = self.queue_dir / draft_file.name
                with open(q_file, "w", encoding="utf-8") as f:
                    json.dump(record, f, indent=2, ensure_ascii=False)

                queue_records.append(record)

        return queue_records

    def apply_transition(
        self,
        record: Dict[str, Any],
        new_status: str,
        reviewer_id: str,
        notes: str,
    ) -> Dict[str, Any]:
        """
        Applies a state machine transition with validation checks.
        Prevents transitioning to 'verified' without human confirmation and valid evidence.
        """
        current_status = record.get("verification_status", "draft")
        allowed_next = ALLOWED_TRANSITIONS.get(current_status, [])

        if new_status not in allowed_next and current_status != new_status:
            raise ReviewWorkflowError(
                f"Illegal transition from '{current_status}' to '{new_status}'. Allowed next states: {allowed_next}"
            )

        now_iso = datetime.now(timezone.utc).isoformat()
        audit_note = f"[{now_iso}] Status changed from '{current_status}' to '{new_status}' by {reviewer_id}: {notes}"

        if new_status == "verified":
            # Strict verification check
            audit_res = self.validator.validate_opportunity(record)
            if not audit_res["is_valid"]:
                err_msg = "; ".join([e["message"] for e in audit_res["errors"]])
                raise ReviewWorkflowError(f"Cannot verify record '{record.get('opportunity_id')}': validation errors exist: {err_msg}")

            # Confirm all criteria
            for c in record.get("eligibility_criteria", []):
                c["review_status"] = "confirmed"

            # Confirm all evidence items
            for ev in record.get("evidence", []):
                ev["review_status"] = "verified"

        record["verification_status"] = new_status
        record["last_checked_at"] = now_iso
        record.setdefault("review_notes", []).append(audit_note)

        # Save record in appropriate location
        opp_id = record.get("opportunity_id", "unnamed")
        target_dir = self.processed_dir if new_status == "verified" else self.queue_dir
        dest_path = target_dir / f"{opp_id}.json"

        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

        return record
