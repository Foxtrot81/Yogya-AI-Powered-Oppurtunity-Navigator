#!/usr/bin/env python3
"""
CLI script to ingest an official opportunity source (URL, PDF, HTML, or text).
Saves raw source metadata, text, and SHA256 content hash in data/raw/.
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.source_ingestion import SourceIngestion
from src.config import config


def main():
    parser = argparse.ArgumentParser(description="Ingest official scheme document or webpage.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", type=str, help="Official URL to download and ingest")
    group.add_argument("--file", type=str, help="Local PDF, HTML, or text file to ingest")
    group.add_argument("--text", type=str, help="Directly supply raw text")

    parser.add_argument("--title", type=str, default=None, help="Document title or scheme name")
    parser.add_argument("--source-url", type=str, default=None, help="Source URL provenance for file or text input")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to save raw ingested JSON")

    args = parser.parse_args()
    out_dir = Path(args.output_dir).resolve() if args.output_dir else config.raw_dir
    ingestor = SourceIngestion(output_dir=out_dir)

    print(f"[*] Ingesting source...")
    if args.url:
        result = ingestor.ingest_url(args.url, source_title=args.title)
    elif args.file:
        file_path = Path(args.file).resolve()
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            result = ingestor.ingest_pdf(file_path, source_url=args.source_url)
        else:
            result = ingestor.ingest_text_file(file_path, source_url=args.source_url)
    elif args.text:
        src_url = args.source_url or "urn:manual:input"
        title = args.title or "Manually Supplied Text"
        result = ingestor.ingest_manual_text(args.text, source_url=src_url, source_title=title)

    status = result.get("retrieval_status")
    ext_status = result.get("extraction_status")
    source_id = result.get("source_id")

    print(f"[+] Ingestion complete.")
    print(f"    Source ID: {source_id}")
    print(f"    Retrieval Status: {status}")
    print(f"    Extraction Status: {ext_status}")
    print(f"    Content Hash: {result.get('content_hash')}")
    print(f"    Text Extracted Length: {len(result.get('text', ''))} characters")

    if result.get("error_message"):
        print(f"    [!] Notice: {result.get('error_message')}")

    if ext_status == "failed" or status == "failed":
        sys.exit(1)


if __name__ == "__main__":
    main()
