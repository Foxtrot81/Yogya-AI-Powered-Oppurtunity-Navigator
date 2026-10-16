# Yogya Opportunity Data Pipeline — Summary & Audit Report

**Generated at:** `2026-10-16T05:40:19.013581+00:00`  
**Target Audience:** Rural Indian Students (Classes 9–12, Vocational Training, Apprenticeships)

## 1. Executive Summary
- **Total Opportunities Processed:** `26`
- **Schema-Valid Records:** `26`
- **Invalid Records (Requiring Corrections):** `0`
- **Records Requiring Human Review:** `12`
- **Potential Duplicate Candidates:** `3`
- **Total Validation Errors:** `0`
- **Total Validation Warnings:** `0`

### Verification Status Breakdown
| Status | Count | Description |
| :--- | :--- | :--- |
| `draft` | **12** | AI/Rule extraction draft pending review |
| `verified` | **14** | Verified by human reviewer with evidence |

### Category Breakdown
| Category | Count |
| :--- | :--- |
| `scholarship` | 16 |
| `vocational_training` | 7 |
| `apprenticeship` | 2 |
| `educational_assistance` | 1 |

## 2. Ingested Schemes Roster
| ID | Scheme Name | Category | Provider | Status | Deadline |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ministry_of_labour_employment_labour_wel` | MINISTRY OF LABOUR & EMPLOYMENT - LABOUR WELF | scholarship | MINISTRY OF LABOUR | `draft` | Unknown / Closed |
| `ministry_of_minority_affairs_begum_hazra` | MINISTRY OF MINORITY AFFAIRS - BEGUM HAZRAT M | vocational_training | MINISTRY OF MINORITY AFFAIRS | `draft` | Unknown / Closed |
| `ministry_of_skill_development_and_entrep` | MINISTRY OF SKILL DEVELOPMENT AND ENTREPRENEU | apprenticeship | MINISTRY OF SKILL DEVELOPMENT  | `draft` | Unknown / Closed |
| `ministry_of_social_justice_and_empowerme` | MINISTRY OF SOCIAL JUSTICE AND EMPOWERMENT -  | scholarship | MINISTRY OF SOCIAL JUSTICE AND | `draft` | Unknown / Closed |
| `opp_begum_hazrat_mahal_2026` | Begum Hazrat Mahal National Scholarship Schem | scholarship | Ministry of Minority Affairs | `verified` | 2025-11-30 |
| `opp_depwd_postmatric_disabilities_2026` | Post-Matric Scholarship for Students with Dis | scholarship | Department of Empowerment of P | `verified` | 2025-12-31 |
| `opp_depwd_prematric_disabilities_2026` | Pre-Matric Scholarship for Students with Disa | scholarship | Department of Empowerment of P | `verified` | 2025-12-31 |
| `opp_dgt_craftsmen_training_iti_2026` | Craftsmen Training Scheme (CTS) at Industrial | vocational_training | Directorate General of Trainin | `verified` | Unknown / Closed |
| `opp_mole_beedi_mine_workers_scholarship_2026` | Financial Assistance for Education of Childre | educational_assistance | Ministry of Labour and Employm | `verified` | 2025-11-30 |
| `opp_mota_postmatric_st_2026` | Post-Matric Scholarship Scheme for ST Student | scholarship | Ministry of Tribal Affairs | `verified` | 2025-12-31 |
| `opp_mota_prematric_st_2026` | Pre-Matric Scholarship Scheme for ST Students | scholarship | Ministry of Tribal Affairs | `verified` | 2025-12-31 |
| `opp_naps_apprenticeship_2026` | National Apprenticeship Promotion Scheme (NAP | apprenticeship | Ministry of Skill Development  | `verified` | Unknown / Closed |
| `opp_nmms_scholarship_2026` | National Means-cum-Merit Scholarship Scheme ( | scholarship | Department of School Education | `verified` | 2025-11-30 |
| `opp_nsp_postmatric_sc_2026` | Centrally Sponsored Post-Matric Scholarship f | scholarship | Ministry of Social Justice and | `verified` | 2025-12-31 |
| `opp_nsp_prematric_sc_2026` | Centrally Sponsored Pre-Matric Scholarship Sc | scholarship | Ministry of Social Justice and | `verified` | 2025-12-31 |
| `opp_pmkvy_skill_india_digital_2026` | Pradhan Mantri Kaushal Vikas Yojana (PMKVY 4. | vocational_training | National Skill Development Cor | `verified` | Unknown / Closed |
| `opp_pm_yasasvi_postmatric_2026` | PM-YASASVI Post-Matric Scholarship for OBC, E | scholarship | Ministry of Social Justice and | `verified` | 2025-12-31 |
| `opp_pm_yasasvi_prematric_2026` | PM Young Achievers Scholarship Award Scheme f | scholarship | Ministry of Social Justice and | `verified` | 2025-11-30 |
| `scheme_cts_1` | Scheme (Cts)
1 | vocational_training | DIRECTORATE GENERAL OF TRAININ | `draft` | Unknown / Closed |
| `scheme_guidelines` | Scheme Guidelines | scholarship | MINISTRY OF EDUCATION | `draft` | Unknown / Closed |
| `scholarship_for_sc_students_1` | Scholarship For Sc Students
1 | scholarship | MINISTRY OF SOCIAL JUSTICE | `draft` | Unknown / Closed |
| `scholarship_for_sc_students_revised_guid` | Scholarship For Sc Students Revised Guideline | scholarship | MINISTRY OF SOCIAL JUSTICE AND | `draft` | Unknown / Closed |
| `scholarship_for_students_with_disabiliti` | Scholarship For Students With Disabilities
1 | vocational_training | Government of India | `draft` | Unknown / Closed |
| `scholarship_for_st_students_1` | Scholarship For St Students
1 | vocational_training | MINISTRY OF TRIBAL AFFAIRS | `draft` | Unknown / Closed |
| `scholarship_scheme` | Scholarship Scheme | scholarship | Government of India | `draft` | Unknown / Closed |
| `yojana_pmkvy_4` | Yojana (Pmkvy 4 | vocational_training | Government of India | `draft` | Unknown / Closed |

## 3. Duplicate Candidates Audit
| Scheme A | Scheme B | Confidence | Reasons | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| `opp_depwd_postmatric_disabilities_2026` | `opp_depwd_prematric_disabilities_2026` | `0.91` | High name similarity (91.2%): 'Post-Matric Scholarship for Students with Disabilities' vs 'Pre-Matric Scholarship for Students with Disabilities' | Investigate: likely duplicate from different sources |
| `opp_nsp_postmatric_sc_2026` | `opp_nsp_prematric_sc_2026` | `0.93` | High name similarity (92.5%): 'Centrally Sponsored Post-Matric Scholarship for SC Students' vs 'Centrally Sponsored Pre-Matric Scholarship Scheme for SC Students' | Investigate: likely duplicate from different sources |
| `opp_pm_yasasvi_postmatric_2026` | `opp_pm_yasasvi_prematric_2026` | `0.9` | Shared official URL(s): ['https://socialjustice.gov.in/schemes/pm-yasasvi'] | Investigate: likely duplicate from different sources |

## 4. Evidence & Traceability Audit
Every extracted official fact must have an exact excerpt verified from official government sources:
- National Scholarship Portal: `https://scholarships.gov.in/`
- Skill India Digital Hub: `https://www.skillindiadigital.gov.in/`
- Bharat Skills: `https://www.bharatskill.gov.in/`
- Ministry of Education (DSEL): `https://dsel.education.gov.in/`
- Ministry of Social Justice & Empowerment: `https://socialjustice.gov.in/`

## 5. Integration Contracts for Persons 2 & 3
- **Backend Developer:** Review `docs/API_CONTRACT.md` and `sql/schema.sql`. Import using `scripts/import_postgres.py`.
- **Eligibility Engine Developer:** Filter records using `verification_status == 'verified'`. Structured operators in `eligibility_criteria` support deterministic boolean evaluation.