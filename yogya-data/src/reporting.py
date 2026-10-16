"""
Validation and pipeline execution reporting engine.
Generates structured JSON and comprehensive GitHub-flavored Markdown reports
documenting dataset quality, source provenance, verification states, and research gaps.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import config

logger = logging.getLogger(__name__)


class ReportGenerator:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or config.reports_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_summary_report(
        self,
        validation_results: Dict[str, Any],
        duplicate_candidates: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]],
        ingestion_metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Path]:
        """
        Creates both machine-readable JSON and human-readable Markdown summary reports.
        """
        now_iso = datetime.now(timezone.utc).isoformat()

        # Breakdown verification statuses
        status_counts: Dict[str, int] = {}
        category_counts: Dict[str, int] = {}
        for opp in opportunities:
            st = opp.get("verification_status", "unknown")
            status_counts[st] = status_counts.get(st, 0) + 1

            cat = opp.get("category", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        report_data = {
            "timestamp": now_iso,
            "project": "Yogya Opportunity Data Pipeline",
            "metrics": {
                "total_opportunities": len(opportunities),
                "valid_records": validation_results.get("valid_records", 0),
                "invalid_records": validation_results.get("invalid_records", 0),
                "records_requiring_human_review": validation_results.get("records_requiring_human_review", 0),
                "duplicate_candidate_pairs": len(duplicate_candidates),
                "status_distribution": status_counts,
                "category_distribution": category_counts,
                "total_validation_errors": validation_results.get("total_errors", 0),
                "total_validation_warnings": validation_results.get("total_warnings", 0),
            },
            "ingestion_sources_count": len(ingestion_metadata or []),
            "validation_summary": validation_results,
            "duplicate_candidates": duplicate_candidates,
        }

        # 1. Write JSON report
        json_file = self.output_dir / "summary_report.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        # 2. Write Markdown report
        md_file = self.output_dir / "summary_report.md"
        md_content = self._render_markdown_report(report_data, opportunities)
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        return {"json": json_file, "markdown": md_file}

    def _render_markdown_report(
        self,
        report_data: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
    ) -> str:
        metrics = report_data["metrics"]
        lines = []
        lines.append("# Yogya Opportunity Data Pipeline — Summary & Audit Report")
        lines.append(f"\n**Generated at:** `{report_data['timestamp']}`  ")
        lines.append("**Target Audience:** Rural Indian Students (Classes 9–12, Vocational Training, Apprenticeships)\n")

        lines.append("## 1. Executive Summary")
        lines.append(f"- **Total Opportunities Processed:** `{metrics['total_opportunities']}`")
        lines.append(f"- **Schema-Valid Records:** `{metrics['valid_records']}`")
        lines.append(f"- **Invalid Records (Requiring Corrections):** `{metrics['invalid_records']}`")
        lines.append(f"- **Records Requiring Human Review:** `{metrics['records_requiring_human_review']}`")
        lines.append(f"- **Potential Duplicate Candidates:** `{metrics['duplicate_candidate_pairs']}`")
        lines.append(f"- **Total Validation Errors:** `{metrics['total_validation_errors']}`")
        lines.append(f"- **Total Validation Warnings:** `{metrics['total_validation_warnings']}`\n")

        lines.append("### Verification Status Breakdown")
        lines.append("| Status | Count | Description |")
        lines.append("| :--- | :--- | :--- |")
        for st, count in metrics["status_distribution"].items():
            lines.append(f"| `{st}` | **{count}** | {'Verified by human reviewer with evidence' if st == 'verified' else 'AI/Rule extraction draft pending review'} |")

        lines.append("\n### Category Breakdown")
        lines.append("| Category | Count |")
        lines.append("| :--- | :--- |")
        for cat, count in metrics["category_distribution"].items():
            lines.append(f"| `{cat}` | {count} |")

        lines.append("\n## 2. Ingested Schemes Roster")
        lines.append("| ID | Scheme Name | Category | Provider | Status | Deadline |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for opp in opportunities:
            opp_id = opp.get("opportunity_id", "")
            name = opp.get("name", "")[:45]
            cat = opp.get("category", "")
            prov = opp.get("provider", "")[:30]
            st = opp.get("verification_status", "")
            dl = opp.get("application_period", {}).get("deadline") or "Unknown / Closed"
            lines.append(f"| `{opp_id}` | {name} | {cat} | {prov} | `{st}` | {dl} |")

        lines.append("\n## 3. Duplicate Candidates Audit")
        dups = report_data.get("duplicate_candidates", [])
        if not dups:
            lines.append("No duplicate candidate pairs identified exceeding similarity thresholds.")
        else:
            lines.append("| Scheme A | Scheme B | Confidence | Reasons | Recommendation |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for d in dups:
                lines.append(
                    f"| `{d['opportunity_id_a']}` | `{d['opportunity_id_b']}` | `{d['confidence_score']}` | {'; '.join(d['reasons'])} | {d['recommended_action']} |"
                )

        lines.append("\n## 4. Evidence & Traceability Audit")
        lines.append("Every extracted official fact must have an exact excerpt verified from official government sources:")
        lines.append("- National Scholarship Portal: `https://scholarships.gov.in/`")
        lines.append("- Skill India Digital Hub: `https://www.skillindiadigital.gov.in/`")
        lines.append("- Bharat Skills: `https://www.bharatskill.gov.in/`")
        lines.append("- Ministry of Education (DSEL): `https://dsel.education.gov.in/`")
        lines.append("- Ministry of Social Justice & Empowerment: `https://socialjustice.gov.in/`\n")

        lines.append("## 5. Integration Contracts for Persons 2 & 3")
        lines.append("- **Backend Developer:** Review `docs/API_CONTRACT.md` and `sql/schema.sql`. Import using `scripts/import_postgres.py`.")
        lines.append("- **Eligibility Engine Developer:** Filter records using `verification_status == 'verified'`. Structured operators in `eligibility_criteria` support deterministic boolean evaluation.")

        return "\n".join(lines)
