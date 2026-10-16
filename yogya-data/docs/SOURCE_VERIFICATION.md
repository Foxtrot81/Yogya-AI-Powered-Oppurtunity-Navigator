# Yogya Platform — Source Verification & Evidence Standards

## 1. Principles of Verification Integrity
In Yogya, **accuracy, traceability, and student protection** supersede dataset volume. Misrepresenting a government scheme's income threshold, deadline, or caste requirement can result in a rural student missing an educational deadline or being disqualified after investing scarce financial resources.

### Mandatory Rules:
1. **Never Invent Facts:** Under no circumstances may an agent, developer, or extraction model infer or synthesize an income threshold, deadline, or benefit amount.
2. **AI Extraction Cannot Self-Verify:** Any record extracted by Gemini, OpenAI, or rule-based heuristics enters as `draft` or `needs_review`. Only an explicit human review action with verified source evidence can promote a record to `verified`.
3. **Exact Evidence Linking:** Every official programme fact (mandatory criterion, income ceiling, stipend, deadline) must be substantiated by a verbatim excerpt in the `evidence` array referencing an accessible official URL.
4. **Distinguish Publication vs. Active Intake:** A scheme description published on an official portal does not mean applications are currently open. Portal window dates must be verified separately and labeled honestly as `open`, `closed`, `upcoming`, or `unknown`.

---

## 2. Verification State Machine

```
      [ Ingested Source ]
              │
              ▼
          ┌───────┐
          │ draft │ ◄──────────────┐
          └───┬───┘                │
              │ (Submit for Audit) │ (Flagged Issues)
              ▼                    │
      ┌──────────────┐             │
      │ needs_review ├─────────────┤
      └───┬──────┬───┘             │
          │      │ (Rejected)      │
          │      ▼                 │
          │  ┌──────────┐          │
          │  │ rejected │          │
          │  └──────────┘          │
          ▼                        │
      ┌──────────┐                 │
      │ reviewed │                 │
      └───┬──────┘                 │
          │ (Evidence Validated)   │
          ▼                        │
      ┌──────────┐                 │
      │ verified │                 │
      └───┬──────┘                 │
          │ (Academic Cycle End)   │
          ▼                        │
      ┌──────────┐                 │
      │  stale   ├─────────────────┘
      └──────────┘
```

### Allowed State Transitions:
- `draft` ➔ `needs_review`, `rejected`
- `needs_review` ➔ `reviewed`, `rejected`, `draft`
- `reviewed` ➔ `verified`, `needs_review`, `rejected`
- `verified` ➔ `stale`, `needs_review`
- `stale` ➔ `needs_review`, `draft`, `verified`
- `rejected` ➔ `draft`, `needs_review`

---

## 3. Human Review Checklist for Promotion to `verified`

Before promoting an opportunity record from `reviewed` to `verified`:

### Step 1: Source Authenticity Audit
- [ ] Is the primary URL hosted on a genuine Indian government domain (`.gov.in`, `.nic.in`, or official state educational boards)?
- [ ] Is the guideline document or gazette notification attached and preserved in `data/raw/`?

### Step 2: Verbatim Excerpt Presence Verification
- [ ] For each item in `evidence`, check that `supporting_excerpt` is an exact, unedited quote from the source document.
- [ ] Run automated presence check:
  ```python
  from src.evidence import check_excerpt_presence
  assert check_excerpt_presence(ev["supporting_excerpt"], raw_source_text) is True
  ```

### Step 3: Criteria & Operator Verification
- [ ] Are income limits represented with operator `less_than_or_equal` and unit `"INR/year"`?
- [ ] Are category criteria (SC, ST, OBC, General) clearly differentiated?
- [ ] Are academic requirements (minimum marks, passing grades) represented accurately?
- [ ] Are exclusions preserved (e.g., KVS/NVS students excluded under NMMSS)?

### Step 4: Application Window & Academic Year Check
- [ ] Is the academic year stated explicitly (e.g. `2025-2026`)?
- [ ] If the deadline has passed, is `application_status` marked `"closed"`?
- [ ] If the opening date has not yet arrived, is `application_status` marked `"upcoming"`?

### Step 5: Document Requirements Check
- [ ] Are mandatory certificates identified (Income Certificate, Caste Certificate, Marksheets)?
- [ ] Is the issuing authority noted (e.g., Tahsildar, Sub-Divisional Magistrate)?

---

## 4. Handling Web Access Barriers & CAPTCHAs
Official Indian government portals (such as NSP and State Scholarship Portals) frequently deploy anti-scraping measures, Cloudflare challenges, or session-based CAPTCHAs.

### Operational Guidelines:
1. **Never Attempt to Bypass Authentication or CAPTCHAs:** Automated crawling must respect `robots.txt`, HTTP 403/429 responses, and terms of service.
2. **Manual Ingestion Fallback:** When a portal page cannot be retrieved via automated HTTP client:
   - Download the official PDF guidelines or copy the official text directly from the browser session.
   - Ingest into the pipeline using the manual ingestion command:
     ```bash
     python scripts/ingest_source.py --file path/to/guidelines.pdf --source-url "https://scholarships.gov.in/..." --title "Official Scheme Guidelines"
     ```
   - The pipeline computes the SHA-256 hash and records the manual provenance transparently.
