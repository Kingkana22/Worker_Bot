CREATE TABLE IF NOT EXISTS freelance_jobs (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    remote_id TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    budget TEXT,
    description TEXT,
    posted_at TIMESTAMPTZ NOT NULL,
    matched_keywords TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scan_runs (
    id BIGSERIAL PRIMARY KEY,
    target TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL,
    blocked BOOLEAN NOT NULL DEFAULT FALSE,
    blocked_reason TEXT,
    artifacts_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS findings (
    id BIGSERIAL PRIMARY KEY,
    scan_run_id BIGINT NOT NULL REFERENCES scan_runs(id),
    target TEXT NOT NULL,
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    tool TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    validated BOOLEAN NOT NULL,
    validation_notes TEXT,
    evidence_json JSONB,
    discovered_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_scan_runs_target ON scan_runs(target);
