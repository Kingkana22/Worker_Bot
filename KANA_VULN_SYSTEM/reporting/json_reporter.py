from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from core.task_models import JobPosting, ScanResult


class JSONReporter:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_scan_report(self, report_name: str, scan_result: ScanResult) -> Path:
        output_path = self.output_dir / f'{report_name}.json'
        payload = asdict(scan_result)
        output_path.write_text(json.dumps(payload, indent=2, default=str), encoding='utf-8')
        return output_path

    def write_jobs_report(self, report_name: str, jobs: list[JobPosting]) -> Path:
        output_path = self.output_dir / f'{report_name}.json'
        payload = [asdict(job) for job in jobs]
        output_path.write_text(json.dumps(payload, indent=2, default=str), encoding='utf-8')
        return output_path
