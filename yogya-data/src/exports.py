"""
Dataset export engine.
Produces clean JSON and CSV distributions filtered by verification status
(drafts, review_queue, reviewed, verified) and full flattened datasets for spreadsheet analysis.
"""

import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import config

logger = logging.getLogger(__name__)


class OpportunityExporter:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or config.processed_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_all(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Path]:
        """
        Exports the dataset into partitioned JSON and CSV files according to status.
        """
        status_buckets: Dict[str, List[Dict[str, Any]]] = {
            "all": opportunities,
            "drafts": [],
            "needs_review": [],
            "reviewed": [],
            "verified": [],
        }

        status_map = {
            "draft": "drafts",
            "drafts": "drafts",
            "needs_review": "needs_review",
            "review_queue": "needs_review",
            "reviewed": "reviewed",
            "verified": "verified",
        }

        for opp in opportunities:
            st = opp.get("verification_status", "draft")
            bucket = status_map.get(st, "drafts")
            status_buckets[bucket].append(opp)

        exported_paths: Dict[str, Path] = {}

        # Export JSONs
        for bucket_name, bucket_items in status_buckets.items():
            json_file = self.output_dir / f"opportunities_{bucket_name}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(bucket_items, f, indent=2, ensure_ascii=False)
            exported_paths[f"{bucket_name}_json"] = json_file

            # Export corresponding CSV
            csv_file = self.output_dir / f"opportunities_{bucket_name}.csv"
            self._export_to_csv(bucket_items, csv_file)
            exported_paths[f"{bucket_name}_csv"] = csv_file

        return exported_paths

    def _export_to_csv(self, opportunities: List[Dict[str, Any]], target_file: Path) -> None:
        """Flattens nested opportunity records into a tabular CSV format."""
        fieldnames = [
            "opportunity_id",
            "name",
            "category",
            "provider",
            "description",
            "education_levels",
            "geographic_scope_type",
            "benefit_type",
            "financial_amount",
            "currency",
            "benefit_frequency",
            "application_status",
            "application_opening_date",
            "application_deadline",
            "academic_year",
            "official_source_urls",
            "application_url",
            "eligibility_summary",
            "required_documents_summary",
            "verification_status",
            "last_checked_at",
            "synthetic",
        ]

        with open(target_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for opp in opportunities:
                # Compile eligibility summary
                crit_summaries = []
                for c in opp.get("eligibility_criteria", []):
                    crit_summaries.append(f"{c.get('field')} {c.get('operator')} {c.get('value')}")
                elig_str = "; ".join(crit_summaries)

                # Compile documents summary
                doc_summaries = [d.get("document_name", "") for d in opp.get("required_documents", [])]
                doc_str = "; ".join(doc_summaries)

                benefits = opp.get("benefits", {})
                app_period = opp.get("application_period", {})
                geo = opp.get("geographic_scope", {})

                row = {
                    "opportunity_id": opp.get("opportunity_id", ""),
                    "name": opp.get("name", ""),
                    "category": opp.get("category", ""),
                    "provider": opp.get("provider", ""),
                    "description": opp.get("description", "").replace("\n", " "),
                    "education_levels": ", ".join(opp.get("education_levels", [])),
                    "geographic_scope_type": geo.get("type", "national"),
                    "benefit_type": benefits.get("type", ""),
                    "financial_amount": benefits.get("financial_amount"),
                    "currency": benefits.get("currency", "INR"),
                    "benefit_frequency": benefits.get("frequency", ""),
                    "application_status": opp.get("application_status", app_period.get("status", "unknown")),
                    "application_opening_date": app_period.get("opening_date", ""),
                    "application_deadline": app_period.get("deadline", ""),
                    "academic_year": app_period.get("academic_year", ""),
                    "official_source_urls": " | ".join(opp.get("official_source_urls", [])),
                    "application_url": opp.get("application_url", ""),
                    "eligibility_summary": elig_str,
                    "required_documents_summary": doc_str,
                    "verification_status": opp.get("verification_status", "draft"),
                    "last_checked_at": opp.get("last_checked_at", ""),
                    "synthetic": opp.get("synthetic", False),
                }
                writer.writerow(row)
