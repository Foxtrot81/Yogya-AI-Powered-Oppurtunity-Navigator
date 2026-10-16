"""
PostgreSQL database layer and importer for Yogya Opportunities.
Performs transactional imports with upsert handling, protects verified records from
accidental unreviewed overwrites, and supports robust dry-run simulation when offline.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from src.config import config
from src.validation import OpportunityValidator

logger = logging.getLogger(__name__)


class DatabaseImporter:
    def __init__(self, database_url: Optional[str] = None):
        self.db_url = database_url or config.database_url
        self.validator = OpportunityValidator()

    def import_records(
        self,
        opportunities: List[Dict[str, Any]],
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Imports validated opportunity records into PostgreSQL.
        If dry_run is True or DB connection is unconfigured, executes simulation.
        """
        report: Dict[str, Any] = {
            "total_submitted": len(opportunities),
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "failed": 0,
            "details": [],
            "mode": "dry_run" if (dry_run or not self.db_url) else "live_database",
        }

        # If dry run or no connection URL configured, execute full offline validation and SQL generation
        if dry_run or not self.db_url:
            return self._simulate_import(opportunities, report)

        # Attempt live PostgreSQL import via psycopg/psycopg2
        try:
            import psycopg
            conn = psycopg.connect(self.db_url)
        except ImportError:
            try:
                import psycopg2
                conn = psycopg2.connect(self.db_url)
            except ImportError:
                report["mode"] = "dry_run (psycopg/psycopg2 not installed)"
                return self._simulate_import(opportunities, report)
        except Exception as e:
            report["mode"] = f"dry_run (connection failed: {str(e)})"
            return self._simulate_import(opportunities, report)

        # Live transaction
        try:
            with conn:
                with conn.cursor() as cur:
                    for opp in opportunities:
                        self._process_single_record_live(cur, opp, report)
        except Exception as e:
            logger.error(f"Live database transaction failed: {e}")
            report["failed"] += len(opportunities) - (report["inserted"] + report["updated"] + report["skipped"])
            report["error"] = str(e)
        finally:
            conn.close()

        return report

    def _simulate_import(
        self,
        opportunities: List[Dict[str, Any]],
        report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validates records and simulates parameterized SQL upserts."""
        simulated_existing_records: Dict[str, str] = {}  # id -> verification_status

        for opp in opportunities:
            opp_id = opp.get("opportunity_id", "unspecified")
            val_res = self.validator.validate_opportunity(opp)

            if not val_res["is_valid"]:
                report["failed"] += 1
                report["details"].append({
                    "opportunity_id": opp_id,
                    "action": "failed",
                    "reason": f"Validation failed with {val_res['error_count']} errors",
                    "errors": val_res["errors"],
                })
                continue

            incoming_status = opp.get("verification_status", "draft")
            existing_status = simulated_existing_records.get(opp_id)

            if existing_status == "verified" and incoming_status in ["draft", "needs_review"]:
                # Safety rule: Protect verified record from unreviewed overwrite
                report["skipped"] += 1
                report["details"].append({
                    "opportunity_id": opp_id,
                    "action": "skipped",
                    "reason": "Existing record is verified; incoming unreviewed draft cannot overwrite it.",
                })
                continue

            if opp_id in simulated_existing_records:
                report["updated"] += 1
                report["details"].append({
                    "opportunity_id": opp_id,
                    "action": "updated",
                    "reason": "Record updated safely.",
                })
            else:
                report["inserted"] += 1
                report["details"].append({
                    "opportunity_id": opp_id,
                    "action": "inserted",
                    "reason": "New record inserted successfully.",
                })

            simulated_existing_records[opp_id] = incoming_status

        return report

    def _process_single_record_live(
        self,
        cur: Any,
        opp: Dict[str, Any],
        report: Dict[str, Any],
    ) -> None:
        """Executes parameterized SQL statements for live PostgreSQL."""
        opp_id = opp.get("opportunity_id", "")
        val_res = self.validator.validate_opportunity(opp)
        if not val_res["is_valid"]:
            report["failed"] += 1
            report["details"].append({
                "opportunity_id": opp_id,
                "action": "failed",
                "reason": "Validation errors",
                "errors": val_res["errors"],
            })
            return

        # Check existing status in DB
        cur.execute("SELECT verification_status FROM opportunities WHERE opportunity_id = %s", (opp_id,))
        row = cur.fetchone()

        incoming_status = opp.get("verification_status", "draft")
        if row:
            existing_status = row[0]
            if existing_status == "verified" and incoming_status in ["draft", "needs_review"]:
                report["skipped"] += 1
                report["details"].append({
                    "opportunity_id": opp_id,
                    "action": "skipped",
                    "reason": "Existing DB record is verified; incoming draft skipped.",
                })
                return

        # Upsert opportunity record
        benefits = opp.get("benefits", {})
        app_period = opp.get("application_period", {})
        geo = opp.get("geographic_scope", {})

        upsert_query = """
            INSERT INTO opportunities (
                opportunity_id, schema_version, name, category, provider, description,
                education_levels, geographic_scope, benefit_type, benefit_financial_amount,
                benefit_currency, benefit_frequency, benefit_description, non_financial_benefits,
                application_status, application_opening_date, application_deadline, academic_year,
                status_verification_date, official_source_urls, application_url, verification_status,
                synthetic, last_checked_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, NOW()
            )
            ON CONFLICT (opportunity_id) DO UPDATE SET
                name = EXCLUDED.name,
                category = EXCLUDED.category,
                provider = EXCLUDED.provider,
                description = EXCLUDED.description,
                education_levels = EXCLUDED.education_levels,
                geographic_scope = EXCLUDED.geographic_scope,
                benefit_type = EXCLUDED.benefit_type,
                benefit_financial_amount = EXCLUDED.benefit_financial_amount,
                benefit_currency = EXCLUDED.benefit_currency,
                benefit_frequency = EXCLUDED.benefit_frequency,
                benefit_description = EXCLUDED.benefit_description,
                non_financial_benefits = EXCLUDED.non_financial_benefits,
                application_status = EXCLUDED.application_status,
                application_opening_date = EXCLUDED.application_opening_date,
                application_deadline = EXCLUDED.application_deadline,
                academic_year = EXCLUDED.academic_year,
                status_verification_date = EXCLUDED.status_verification_date,
                official_source_urls = EXCLUDED.official_source_urls,
                application_url = EXCLUDED.application_url,
                verification_status = EXCLUDED.verification_status,
                synthetic = EXCLUDED.synthetic,
                last_checked_at = EXCLUDED.last_checked_at,
                updated_at = NOW();
        """

        cur.execute(
            upsert_query,
            (
                opp_id,
                opp.get("schema_version", "1.0.0"),
                opp.get("name"),
                opp.get("category"),
                opp.get("provider"),
                opp.get("description"),
                json.dumps(opp.get("education_levels", [])),
                json.dumps(geo),
                benefits.get("type"),
                benefits.get("financial_amount"),
                benefits.get("currency", "INR"),
                benefits.get("frequency"),
                benefits.get("description"),
                json.dumps(benefits.get("non_financial_benefits", [])),
                opp.get("application_status", app_period.get("status", "unknown")),
                app_period.get("opening_date"),
                app_period.get("deadline"),
                app_period.get("academic_year"),
                app_period.get("status_verification_date"),
                json.dumps(opp.get("official_source_urls", [])),
                opp.get("application_url"),
                incoming_status,
                opp.get("synthetic", False),
                opp.get("last_checked_at"),
            ),
        )

        # Replace child criteria
        cur.execute("DELETE FROM eligibility_criteria WHERE opportunity_id = %s", (opp_id,))
        for c in opp.get("eligibility_criteria", []):
            cur.execute(
                """
                INSERT INTO eligibility_criteria (
                    criterion_id, opportunity_id, field, operator, value, unit,
                    condition_type, required, evidence_reference, review_status, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    c.get("criterion_id"),
                    opp_id,
                    c.get("field"),
                    c.get("operator"),
                    json.dumps(c.get("value")),
                    c.get("unit"),
                    c.get("condition_type", "mandatory"),
                    c.get("required", True),
                    c.get("evidence_reference"),
                    c.get("review_status", "unreviewed"),
                    c.get("notes"),
                ),
            )

        # Replace child documents
        cur.execute("DELETE FROM required_documents WHERE opportunity_id = %s", (opp_id,))
        for doc in opp.get("required_documents", []):
            cur.execute(
                """
                INSERT INTO required_documents (
                    opportunity_id, document_name, document_type, mandatory, description, evidence_reference
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    opp_id,
                    doc.get("document_name"),
                    doc.get("document_type"),
                    doc.get("mandatory", True),
                    doc.get("description"),
                    doc.get("evidence_reference"),
                ),
            )

        # Replace child evidence
        cur.execute("DELETE FROM evidence_records WHERE opportunity_id = %s", (opp_id,))
        for ev in opp.get("evidence", []):
            cur.execute(
                """
                INSERT INTO evidence_records (
                    evidence_id, opportunity_id, field_path, source_url, source_title,
                    supporting_excerpt, page_number, section_heading, retrieved_at,
                    extraction_method, review_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    ev.get("evidence_id"),
                    opp_id,
                    ev.get("field_path"),
                    ev.get("source_url"),
                    ev.get("source_title"),
                    ev.get("supporting_excerpt"),
                    ev.get("page_number"),
                    ev.get("section_heading"),
                    ev.get("retrieved_at"),
                    ev.get("extraction_method"),
                    ev.get("review_status", "pending_review"),
                ),
            )

        if row:
            report["updated"] += 1
            action = "updated"
        else:
            report["inserted"] += 1
            action = "inserted"

        report["details"].append({"opportunity_id": opp_id, "action": action, "reason": "Success"})
