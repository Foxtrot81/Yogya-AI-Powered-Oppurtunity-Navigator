#!/usr/bin/env python3
"""
CLI script to validate opportunity JSON records against strict schema and deterministic rules.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.validation import validate_dataset
from src.config import config


def main():
    parser = argparse.ArgumentParser(description="Validate opportunity JSON files against schema and logical rules.")
    parser.add_argument("--input", type=str, default=None, help="Path to single JSON file or directory containing opportunities (defaults to data/drafts/)")
    parser.add_argument("--schema", type=str, default=None, help="Path to opportunity.schema.json override")
    parser.add_argument("--report", type=str, default=None, help="Path to save validation output report JSON")

    args = parser.parse_args()
    input_path = Path(args.input).resolve() if args.input else config.drafts_dir

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

    if not opportunities:
        print(f"[!] No opportunities found to validate in {input_path}")
        sys.exit(0)

    schema_file = Path(args.schema).resolve() if args.schema else config.opportunity_schema_path
    print(f"[*] Validating {len(opportunities)} opportunity record(s) using schema: {schema_file.name}...")

    results = validate_dataset(opportunities, schema_path=schema_file)

    print("\n================ VALIDATION REPORT ================")
    print(f"Total Records Processed:      {results['total_records_processed']}")
    print(f"Valid Records:                {results['valid_records']}")
    print(f"Invalid Records:              {results['invalid_records']}")
    print(f"Requiring Human Review:       {results['records_requiring_human_review']}")
    print(f"Total Errors Found:           {results['total_errors']}")
    print(f"Total Warnings Found:         {results['total_warnings']}")
    print("===================================================\n")

    for rec in results["record_results"]:
        status_marker = "[PASS]" if rec["is_valid"] else "[FAIL]"
        print(f"{status_marker} {rec['opportunity_id']}: {rec['name']}")
        for err in rec["errors"]:
            print(f"    - ERROR [{err['field']}]: {err['message']}")
        for warn in rec["warnings"]:
            print(f"    - WARN  [{warn['field']}]: {warn['message']}")

    if args.report:
        report_file = Path(args.report).resolve()
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as rf:
            json.dump(results, rf, indent=2, ensure_ascii=False)
        print(f"\n[+] Detailed validation report saved to: {report_file}")

    if results["invalid_records"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
