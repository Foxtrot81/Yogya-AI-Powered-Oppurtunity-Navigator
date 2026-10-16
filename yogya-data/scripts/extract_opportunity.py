#!/usr/bin/env python3
"""
CLI script to extract structured opportunity information from ingested raw sources.
Uses the configured LLM provider (Gemini / OpenAI) or rule-based fallback.
Saves extracted records into data/drafts/.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.extraction import get_extractor, extract_opportunities_from_raw
from src.config import config


def main():
    parser = argparse.ArgumentParser(description="Extract structured opportunities from raw ingested source.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--raw-file", type=str, help="Path to single raw source JSON file in data/raw/")
    group.add_argument("--raw-dir", type=str, help="Directory containing raw source JSON files")

    parser.add_argument("--provider", type=str, default=None, choices=["gemini", "openai", "none", "fallback"], help="LLM extraction provider override")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to save extracted draft opportunities")

    args = parser.parse_args()
    out_dir = Path(args.output_dir).resolve() if args.output_dir else config.drafts_dir
    extractor = get_extractor(args.provider)

    raw_files = []
    if args.raw_file:
        raw_files.append(Path(args.raw_file).resolve())
    elif args.raw_dir:
        raw_files.extend(list(Path(args.raw_dir).resolve().glob("*.json")))

    if not raw_files:
        print("[!] No raw source files found.")
        sys.exit(1)

    print(f"[*] Processing {len(raw_files)} raw source(s) with extractor: {extractor.__class__.__name__}...")
    total_extracted = 0

    for rf in raw_files:
        print(f"    Extracting from {rf.name}...")
        extracted = extract_opportunities_from_raw(rf, output_dir=out_dir, extractor=extractor)
        total_extracted += len(extracted)
        for opp in extracted:
            print(f"      -> Extracted: {opp.get('opportunity_id')} ({opp.get('name')})")

    print(f"[+] Extraction complete. Total opportunities extracted: {total_extracted}")
    print(f"    Saved into: {out_dir}")


if __name__ == "__main__":
    main()
