-- ====================================================================
-- Yogya Opportunity Data Platform - Relational PostgreSQL Schema
-- Designed for normalized, traceable scheme storage, eligibility matching,
-- and audit logging for rural education schemes in India.
-- ====================================================================

-- 1. Main Opportunities Table
CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id VARCHAR(80) PRIMARY KEY,
    schema_version VARCHAR(16) NOT NULL DEFAULT '1.0.0',
    name VARCHAR(300) NOT NULL,
    category VARCHAR(50) NOT NULL,
    provider VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    education_levels JSONB NOT NULL,
    geographic_scope JSONB NOT NULL,
    benefit_type VARCHAR(50) NOT NULL,
    benefit_financial_amount NUMERIC(12, 2),
    benefit_currency VARCHAR(10) DEFAULT 'INR',
    benefit_frequency VARCHAR(50),
    benefit_description TEXT,
    non_financial_benefits JSONB DEFAULT '[]'::jsonb,
    application_status VARCHAR(30) NOT NULL,
    application_opening_date DATE,
    application_deadline DATE,
    academic_year VARCHAR(20),
    status_verification_date DATE,
    official_source_urls JSONB NOT NULL,
    application_url TEXT,
    verification_status VARCHAR(30) NOT NULL DEFAULT 'draft',
    synthetic BOOLEAN DEFAULT FALSE,
    last_checked_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indices for rapid querying by eligibility engine and mobile app
CREATE INDEX IF NOT EXISTS idx_opportunities_category ON opportunities(category);
CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(application_status);
CREATE INDEX IF NOT EXISTS idx_opportunities_verification ON opportunities(verification_status);
CREATE INDEX IF NOT EXISTS idx_opportunities_deadline ON opportunities(application_deadline);
CREATE INDEX IF NOT EXISTS idx_opportunities_education_levels ON opportunities USING GIN (education_levels);

-- 2. Structured Eligibility Criteria Table
CREATE TABLE IF NOT EXISTS eligibility_criteria (
    criterion_id VARCHAR(60) PRIMARY KEY,
    opportunity_id VARCHAR(80) NOT NULL REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,
    field VARCHAR(80) NOT NULL,
    operator VARCHAR(40) NOT NULL,
    value JSONB,
    unit VARCHAR(40),
    condition_type VARCHAR(30) NOT NULL DEFAULT 'mandatory',
    required BOOLEAN NOT NULL DEFAULT TRUE,
    evidence_reference VARCHAR(60),
    review_status VARCHAR(30) NOT NULL DEFAULT 'unreviewed',
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_criteria_opportunity_id ON eligibility_criteria(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_criteria_field ON eligibility_criteria(field);

-- 3. Required Documents Table
CREATE TABLE IF NOT EXISTS required_documents (
    document_id SERIAL PRIMARY KEY,
    opportunity_id VARCHAR(80) NOT NULL REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,
    document_name VARCHAR(200) NOT NULL,
    document_type VARCHAR(80) NOT NULL,
    mandatory BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT,
    evidence_reference VARCHAR(60),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_opportunity_id ON required_documents(opportunity_id);

-- 4. Evidence Traceability Table
CREATE TABLE IF NOT EXISTS evidence_records (
    evidence_id VARCHAR(60) PRIMARY KEY,
    opportunity_id VARCHAR(80) NOT NULL REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,
    field_path VARCHAR(120) NOT NULL,
    source_url TEXT NOT NULL,
    source_title VARCHAR(300),
    supporting_excerpt TEXT NOT NULL,
    page_number INT,
    section_heading VARCHAR(200),
    retrieved_at TIMESTAMPTZ NOT NULL,
    extraction_method VARCHAR(50) NOT NULL,
    review_status VARCHAR(30) NOT NULL DEFAULT 'pending_review',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evidence_opportunity_id ON evidence_records(opportunity_id);

-- 5. Opportunity Audit & Review Log
CREATE TABLE IF NOT EXISTS opportunity_audit_log (
    log_id SERIAL PRIMARY KEY,
    opportunity_id VARCHAR(80) NOT NULL REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,
    previous_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    actor_id VARCHAR(100) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    notes TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_opportunity_id ON opportunity_audit_log(opportunity_id);
