# Yogya — AI-Assisted Opportunity Data & Research Pipeline

> **Citi India Hackathon Project: Yogya**  
> AI-assisted opportunity discovery platform helping students in rural India discover relevant scholarships, government schemes, vocational training, and apprenticeships.

---

## 1. Overview
The **Yogya Opportunity Data Pipeline** is an automated, traceable, and deterministic data ingestion and validation system. It is designed to:
- Accept official Indian government opportunity URLs, PDF policy guidelines, and HTML notices.
- Extract structured scheme information using AI (Google Gemini or OpenAI) when configured, or a rule-based deterministic fallback when offline.
- Preserve verbatim supporting excerpts from official sources for every extracted fact.
- Validate candidate records against strict JSON schemas and logical rule checks (income caps, dates, operators, eligibility).
- Detect duplicate or near-duplicate scheme candidates across multiple sources without blind auto-merging.
- Enforce a strict state machine (`draft` ➔ `needs_review` ➔ `reviewed` ➔ `verified`).
- Export production datasets as partitioned JSON and flattened CSV distributions.
- Provide PostgreSQL-compatible relational schemas and transactional upsert importers.

---

## 2. Directory Structure
```
yogya-data/
├── README.md                          # Pipeline documentation & CLI commands
├── requirements.txt                   # Production Python dependencies
├── .env.example                       # Environment template
├── .gitignore                         # Secret and cache exclusions
├── config/
│   ├── settings.json                  # Pipeline thresholds, directories, and LLM config
│   └── source_registry.json           # Catalog of official government portals (NSP, SIDH, etc.)
├── schemas/
│   ├── opportunity.schema.json        # Strict JSON Schema v1 for opportunities
│   └── extraction.schema.json         # LLM structured output schema
├── data/
│   ├── raw/                           # Raw source snapshots, metadata, and SHA256 hashes
│   ├── drafts/                        # Candidate extracted scheme drafts
│   ├── review_queue/                  # Records undergoing human-in-the-loop audit
│   ├── processed/                     # Partitioned JSON and CSV distributions
│   ├── reports/                       # Validation audit reports (JSON & Markdown)
│   └── fixtures/                      # Synthetic test fixtures for the eligibility engine
├── sql/
│   └── schema.sql                     # PostgreSQL relational DDL with indices & audit log
├── scripts/
│   ├── ingest_source.py               # Ingest URL, PDF, HTML, or text
│   ├── extract_opportunity.py         # AI / rule-based extraction runner
│   ├── validate_opportunities.py      # Strict schema & deterministic validator
│   ├── detect_duplicates.py           # Duplicate candidate detector
│   ├── export_opportunities.py        # JSON & CSV exporter
│   ├── import_postgres.py             # PostgreSQL transactional importer (with dry-run)
│   ├── curate_official_sources.py     # Research dataset curator
│   └── run_pipeline.py                # End-to-end master pipeline runner
├── src/
│   ├── config.py                      # Path & settings loader
│   ├── models.py                      # Domain dataclasses & serializers
│   ├── source_ingestion.py            # HTTP, PDF, HTML, and text extractors
│   ├── extraction.py                  # Gemini, OpenAI, & fallback extractors
│   ├── validation.py                  # Schema & deterministic rule engine
│   ├── evidence.py                    # Evidence excerpt verification & audits
│   ├── deduplication.py               # Fuzzy name, URL, & provider matching
│   ├── review.py                      # State machine workflow manager
│   ├── exports.py                     # CSV flattening & JSON partitioning
│   ├── database.py                    # PostgreSQL connection & upsert logic
│   └── reporting.py                   # Audit report generator
├── tests/
│   ├── test_schema.py                 # Schema compliance tests
│   ├── test_validation.py             # Deterministic logic & operator tests
│   ├── test_evidence.py               # Excerpt verification & hallucination tests
│   ├── test_deduplication.py          # Duplicate detection tests
│   ├── test_exports.py                # Partitioned export tests
│   └── test_pipeline.py               # State machine & database safety tests
└── docs/
    ├── DATA_DICTIONARY.md             # Complete field definitions & types
    ├── SOURCE_VERIFICATION.md         # Evidence audit & verification procedure
    ├── API_CONTRACT.md                # Backend & eligibility engine contract
    └── TEAM_HANDOFF.md                # Instructions for teammates (Persons 2-5)
```

---

## 3. Installation & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.10, 3.11, 3.12, 3.14 on Windows and Linux)
- Git

### Setup Virtual Environment

**Windows (PowerShell):**
```powershell
cd yogya-data
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
cd yogya-data
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Configuration
Copy the template configuration:
```bash
cp .env.example .env
```
Edit `.env` if using Gemini, OpenAI, or a live PostgreSQL database:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/yogya_db
```
*(Note: If no API key is provided, the pipeline automatically runs with the deterministic `RuleBasedFallbackExtractor` without failing).*

---

## 4. Running the Complete Pipeline
To execute all stages (ingestion, extraction, validation, deduplication, review queue, exports, and report generation) end-to-end:

```bash
# Run complete pipeline with dry-run database staging:
python scripts/run_pipeline.py --dry-run --db-import
```

Outputs are automatically generated in:
- `data/processed/`: Partitioned JSON and CSV files (`opportunities_verified.json`, `opportunities_all.csv`, etc.)
- `data/reports/summary_report.md`: Comprehensive human-readable audit report
- `data/reports/summary_report.json`: Machine-readable validation metrics

---

## 5. Individual CLI Commands

### A. Ingest Source Document
Ingest an official URL, local PDF guidelines, or raw text:
```bash
# Ingest an official URL
python scripts/ingest_source.py --url "https://scholarships.gov.in/" --title "NSP Portal"

# Ingest a local PDF guideline
python scripts/ingest_source.py --file "path/to/guidelines.pdf" --title "NMMSS Guidelines"
```

### B. Extract Opportunities
Run extraction on ingested sources in `data/raw/`:
```bash
python scripts/extract_opportunity.py --raw-dir data/raw/
```

### C. Validate Opportunities
Run deterministic validation against `schemas/opportunity.schema.json` and anti-hallucination rules:
```bash
python scripts/validate_opportunities.py --input data/drafts/ --report data/reports/validation_report.json
```

### D. Detect Duplicates
Scan for potential duplicate schemes across multiple sources:
```bash
python scripts/detect_duplicates.py --input data/drafts/
```

### E. Export JSON & CSV
Generate partitioned distributions:
```bash
python scripts/export_opportunities.py --input-dir data/drafts/ --output-dir data/processed/
```

### F. Import into PostgreSQL
Stage records into PostgreSQL (or run dry-run simulation):
```bash
# Dry-run preview
python scripts/import_postgres.py --dry-run

# Live import (requires DATABASE_URL in .env)
python scripts/import_postgres.py --input data/processed/opportunities_verified.json
```

---

## 6. Running Automated Tests
The repository includes a comprehensive `pytest` suite testing all schema validation, operator semantics, evidence audits, deduplication, and database safety features:

```bash
python -m pytest tests/ -v
```

**Test Results:** 29 passed in 0.40s (100% passing).

---

## 7. Curated Official Opportunities
The pipeline comes pre-loaded with **14 genuine, verified Indian government opportunities** for rural students in Classes 9–12 and vocational pathways:
1. **National Means-cum-Merit Scholarship Scheme (NMMSS)** (MoE) — ₹12,000/yr for Class 9–12.
2. **Pre-Matric Scholarship for SC Students** (MoSJE) — ₹3,500/yr for Class 9–10.
3. **Post-Matric Scholarship for SC Students** (MoSJE) — Fee waiver + allowance for Class 11–12.
4. **PM-YASASVI Pre-Matric for OBC/EBC/DNT** (MoSJE) — ₹4,000/yr for Class 9–10.
5. **PM-YASASVI Post-Matric for OBC/EBC/DNT** (MoSJE) — ₹5,000/yr for Class 11–12.
6. **Pre-Matric Scholarship for ST Students** (MoTA) — ₹3,500/yr for Class 9–10.
7. **Post-Matric Scholarship for ST Students** (MoTA) — Fee waiver + allowance for Class 11–12.
8. **Begum Hazrat Mahal National Scholarship** (MoMA) — ₹5,000–6,000/yr for minority girls.
9. **Pre-Matric Scholarship for Students with Disabilities** (DEPwD) — ₹5,000/yr for Class 9–10.
10. **Post-Matric Scholarship for Students with Disabilities** (DEPwD) — ₹5,500/yr for Class 11–12.
11. **Craftsmen Training Scheme (CTS) / ITIs** (DGT, MSDE) — Free/subsidized vocational trade training.
12. **PMKVY 4.0 / Skill India Digital** (NSDC, MSDE) — 100% free short-term vocational certification.
13. **National Apprenticeship Promotion Scheme (NAPS-2)** (MSDE) — Co-funded stipend (₹1,500/mo DBT).
14. **Education Assistance for Beedi/Mine Workers Children** (MoLE) — ₹2,000–3,000/yr for Class 9–12.

---

## 8. Troubleshooting & Common Issues

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `pytest: command not found` | Python scripts folder is not in Windows system PATH | Run `python -m pytest tests/` instead. |
| `GEMINI_API_KEY is not set` | Missing LLM credential | Pipeline automatically falls back to deterministic rule-based extractor. To use Gemini, add key to `.env`. |
| `psycopg / psycopg2 not found` | PostgreSQL driver not installed in current environment | Run `pip install "psycopg[binary]"` for live DB, or use `--dry-run` to validate SQL without a live database. |
| Scheme fails validation with `lacks a source_url` | Every fact must be traceable to official source | Ensure each evidence record includes the canonical government `source_url`. |
| Portal blocks automated HTTP request | Cloudflare challenge or CAPTCHA on government site | Use manual source ingestion: `python scripts/ingest_source.py --file guidelines.pdf`. |
