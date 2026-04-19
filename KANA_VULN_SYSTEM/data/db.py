from __future__ import annotations

import json
from pathlib import Path

import aiosqlite
import asyncpg

from core.task_models import JobPosting, ScanResult


class DatabaseClient:
    def __init__(self, engine: str, dsn: str) -> None:
        self.engine = engine.lower()
        self.dsn = dsn

    async def initialize_schema(self, schema_path: Path) -> None:
        sql = schema_path.read_text(encoding='utf-8')
        if self.engine == 'sqlite':
            db_path = Path(self.dsn)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            async with aiosqlite.connect(db_path) as conn:
                await conn.executescript(sql)
                await conn.commit()
            return

        if self.engine == 'postgres':
            conn = await asyncpg.connect(self.dsn)
            try:
                await conn.execute(sql)
            finally:
                await conn.close()
            return

        raise ValueError(f'Unsupported database engine: {self.engine}')

    async def save_jobs(self, jobs: list[JobPosting]) -> None:
        if not jobs:
            return

        if self.engine == 'sqlite':
            db_path = Path(self.dsn)
            async with aiosqlite.connect(db_path) as conn:
                await conn.executemany(
                    '''
                    INSERT INTO freelance_jobs
                    (source, remote_id, title, url, budget, description, posted_at, matched_keywords)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    [
                        (
                            j.source,
                            j.remote_id,
                            j.title,
                            j.url,
                            j.budget,
                            j.description,
                            j.posted_at.isoformat(),
                            ','.join(j.matched_keywords),
                        )
                        for j in jobs
                    ],
                )
                await conn.commit()
            return

        if self.engine == 'postgres':
            conn = await asyncpg.connect(self.dsn)
            try:
                await conn.executemany(
                    '''
                    INSERT INTO freelance_jobs
                    (source, remote_id, title, url, budget, description, posted_at, matched_keywords)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ''',
                    [
                        (
                            j.source,
                            j.remote_id,
                            j.title,
                            j.url,
                            j.budget,
                            j.description,
                            j.posted_at,
                            ','.join(j.matched_keywords),
                        )
                        for j in jobs
                    ],
                )
            finally:
                await conn.close()
            return

    async def save_scan_result(self, result: ScanResult) -> None:
        if self.engine == 'sqlite':
            db_path = Path(self.dsn)
            async with aiosqlite.connect(db_path) as conn:
                cursor = await conn.execute(
                    '''
                    INSERT INTO scan_runs (target, started_at, completed_at, blocked, blocked_reason, artifacts_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        result.target,
                        result.started_at.isoformat(),
                        result.completed_at.isoformat(),
                        int(result.blocked),
                        result.blocked_reason,
                        json.dumps(result.artifacts),
                    ),
                )
                scan_run_id = cursor.lastrowid
                await conn.executemany(
                    '''
                    INSERT INTO findings
                    (scan_run_id, target, title, severity, tool, confidence, validated, validation_notes, evidence_json, discovered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    [
                        (
                            scan_run_id,
                            f.target,
                            f.title,
                            f.severity,
                            f.tool,
                            f.confidence,
                            int(f.validated),
                            f.validation_notes,
                            json.dumps(f.evidence, default=str),
                            f.discovered_at.isoformat(),
                        )
                        for f in result.raw_findings
                    ],
                )
                await conn.commit()
            return

        if self.engine == 'postgres':
            conn = await asyncpg.connect(self.dsn)
            try:
                scan_run_id = await conn.fetchval(
                    '''
                    INSERT INTO scan_runs (target, started_at, completed_at, blocked, blocked_reason, artifacts_json)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                    ''',
                    result.target,
                    result.started_at,
                    result.completed_at,
                    result.blocked,
                    result.blocked_reason,
                    json.dumps(result.artifacts),
                )
                await conn.executemany(
                    '''
                    INSERT INTO findings
                    (scan_run_id, target, title, severity, tool, confidence, validated, validation_notes, evidence_json, discovered_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ''',
                    [
                        (
                            scan_run_id,
                            f.target,
                            f.title,
                            f.severity,
                            f.tool,
                            f.confidence,
                            f.validated,
                            f.validation_notes,
                            json.dumps(f.evidence, default=str),
                            f.discovered_at,
                        )
                        for f in result.raw_findings
                    ],
                )
            finally:
                await conn.close()
            return
