# Yogya Platform — Database & Eligibility Engine API Contract

## 1. Purpose & Architecture
This contract establishes the formal interface between the **Yogya Data Pipeline (Component 1)**, the **PostgreSQL Backend (Component 2)**, and the **Rule-Based Eligibility Engine (Component 3)** for the Citi India Hackathon.

```
┌───────────────────────────┐
│   Yogya Data Pipeline     │
│  (Research & Ingestion)   │
└─────────────┬─────────────┘
              │ Validated Production Records
              ▼
┌───────────────────────────┐
│    PostgreSQL Database    │
│  (Normalized Tables/JSONB)│
└─────────────┬─────────────┘
              │ Scheme Criteria & Thresholds
              ▼
┌───────────────────────────┐        ┌───────────────────────────┐
│ Eligibility Match Engine  │ ◄────  │ Student Profile Data      │
│ (Multi-Valued Logic)      │        │ (Income, Caste, Class...) │
└─────────────┬─────────────┘        └───────────────────────────┘
              │ Match Confidence & Required Actions
              ▼
┌───────────────────────────┐
│    Yogya Mobile App       │
│ (Personalized Discovery)  │
└───────────────────────────┘
```

---

## 2. Canonical Enumerations

### A. Opportunity Categories (`category`)
- `scholarship`: Direct cash grants or financial awards for education.
- `educational_assistance`: In-kind uniforms, textbooks, bicycles, or hostel subsidies.
- `vocational_training`: Technical training, ITI courses, and Craftsmen Training Schemes.
- `apprenticeship`: On-the-job industrial training with government/industry stipend (NAPS-2).
- `course`: Short-term digital, vocational, or preparatory certifications.
- `other`: Specialized government welfare initiatives.

### B. Education Levels (`education_levels`)
- Primary/Middle: `class_8_pass`
- Secondary: `class_9`, `class_10`
- Higher Secondary: `class_11`, `class_12`
- Post-School / Vocational: `vocational`, `diploma`, `undergraduate`, `postgraduate`, `all`

### C. Verification Status (`verification_status`)
Production queries must filter for:
```sql
WHERE verification_status = 'verified' AND synthetic = FALSE
```

---

## 3. Four-Valued Eligibility Logic Specification

A critical vulnerability in naive matching engines is assuming that missing student information or ambiguous government criteria implies ineligibility.

The Yogya Eligibility Engine evaluates each criterion into one of **four distinct states**:

1. **`SATISFIED` (`True`):** The student profile meets or exceeds the criterion threshold.
2. **`NOT_SATISFIED` (`False`):** The student profile definitively violates the criterion (e.g., student income exceeds ceiling, or wrong caste category).
3. **`UNKNOWN` (`None`):** The student profile has not provided this attribute yet (e.g., family income is not filled in). The app prompts the student: *"Provide your family income to unlock this scheme."*
4. **`REQUIRES_VERIFICATION` (`'MANUAL'`):** The condition involves physical documentation, state-level entrance exam ranking, or district quota that cannot be evaluated purely by profile matching.

### Logical Aggregation Rules (AND / OR):
- A scheme requires all `mandatory` criteria to be `SATISFIED`.
- If any mandatory criterion is `NOT_SATISFIED` ➔ Overall Scheme: **`INELIGIBLE`**.
- If no mandatory criteria are `NOT_SATISFIED`, but one or more are `UNKNOWN` ➔ Overall Scheme: **`POTENTIAL_MATCH_NEEDS_INFO`** (surfaces missing questions to student).
- If all mandatory criteria are `SATISFIED`, but some require document verification ➔ Overall Scheme: **`ELIGIBLE_NEEDS_DOCUMENTS`**.

---

## 4. Operator Evaluation Semantics

| Operator | Field Value Type | Comparison Rule |
| :--- | :--- | :--- |
| `equals` | String / Number / Bool | `profile[field] == criterion.value` |
| `not_equals` | String / Number / Bool | `profile[field] != criterion.value` |
| `less_than` | Number | `profile[field] < criterion.value` |
| `less_than_or_equal`| Number | `profile[field] <= criterion.value` (Used for income caps) |
| `greater_than` | Number | `profile[field] > criterion.value` |
| `greater_than_or_equal`| Number | `profile[field] >= criterion.value` (Used for marks %, age) |
| `in` | List | `profile[field] in criterion.value` (Used for caste, class levels) |
| `not_in` | List | `profile[field] not in criterion.value` |
| `between` | `[min, max]` | `criterion.value[0] <= profile[field] <= criterion.value[1]` |
| `contains` | String / List | `criterion.value in profile[field]` |
| `requires_document` | Document identifier | `profile.has_document(criterion.value)` |
| `unknown_or_manual_review`| Any / null | Evaluates to `'MANUAL'` (requires human/document verification) |

---

## 5. Separation of Application Status vs. Student Eligibility

> **CRITICAL RULE:** An opportunity being closed for applications does **NOT** make a student ineligible!

- **Eligibility** is an intrinsic attribute of the student's background (caste, income, class).
- **Application Status** (`open`, `closed`, `upcoming`, `unknown`) is an extrinsic property of the government portal calendar.

### Mobile App Presentation Matrix:

| Eligibility State | Application Status = `open` | Application Status = `closed` / `upcoming` |
| :--- | :--- | :--- |
| **`ELIGIBLE`** | **"Apply Now"** (Green Action Button) | **"Eligible for Next Cycle"** (Set Calendar Reminder) |
| **`POTENTIAL_MATCH`**| **"Complete 1 Detail to Qualify"** | **"Check Requirements for Upcoming Cycle"** |
| **`INELIGIBLE`** | Hidden or placed in "Other Schemes" | Hidden |

---

## 6. PostgreSQL Query Patterns for Backend Developers

### Query 1: Fetch all verified opportunities for Class 9 or 10 students
```sql
SELECT
    opportunity_id,
    name,
    category,
    provider,
    benefit_financial_amount,
    benefit_frequency,
    application_status,
    application_deadline
FROM opportunities
WHERE verification_status = 'verified'
  AND synthetic = FALSE
  AND education_levels ?| array['class_9', 'class_10']
ORDER BY benefit_financial_amount DESC NULLS LAST;
```

### Query 2: Fetch all criteria for a specific opportunity
```sql
SELECT
    criterion_id,
    field,
    operator,
    value,
    unit,
    condition_type,
    required,
    review_status
FROM eligibility_criteria
WHERE opportunity_id = 'opp_nmms_scholarship_2026'
ORDER BY required DESC, criterion_id ASC;
```

### Query 3: Fetch audit trail and supporting evidence
```sql
SELECT
    evidence_id,
    field_path,
    source_url,
    supporting_excerpt,
    section_heading
FROM evidence_records
WHERE opportunity_id = 'opp_nmms_scholarship_2026';
```
