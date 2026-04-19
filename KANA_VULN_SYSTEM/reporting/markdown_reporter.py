from __future__ import annotations

from pathlib import Path

from core.task_models import JobPosting, ScanResult


class MarkdownReporter:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_scan_report(self, report_name: str, scan_result: ScanResult) -> Path:
        output_path = self.output_dir / f'{report_name}.md'
        lines: list[str] = []
        lines.append(f'# Scan Report: {scan_result.target}')
        lines.append('')
        lines.append(f'- Started: {scan_result.started_at.isoformat()}')
        lines.append(f'- Completed: {scan_result.completed_at.isoformat()}')
        lines.append(f'- Blocked: {scan_result.blocked}')
        if scan_result.blocked_reason:
            lines.append(f'- Blocked Reason: {scan_result.blocked_reason}')
        lines.append('')
        lines.append('## Validated Findings')
        lines.append('')

        if not scan_result.validated_findings:
            lines.append('No validated findings.')
        else:
            for finding in scan_result.validated_findings:
                lines.append(f'### {finding.title}')
                lines.append(f'- Severity: {finding.severity}')
                lines.append(f'- Tool: {finding.tool}')
                lines.append(f'- Target: {finding.target}')
                lines.append(f'- Confidence: {finding.confidence}')
                lines.append(f'- Notes: {finding.validation_notes}')
                lines.append('')

        lines.append('## Artifacts')
        lines.append('')
        for key, value in scan_result.artifacts.items():
            lines.append(f'- {key}: {value}')

        output_path.write_text('\n'.join(lines), encoding='utf-8')
        return output_path

    def write_jobs_report(self, report_name: str, jobs: list[JobPosting]) -> Path:
        output_path = self.output_dir / f'{report_name}.md'
        lines: list[str] = ['# Freelance Jobs Report', '']
        if not jobs:
            lines.append('No jobs returned from API.')
        for job in jobs:
            lines.append(f'## {job.title}')
            lines.append(f'- Source: {job.source}')
            lines.append(f'- URL: {job.url}')
            lines.append(f'- Budget: {job.budget}')
            lines.append(f"- Matched Keywords: {', '.join(job.matched_keywords) if job.matched_keywords else 'None'}")
            lines.append('')
            lines.append(job.description)
            lines.append('')
        output_path.write_text('\n'.join(lines), encoding='utf-8')
        return output_path
