CREATE TABLE IF NOT EXISTS freelance_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    remote_id TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    budget TEXT,
    description TEXT,
    posted_at TEXT NOT NULL,
    matched_keywords TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scan_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    blocked INTEGER NOT NULL DEFAULT 0,
    blocked_reason TEXT,
    artifacts_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id INTEGER NOT NULL,
    target TEXT NOT NULL,
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    tool TEXT NOT NULL,
    confidence REAL NOT NULL,
    validated INTEGER NOT NULL,
    validation_notes TEXT,
    evidence_json TEXT,
    discovered_at TEXT NOT NULL,
    FOREIGN KEY(scan_run_id) REFERENCES scan_runs(id)
);

CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_scan_runs_target ON scan_runs(target);
