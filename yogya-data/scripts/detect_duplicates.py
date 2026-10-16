#!/usr/bin/env python3
"""
CLI script to detect duplicate or near-duplicate opportunity candidates.
Evaluates normalized names, providers, source URLs, and identifiers.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.deduplication import detect_duplicate_candidates
from src.config import config


def main():
    parser = argparse.ArgumentParser(description="Identify duplicate opportunity candidates across dataset.")
    parser.add_argument("--input", type=str, default=None, help="Directory or JSON file with opportunities (defaults to data/drafts/)")
    parser.add_argument("--threshold", type=float, default=None, help="Similarity threshold (0.0 - 1.0, default 0.85)")
    parser.add_argument("--report", type=str, default=None, help="Path to save duplicate report JSON")

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

    print(f"[*] Scanning {len(opportunities)} opportunities for duplicates...")
    candidates = detect_duplicate_candidates(opportunities, similarity_threshold=args.threshold)

    print("\n================ DUPLICATE DETECTION RESULTS ================")
    print(f"Total Candidate Duplicate Pairs: {len(candidates)}")
    print("=============================================================\n")

    for idx, c in enumerate(candidates, 1):
        print(f"[{idx}] Confidence: {c['confidence_score']:.2f}")
        print(f"    Scheme A: {c['opportunity_id_a']} ('{c['name_a']}') - {c.get('provider_a')}")
        print(f"    Scheme B: {c['opportunity_id_b']} ('{c['name_b']}') - {c.get('provider_b')}")
        print(f"    Reasons:  {', '.join(c['reasons'])}")
        if c.get("distinctions"):
            print(f"    Distinctions: {', '.join(c['distinctions'])}")
        print(f"    Action:   {c['recommended_action']}\n")

    if args.report:
        rep_path = Path(args.report).resolve()
        rep_path.parent.mkdir(parents=True, exist_ok=True)
        with open(rep_path, "w", encoding="utf-8") as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)
        print(f"[+] Duplicate report saved to: {rep_path}")


if __name__ == "__main__":
    main()
