from __future__ import annotations

from core.scope_checker import ScopeChecker
from core.task_models import Finding


_SEVERITY_ORDER: dict[str, int] = {
    'info': 0,
    'low': 1,
    'medium': 2,
    'high': 3,
    'critical': 4,
}


class FindingValidator:
    def __init__(self, scope_checker: ScopeChecker, min_severity: str = 'low') -> None:
        self.scope_checker = scope_checker
        self.min_severity = min_severity.lower()

    def validate(self, finding: Finding) -> tuple[bool, str]:
        if not self.scope_checker.is_target_allowed(finding.target):
            return False, 'Target is out of approved scope.'

        severity_value = _SEVERITY_ORDER.get(finding.severity.lower(), -1)
        minimum_value = _SEVERITY_ORDER.get(self.min_severity, 1)
        if severity_value < minimum_value:
            return False, f'Severity {finding.severity} is below minimum threshold {self.min_severity}.'

        if not finding.title.strip():
            return False, 'Missing finding title/evidence context.'

        if finding.confidence < 0.5:
            return False, 'Confidence score below 0.5 threshold.'

        return True, 'Validated for reporting.'
