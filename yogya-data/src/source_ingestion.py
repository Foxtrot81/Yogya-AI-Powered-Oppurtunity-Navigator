"""
Source ingestion module for URLs, local PDF, HTML, and text documents.
Extracts clean, readable scheme text while preserving provenance, content hash, and page numbers.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup

from src.config import config

logger = logging.getLogger(__name__)


class SourceIngestion:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or config.raw_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        crawler_cfg = config.settings.get("crawler", {})
        self.user_agent = crawler_cfg.get("user_agent", "YogyaResearchBot/1.0")
        self.timeout = crawler_cfg.get("request_timeout_seconds", 30)
        self.max_bytes = crawler_cfg.get("max_content_bytes", 10485760)

    @staticmethod
    def compute_sha256(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def ingest_url(self, url: str, source_title: Optional[str] = None) -> Dict[str, Any]:
        """Ingests content from a public HTTP/HTTPS URL."""
        retrieved_at = datetime.now(timezone.utc).isoformat()
        metadata: Dict[str, Any] = {
            "source_id": f"src_{hashlib.md5(url.encode()).hexdigest()[:10]}",
            "source_type": "url",
            "source_url": url,
            "source_title": source_title or url,
            "retrieved_at": retrieved_at,
            "retrieval_status": "failed",
            "extraction_status": "pending",
            "content_hash": None,
            "error_message": None,
            "text": "",
            "pages": [],
        }

        try:
            headers = {"User-Agent": self.user_agent, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
            response = self.session.get(url, headers=headers, timeout=self.timeout, stream=True)
            
            # Check content length
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > self.max_bytes:
                metadata["error_message"] = f"Content exceeds max allowed bytes ({self.max_bytes})"
                metadata["extraction_status"] = "failed"
                return self._save_raw_source(metadata)

            response.raise_for_status()
            metadata["retrieval_status"] = "success"

            content_type = response.headers.get("Content-Type", "").lower()
            if "application/pdf" in content_type or url.lower().endswith(".pdf"):
                # Handle PDF stream
                pdf_bytes = response.content
                text, pages, ocr_needed = self._extract_pdf_bytes(pdf_bytes)
                metadata["text"] = text
                metadata["pages"] = pages
                metadata["source_type"] = "pdf"
                metadata["extraction_status"] = "ocr_required" if ocr_needed else ("extracted" if text else "empty")
            else:
                # Handle HTML
                html_text = response.text
                text = self._clean_html(html_text)
                metadata["text"] = text
                metadata["extraction_status"] = "extracted" if text else "empty"

            if metadata["text"]:
                metadata["content_hash"] = self.compute_sha256(metadata["text"])

        except requests.exceptions.RequestException as e:
            metadata["error_message"] = f"HTTP request failed: {str(e)}"
            metadata["extraction_status"] = "failed"
        except Exception as e:
            metadata["error_message"] = f"Extraction failed: {str(e)}"
            metadata["extraction_status"] = "failed"

        return self._save_raw_source(metadata)

    def ingest_pdf(self, file_path: Path, source_url: Optional[str] = None) -> Dict[str, Any]:
        """Ingests and extracts text page-by-page from a local PDF."""
        retrieved_at = datetime.now(timezone.utc).isoformat()
        path = Path(file_path).resolve()
        metadata: Dict[str, Any] = {
            "source_id": f"src_pdf_{hashlib.md5(str(path).encode()).hexdigest()[:10]}",
            "source_type": "pdf",
            "file_path": str(path),
            "source_url": source_url or f"file:///{path.as_posix()}",
            "source_title": path.stem,
            "retrieved_at": retrieved_at,
            "retrieval_status": "success" if path.exists() else "failed",
            "extraction_status": "pending",
            "content_hash": None,
            "error_message": None,
            "text": "",
            "pages": [],
        }

        if not path.exists():
            metadata["error_message"] = f"File not found: {path}"
            metadata["extraction_status"] = "failed"
            return self._save_raw_source(metadata)

        try:
            with open(path, "rb") as f:
                pdf_bytes = f.read()
            text, pages, ocr_needed = self._extract_pdf_bytes(pdf_bytes)
            metadata["text"] = text
            metadata["pages"] = pages
            metadata["extraction_status"] = "ocr_required" if ocr_needed else ("extracted" if text else "empty")
            if text:
                metadata["content_hash"] = self.compute_sha256(text)
        except Exception as e:
            metadata["error_message"] = f"Failed to extract PDF: {str(e)}"
            metadata["extraction_status"] = "failed"

        return self._save_raw_source(metadata)

    def ingest_text_file(self, file_path: Path, source_url: Optional[str] = None) -> Dict[str, Any]:
        """Ingests a plain text or markdown file."""
        retrieved_at = datetime.now(timezone.utc).isoformat()
        path = Path(file_path).resolve()
        metadata: Dict[str, Any] = {
            "source_id": f"src_txt_{hashlib.md5(str(path).encode()).hexdigest()[:10]}",
            "source_type": "text",
            "file_path": str(path),
            "source_url": source_url or f"file:///{path.as_posix()}",
            "source_title": path.stem,
            "retrieved_at": retrieved_at,
            "retrieval_status": "success" if path.exists() else "failed",
            "extraction_status": "pending",
            "content_hash": None,
            "error_message": None,
            "text": "",
            "pages": [],
        }

        if not path.exists():
            metadata["error_message"] = f"File not found: {path}"
            metadata["extraction_status"] = "failed"
            return self._save_raw_source(metadata)

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read().strip()
            metadata["text"] = text
            metadata["extraction_status"] = "extracted" if text else "empty"
            if text:
                metadata["content_hash"] = self.compute_sha256(text)
        except Exception as e:
            metadata["error_message"] = f"Failed to read file: {str(e)}"
            metadata["extraction_status"] = "failed"

        return self._save_raw_source(metadata)

    def ingest_manual_text(self, text: str, source_url: str, source_title: str) -> Dict[str, Any]:
        """Ingests manually supplied text or guidelines."""
        retrieved_at = datetime.now(timezone.utc).isoformat()
        cleaned = text.strip()
        metadata: Dict[str, Any] = {
            "source_id": f"src_manual_{hashlib.md5((source_url + source_title).encode()).hexdigest()[:10]}",
            "source_type": "manual",
            "source_url": source_url,
            "source_title": source_title,
            "retrieved_at": retrieved_at,
            "retrieval_status": "success",
            "extraction_status": "extracted" if cleaned else "empty",
            "content_hash": self.compute_sha256(cleaned) if cleaned else None,
            "error_message": None,
            "text": cleaned,
            "pages": [],
        }
        return self._save_raw_source(metadata)

    def _clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        # Remove non-content elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg"]):
            element.extract()

        # Extract structured text with headings and table representation
        lines = []
        for elem in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "tr"]):
            if elem.name in ["h1", "h2", "h3", "h4"]:
                heading_level = "#" * int(elem.name[1])
                text = elem.get_text(separator=" ", strip=True)
                if text:
                    lines.append(f"\n{heading_level} {text}\n")
            elif elem.name == "tr":
                cols = [td.get_text(separator=" ", strip=True) for td in elem.find_all(["td", "th"])]
                if cols:
                    lines.append(" | ".join(cols))
            else:
                text = elem.get_text(separator=" ", strip=True)
                if text:
                    lines.append(text)

        cleaned = "\n".join(lines).strip()
        return cleaned

    def _extract_pdf_bytes(self, pdf_bytes: bytes) -> Tuple[str, List[Dict[str, Any]], bool]:
        """Extracts text from PDF bytes page by page."""
        import io
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages_data = []
        full_text_parts = []
        total_extracted_chars = 0

        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1
            page_text = page.extract_text() or ""
            cleaned = page_text.strip()
            total_extracted_chars += len(cleaned)
            pages_data.append({"page_number": page_num, "text": cleaned})
            if cleaned:
                full_text_parts.append(f"--- Page {page_num} ---\n{cleaned}")

        full_text = "\n\n".join(full_text_parts).strip()
        # If there are pages but almost zero text, it's likely a scanned image requiring OCR
        ocr_needed = len(reader.pages) > 0 and total_extracted_chars < 50
        return full_text, pages_data, ocr_needed

    def _save_raw_source(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        source_id = metadata["source_id"]
        meta_file = self.output_dir / f"{source_id}.json"
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        return metadata
