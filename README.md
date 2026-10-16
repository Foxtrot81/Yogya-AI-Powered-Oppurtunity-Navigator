# Yogya — Citi India Hackathon Project

Welcome to **Yogya**, a platform helping students in rural India discover relevant scholarships, government schemes, vocational training, and apprenticeships.

The opportunity data, extraction, validation, and research pipeline is located in [`yogya-data/`](file:///c:/Projects/Hacks/Citi/yogya-data):

- **Data Pipeline Documentation:** [`yogya-data/README.md`](file:///c:/Projects/Hacks/Citi/yogya-data/README.md)
- **Data Dictionary:** [`yogya-data/docs/DATA_DICTIONARY.md`](file:///c:/Projects/Hacks/Citi/yogya-data/docs/DATA_DICTIONARY.md)
- **Source Verification:** [`yogya-data/docs/SOURCE_VERIFICATION.md`](file:///c:/Projects/Hacks/Citi/yogya-data/docs/SOURCE_VERIFICATION.md)
- **API & Eligibility Contract:** [`yogya-data/docs/API_CONTRACT.md`](file:///c:/Projects/Hacks/Citi/yogya-data/docs/API_CONTRACT.md)
- **Team Handoff Guide:** [`yogya-data/docs/TEAM_HANDOFF.md`](file:///c:/Projects/Hacks/Citi/yogya-data/docs/TEAM_HANDOFF.md)
- **PostgreSQL DDL:** [`yogya-data/sql/schema.sql`](file:///c:/Projects/Hacks/Citi/yogya-data/sql/schema.sql)
- **Partitioned Exports:** [`yogya-data/data/processed/`](file:///c:/Projects/Hacks/Citi/yogya-data/data/processed/)

### Quick Start
```powershell
cd yogya-data
python -m pytest tests/ -v
python scripts/run_pipeline.py --dry-run --db-import
```
