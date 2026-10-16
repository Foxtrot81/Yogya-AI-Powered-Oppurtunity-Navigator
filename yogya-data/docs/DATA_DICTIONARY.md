# Yogya Platform — Opportunity Data Dictionary

## 1. Overview
This document specifies the exact field definitions, data types, allowed enumerations, and validation constraints for the **Yogya Opportunity Data Schema (v1.0.0)**. The schema is optimized for rural students in India (Classes 9–12, vocational training, apprenticeships, and higher education).

---

## 2. Core Entity: Opportunity

| Field Name | Type | Required | Description & Constraints | Example |
| :--- | :--- | :--- | :--- | :--- |
| `schema_version` | String | **Yes** | Semantic version of the schema format. Pattern: `^[0-9]+\.[0-9]+\.[0-9]+$` | `"1.0.0"` |
| `opportunity_id` | String | **Yes** | Unique, stable, lowercase slug identifier. Pattern: `^[a-z0-9_-]{5,80}$` | `"opp_nmms_scholarship_2026"` |
| `name` | String | **Yes** | Official scheme title. Length: 3 to 300 characters. | `"National Means-cum-Merit Scholarship Scheme"` |
| `category` | Enum | **Yes** | Classification of opportunity. Allowed: `scholarship`, `educational_assistance`, `vocational_training`, `apprenticeship`, `course`, `other`. | `"scholarship"` |
| `provider` | String | **Yes** | Government Ministry, Department, or Directorate. | `"Ministry of Education"` |
| `description` | String | **Yes** | Clear summary of target students, purpose, and institutional scope (min 10 chars). | `"Central scheme awarding scholarships to Class 9-12 students..."` |
| `education_levels` | Array[Enum] | **Yes** | Target school/college levels. Enum: `class_9`, `class_10`, `class_11`, `class_12`, `undergraduate`, `diploma`, `vocational`, `postgraduate`, `all`. | `["class_9", "class_10", "class_11", "class_12"]` |
| `geographic_scope` | Object | **Yes** | Geographic applicability (`type`: `national`, `state`, `district`; `states`: list of state names; `districts`: list). | `{"type": "national", "states": [], "districts": []}` |
| `eligibility_criteria` | Array[Object] | **Yes** | Structured criteria evaluated by the Yogya eligibility matching engine (see Section 3). | `[...]` |
| `required_documents` | Array[Object] | **Yes** | Necessary certificates and identification documents (see Section 4). | `[...]` |
| `benefits` | Object | **Yes** | Financial and in-kind benefits package (see Section 5). | `{...}` |
| `application_period` | Object | **Yes** | Dates, academic year, and status verification metadata (see Section 6). | `{...}` |
| `application_status` | Enum | **Yes** | Current portal intake status: `open`, `closed`, `upcoming`, `unknown`. | `"closed"` |
| `official_source_urls`| Array[URI] | **Yes** | Verified official government domains hosting scheme documentation. Min items: 1. | `["https://scholarships.gov.in/"]` |
| `application_url` | URI / null | No | Deep-link to student application portal. | `"https://scholarships.gov.in/"` |
| `evidence` | Array[Object] | **Yes** | Traceable evidence excerpts proving extracted facts (see Section 7). | `[...]` |
| `last_checked_at` | ISO 8601 | **Yes** | Timestamp when facts were last audited against the official source. | `"2026-10-16T10:00:00Z"` |
| `verification_status`| Enum | **Yes** | Documented review state: `draft`, `needs_review`, `reviewed`, `verified`, `stale`, `rejected`. | `"verified"` |
| `review_notes` | Array[String]| No | Audit log entries recording reviewer ID, rationale, and timestamps. | `["[2026-10-16] Verified by Data Quality Engineer"]` |
| `synthetic` | Boolean | No | Flags artificial test records. Must be `false` for production datasets. | `false` |

---

## 3. Structured Eligibility Criteria (`eligibility_criteria`)

Each element represents an atomic predicate that can be evaluated deterministically by the student eligibility matcher.

| Field | Type | Required | Description / Allowed Values |
| :--- | :--- | :--- | :--- |
| `criterion_id` | String | **Yes** | Unique identifier (e.g., `"crit_nmms_income"`). Pattern: `^[a-z0-9_-]{3,60}$` |
| `field` | String | **Yes** | Profile attribute to evaluate (e.g., `annual_family_income`, `caste_category`, `min_marks_percentage`, `gender`, `domicile_state`, `age_years`). |
| `operator` | Enum | **Yes** | Relational operator. Supported:<br>• `equals`<br>• `not_equals`<br>• `less_than`<br>• `less_than_or_equal`<br>• `greater_than`<br>• `greater_than_or_equal`<br>• `in`<br>• `not_in`<br>• `between`<br>• `contains`<br>• `requires_document`<br>• `unknown_or_manual_review` |
| `value` | Any | No | Threshold or target value (e.g., `350000.0`, `"SC"`, `["class_9", "class_10"]`). |
| `unit` | String / null | No | Standard unit (e.g., `"INR/year"`, `"percentage"`, `"years"`). |
| `condition_type`| Enum | **Yes** | Role in evaluation: `mandatory` (must satisfy), `optional` (points-based), `disqualification` (fails if matched), `preference` (bonus weight). |
| `required` | Boolean | **Yes** | Whether this criterion is strictly required to qualify. |
| `evidence_reference`| String / null | No | Cross-reference linking to `evidence_id` in the `evidence` array. Mandatory criteria **must** have a valid evidence reference. |
| `review_status` | Enum | **Yes** | Human review state: `unreviewed`, `confirmed`, `flagged`, `rejected`. |
| `notes` | String / null | No | Clarifications on exceptions, state relaxations, or exemptions. |

---

## 4. Required Documents (`required_documents`)

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `document_name` | String | **Yes** | Human-readable document title (e.g., `"Income Certificate"`, `"Aadhaar Card"`). |
| `document_type` | String | **Yes** | Semantic document class (e.g., `income_proof`, `caste_proof`, `academic_proof`, `identity_proof`, `disability_proof`, `bank_details`). |
| `mandatory` | Boolean | **Yes** | Indicates if application cannot be submitted without this document. |
| `description` | String / null| No | Issuing authority guidelines (e.g., `"Issued by Tahsildar/SDM"`). |
| `evidence_reference`| String / null| No | Matches `evidence_id` where requirement is stated in source text. |

---

## 5. Benefits Object (`benefits`)

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `type` | Enum | **Yes** | Benefit archetype: `financial`, `stipend`, `tuition_waiver`, `in_kind`, `composite`, `training_and_certification`. |
| `financial_amount` | Number / null | No | Monetary amount (must be non-negative). `null` for non-cash training schemes. |
| `currency` | String | No | Default currency code: `"INR"`. |
| `frequency` | Enum / null | No | Disbursement cadence: `annual`, `monthly`, `one_time`, `course_duration`, `variable`. |
| `description` | String | **Yes** | Clear summary of financial allowances, fee waivers, or kits provided. |
| `non_financial_benefits`| Array[String]| No | List of additional outcomes (e.g., `["National Trade Certificate (NTC)", "Placement Assistance"]`). |

---

## 6. Application Period (`application_period`)

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `opening_date` | Date / null | No | ISO 8601 Date (`YYYY-MM-DD`). |
| `deadline` | Date / null | No | ISO 8601 Date (`YYYY-MM-DD`). Must satisfy `opening_date <= deadline`. |
| `academic_year`| String / null | No | Academic cycle (e.g., `"2025-2026"`). |
| `status` | Enum | **Yes** | Current portal availability: `open`, `closed`, `upcoming`, `unknown`. |
| `status_verification_date`| Date / null | No | Date when portal window was verified (`YYYY-MM-DD`). |
| `notes` | String / null | No | Context regarding portal state or tentative reopening dates. |

---

## 7. Evidence Traceability Object (`evidence`)

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `evidence_id` | String | **Yes** | Unique identifier (e.g., `"ev_nmms_income"`). Pattern: `^ev_[a-z0-9_-]{2,60}$` |
| `field_path` | String | **Yes** | JSON path to verified attribute (e.g., `"eligibility_criteria[0].value"`, `"benefits.financial_amount"`). |
| `source_url` | URI | **Yes** | URL of official document or portal page from which excerpt was extracted. |
| `source_title` | String / null | No | Title of official policy document, gazette notification, or guideline booklet. |
| `supporting_excerpt`| String | **Yes** | Verbatim quote from source text (min 5, max 1000 characters). Must exist in raw source. |
| `page_number` | Integer / null | No | Page number in source PDF (1-indexed). |
| `section_heading` | String / null | No | Section or clause heading from official guidelines. |
| `retrieved_at` | ISO 8601 | **Yes** | Timestamp of source ingestion. |
| `extraction_method` | Enum | **Yes** | `manual`, `rule_based`, `llm_gemini`, `llm_openai`, `llm_fallback`. |
| `review_status` | Enum | **Yes** | `pending_review`, `verified`, `rejected`, `flagged`. |
