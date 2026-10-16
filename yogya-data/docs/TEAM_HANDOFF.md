# Yogya Platform — Team Handoff & Integration Guide

**Citi India Hackathon — Team Yogya**  
*Role: Opportunity Data & Research Pipeline Specialist*  
*Deliverable: Opportunity Data Ingestion, Extraction, Validation, and Export System*

---

## 1. Executive Summary for Team
The **Yogya Opportunity Data Pipeline** is implemented, fully tested (29/29 passing automated tests), and populated with **14 genuine, verified Indian government opportunities** targeting rural students in Classes 9–12, vocational trainees, and apprentices.

Every single fact (income thresholds, marks criteria, scholarship amounts, application windows) is backed by **verbatim quotes from official Ministry guidelines** (Ministry of Education, MoSJE, MoTA, MoMA, MSDE, and Ministry of Labour).

---

## 2. Handoff to Person 2 (Backend Developer)
**Your Responsibility:** Exposing REST/GraphQL endpoints for the mobile app and managing PostgreSQL persistence.

### Deliverables for You:
1. **Relational Schema DDL:** [`sql/schema.sql`](file:///c:/Projects/Hacks/Citi/yogya-data/sql/schema.sql)  
   Contains normalized tables: `opportunities`, `eligibility_criteria`, `required_documents`, `evidence_records`, and `opportunity_audit_log`. Includes GIN index on `education_levels` and B-tree indices on `category`, `status`, and `deadline`.
2. **Production Verified Dataset:**  
   - [`data/processed/opportunities_verified.json`](file:///c:/Projects/Hacks/Citi/yogya-data/data/processed/opportunities_verified.json) (Clean JSON distribution)
   - [`data/processed/opportunities_verified.csv`](file:///c:/Projects/Hacks/Citi/yogya-data/data/processed/opportunities_verified.csv) (Flattened spreadsheet view)
3. **Database Import CLI:** [`scripts/import_postgres.py`](file:///c:/Projects/Hacks/Citi/yogya-data/scripts/import_postgres.py)

### How to Run Database Migration and Seed:
```bash
# 1. Create tables in PostgreSQL
psql -U postgres -d yogya_db -f sql/schema.sql

# 2. Configure .env with your local PostgreSQL credentials:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/yogya_db

# 3. Import verified opportunities
python scripts/import_postgres.py --input data/processed/opportunities_verified.json

# (Optional: Dry-run simulation to preview without database)
python scripts/import_postgres.py --dry-run
```

### Safety Features to Know:
- **Zero Accidental Overwrites:** The importer protects verified records. If an incoming record is a raw AI draft, it will **not** overwrite an existing `verified` record in PostgreSQL.
- **Transactional Atomicity:** Inserts for opportunities, child criteria, documents, and evidence run inside an atomic `BEGIN ... COMMIT` transaction.

---

## 3. Handoff to Person 3 (Eligibility & Matching Engine Developer)
**Your Responsibility:** Matching student profiles against scheme criteria and computing eligibility.

### Deliverables for You:
1. **API & Logic Contract:** [`docs/API_CONTRACT.md`](file:///c:/Projects/Hacks/Citi/yogya-data/docs/API_CONTRACT.md)
2. **Data Dictionary:** [`docs/DATA_DICTIONARY.md`](file:///c:/Projects/Hacks/Citi/yogya-data/docs/DATA_DICTIONARY.md)
3. **Synthetic Demonstration Fixtures:** [`data/fixtures/synthetic_fixture_rural_girl_scholarship.json`](file:///c:/Projects/Hacks/Citi/yogya-data/data/fixtures/synthetic_fixture_rural_girl_scholarship.json)

### Core Rules for Your Matching Logic:
1. **Four-Valued Logic (`SATISFIED`, `NOT_SATISFIED`, `UNKNOWN`, `REQUIRES_VERIFICATION`):**
   - If a student profile lacks family income, evaluate `annual_family_income <= 350000` to `UNKNOWN` (do NOT mark ineligible).
   - Use this state to prompt the user in the UI: *"Add your family income to unlock Rs. 12,000 NMMSS scholarship!"*
2. **Preserve AND Logic:** Schemes like NMMSS require:
   - `annual_family_income <= 350000` **AND**
   - `caste_category in ['General', 'OBC', 'SC', 'ST']` **AND**
   - `school_management_type in ['government', 'government_aided', 'local_body']` **AND**
   - `min_marks_percentage >= 55.0`
3. **Decouple Intake Window from Qualification:**
   - Even if `application_period.status == "closed"`, a qualified student should see: *"You are eligible! Applications open next cycle (July 2026). Tap to get notified."*

---

## 4. Handoff to Person 4 (Mobile App Developer)
**Your Responsibility:** Creating a clean, localized, low-bandwidth UI for rural students.

### Guidance for the Mobile UI:
1. **Clear Benefit Cards:** Show the headline benefit prominently:
   - e.g., `"₹12,000 / year"` or `"100% Free Government ITI Training"`
2. **Next Steps & Document Readiness:**
   - Every opportunity lists `required_documents` (e.g. Aadhaar, Income Certificate from Tahsildar).
   - Show a checklist so students know which documents to take to their local Common Service Centre (CSC) / Cyber Cafe.
3. **Official Links:**
   - Always link to the `application_url` (`https://scholarships.gov.in/`) so students apply through the authentic government portal.

---

## 5. Handoff to Person 5 (Product Lead / Pitch Presentation)
**Key Differentiators to Highlight to Hackathon Judges:**
- **Zero Hallucination Guarantee:** We refuse to synthesize scheme facts. 100% of our production records have traceable excerpts to `.gov.in` websites.
- **Traceable Provenance:** Every threshold links to an exact clause in government policy documents.
- **State Machine Safeguard:** AI models extract drafts, but strict deterministic rules and human review gates prevent unverified data from reaching vulnerable students.
- **Comprehensive Coverage:** 14 verified opportunities spanning school scholarships (NMMSS, Pre-Matric SC/ST/OBC), minority schemes (Begum Hazrat Mahal), disability assistance, vocational training (CTS/ITI), and apprenticeships (NAPS-2).
