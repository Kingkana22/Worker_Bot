from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class JobPosting:
    source: str
    remote_id: str
    title: str
    url: str
    budget: str
    description: str
    posted_at: datetime
    matched_keywords: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Finding:
    target: str
    title: str
    severity: str
    tool: str
    evidence: dict[str, Any]
    confidence: float
    validated: bool = False
    validation_notes: str = ''
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class ScanResult:
    target: str
    started_at: datetime
    completed_at: datetime
    raw_findings: list[Finding] = field(default_factory=list)
    validated_findings: list[Finding] = field(default_factory=list)
    blocked: bool = False
    blocked_reason: str = ''
    artifacts: dict[str, str] = field(default_factory=dict)
