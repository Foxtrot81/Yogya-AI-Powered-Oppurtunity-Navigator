#!/usr/bin/env python3
"""
CLI script to import validated opportunity records into PostgreSQL backend.
Supports safe dry-run simulation when database or drivers are unconfigured.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import DatabaseImporter
from src.config import config


def main():
    parser = argparse.ArgumentParser(description="Import opportunities into PostgreSQL database.")
    parser.add_argument("--input", type=str, default=None, help="Directory or JSON file with opportunities (defaults to data/processed/opportunities_verified.json or data/drafts/)")
    parser.add_argument("--database-url", type=str, default=None, help="PostgreSQL connection string override")
    parser.add_argument("--dry-run", action="store_true", help="Execute offline dry-run simulation without modifying database")

    args = parser.parse_args()
    
    # Determine input path
    input_path = None
    if args.input:
        input_path = Path(args.input).resolve()
    else:
        verified_file = config.processed_dir / "opportunities_verified.json"
        if verified_file.exists():
            input_path = verified_file
        else:
            input_path = config.drafts_dir

    opportunities = []
    if input_path.is_file():
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                opportunities.extend(data)
            else:
                opportunities.append(data)
    elif input_path.is_dir():
        for f in input_path.glob("*.json"):
            with open(f, "r", encoding="utf-8") as jf:
                data = json.load(jf)
                if isinstance(data, list):
                    opportunities.extend(data)
                else:
                    opportunities.append(data)

    print(f"[*] Initializing PostgreSQL importer (Input records: {len(opportunities)})...")
    importer = DatabaseImporter(database_url=args.database_url)
    report = importer.import_records(opportunities, dry_run=args.dry_run)

    print("\n================ DATABASE IMPORT REPORT ================")
    print(f"Mode:                 {report['mode']}")
    print(f"Total Submitted:      {report['total_submitted']}")
    print(f"Inserted:             {report['inserted']}")
    print(f"Updated:              {report['updated']}")
    print(f"Skipped (Protected):  {report['skipped']}")
    print(f"Failed:               {report['failed']}")
    print("========================================================\n")

    for d in report.get("details", []):
        print(f"[{d['action'].upper()}] {d['opportunity_id']}: {d['reason']}")

    if report["failed"] > 0 and not args.dry_run:
        sys.exit(1)


if __name__ == "__main__":
    main()
