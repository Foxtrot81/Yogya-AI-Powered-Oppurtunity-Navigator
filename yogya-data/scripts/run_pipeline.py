#!/usr/bin/env python3
"""
Master orchestrator script for the Yogya Opportunity Data Pipeline.
Executes source ingestion, extraction, validation, deduplication, review queue building,
partitioned exports, database staging, and research reporting end-to-end.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import config
from src.source_ingestion import SourceIngestion
from src.extraction import get_extractor, extract_opportunities_from_raw
from src.validation import validate_dataset
from src.deduplication import detect_duplicate_candidates
from src.review import ReviewManager
from src.exports import OpportunityExporter
from src.database import DatabaseImporter
from src.reporting import ReportGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("yogya_pipeline")


def run_pipeline(
    source_url: str = None,
    source_file: str = None,
    provider: str = None,
    dry_run: bool = False,
    run_db_import: bool = False,
) -> int:
    logger.info(">>> Starting Yogya Opportunity Data Pipeline execution <<<")

    # Step 1: Ingestion
    ingestor = SourceIngestion()
    ingested_meta_list = []

    if source_url:
        logger.info(f"Ingesting supplied URL: {source_url}")
        meta = ingestor.ingest_url(source_url)
        ingested_meta_list.append(meta)
    elif source_file:
        file_path = Path(source_file).resolve()
        logger.info(f"Ingesting supplied file: {file_path}")
        if file_path.suffix.lower() == ".pdf":
            meta = ingestor.ingest_pdf(file_path)
        else:
            meta = ingestor.ingest_text_file(file_path)
        ingested_meta_list.append(meta)
    else:
        # Load any existing raw sources
        raw_files = list(config.raw_dir.glob("*.json"))
        logger.info(f"Using {len(raw_files)} existing raw source(s) in {config.raw_dir}")
        for rf in raw_files:
            try:
                with open(rf, "r", encoding="utf-8") as f:
                    ingested_meta_list.append(json.load(f))
            except Exception as e:
                logger.warning(f"Could not read raw file {rf}: {e}")

    # Step 2: Extraction
    raw_files = list(config.raw_dir.glob("*.json"))
    extractor = get_extractor(provider)
    logger.info(f"Extracting opportunities with engine: {extractor.__class__.__name__}")
    
    extracted_opps = []
    for rf in raw_files:
        try:
            opps = extract_opportunities_from_raw(rf, extractor=extractor)
            extracted_opps.extend(opps)
        except Exception as e:
            logger.error(f"Extraction failed on {rf}: {e}")

    # Load all drafts
    all_drafts = []
    for df in config.drafts_dir.glob("*.json"):
        try:
            with open(df, "r", encoding="utf-8") as f:
                all_drafts.append(json.load(f))
        except Exception as e:
            logger.error(f"Error loading draft {df}: {e}")

    logger.info(f"Loaded {len(all_drafts)} total candidate draft(s) for validation.")

    # Step 3: Validation
    logger.info("Executing deterministic schema, date, URL, and evidence validation...")
    validation_results = validate_dataset(all_drafts)
    logger.info(
        f"Validation completed: {validation_results['valid_records']} valid, "
        f"{validation_results['invalid_records']} invalid, "
        f"{validation_results['records_requiring_human_review']} requiring human review."
    )

    # Step 4: Duplicate Detection
    logger.info("Executing deduplication analysis...")
    duplicate_candidates = detect_duplicate_candidates(all_drafts)
    logger.info(f"Found {len(duplicate_candidates)} duplicate candidate pair(s).")

    # Step 5: Review Queue
    logger.info("Populating review queue for human-in-the-loop audit...")
    review_mgr = ReviewManager()
    queue_records = review_mgr.build_review_queue()
    logger.info(f"Review queue updated with {len(queue_records)} record(s).")

    # Step 6: Exports
    logger.info("Exporting partitioned JSON and CSV distributions...")
    exporter = OpportunityExporter()
    exported_files = exporter.export_all(all_drafts)
    for k, p in exported_files.items():
        logger.info(f"  Exported -> {p.name}")

    # Step 7: Database Staging / Import
    if run_db_import:
        logger.info("Staging opportunities to PostgreSQL...")
        importer = DatabaseImporter()
        db_report = importer.import_records(all_drafts, dry_run=dry_run)
        logger.info(
            f"Database Import ({db_report['mode']}): "
            f"Inserted={db_report['inserted']}, Updated={db_report['updated']}, "
            f"Skipped={db_report['skipped']}, Failed={db_report['failed']}"
        )

    # Step 8: Reporting
    logger.info("Generating comprehensive research and validation audit report...")
    reporter = ReportGenerator()
    reports = reporter.generate_summary_report(
        validation_results=validation_results,
        duplicate_candidates=duplicate_candidates,
        opportunities=all_drafts,
        ingestion_metadata=ingested_meta_list,
    )
    logger.info(f"Summary Report Markdown: {reports['markdown']}")
    logger.info(f"Summary Report JSON:     {reports['json']}")

    logger.info(">>> Yogya Opportunity Pipeline execution finished successfully <<<")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Run complete Yogya opportunity pipeline end-to-end.")
    parser.add_argument("--source-url", type=str, default=None, help="Ingest a specific URL before pipeline run")
    parser.add_argument("--source-file", type=str, default=None, help="Ingest a specific PDF/HTML/text file before pipeline run")
    parser.add_argument("--provider", type=str, default=None, choices=["gemini", "openai", "fallback", "none"], help="LLM extraction provider override")
    parser.add_argument("--dry-run", action="store_true", help="Simulate DB import and API calls")
    parser.add_argument("--db-import", action="store_true", help="Execute PostgreSQL database import")

    args = parser.parse_args()
    code = run_pipeline(
        source_url=args.source_url,
        source_file=args.source_file,
        provider=args.provider,
        dry_run=args.dry_run,
        run_db_import=args.db_import,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
