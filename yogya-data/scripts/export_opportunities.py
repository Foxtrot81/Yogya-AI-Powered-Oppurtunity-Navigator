#!/usr/bin/env python3
"""
CLI script to export opportunities into partitioned JSON and CSV distributions.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.exports import OpportunityExporter
from src.config import config


def main():
    parser = argparse.ArgumentParser(description="Export opportunity datasets into JSON and CSV files.")
    parser.add_argument("--input-dir", type=str, default=None, help="Directory containing source opportunity JSONs (defaults to data/drafts/)")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to save exported files (defaults to data/processed/)")

    args = parser.parse_args()
    in_dir = Path(args.input_dir).resolve() if args.input_dir else config.drafts_dir
    out_dir = Path(args.output_dir).resolve() if args.output_dir else config.processed_dir

    opportunities = []
    for f in in_dir.glob("*.json"):
        with open(f, "r", encoding="utf-8") as jf:
            data = json.load(jf)
            if isinstance(data, list):
                opportunities.extend(data)
            else:
                opportunities.append(data)

    print(f"[*] Exporting {len(opportunities)} opportunities from {in_dir} to {out_dir}...")
    exporter = OpportunityExporter(output_dir=out_dir)
    exported = exporter.export_all(opportunities)

    print("\n[+] Exports completed successfully:")
    for key, path in exported.items():
        print(f"    - {key}: {path}")


if __name__ == "__main__":
    main()
