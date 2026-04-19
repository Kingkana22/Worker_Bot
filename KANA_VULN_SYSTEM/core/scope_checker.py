from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse


class ScopeChecker:
    def __init__(self, allowed_patterns: set[str]) -> None:
        self._allowed_patterns = {pattern.strip().lower() for pattern in allowed_patterns if pattern.strip()}

    @classmethod
    def from_file(cls, scope_file: Path) -> 'ScopeChecker':
        patterns: set[str] = set()
        for line in scope_file.read_text(encoding='utf-8').splitlines():
            cleaned = line.strip()
            if not cleaned or cleaned.startswith('#'):
                continue
            patterns.add(cleaned)
        return cls(patterns)

    def is_target_allowed(self, target: str) -> bool:
        parsed = urlparse(target)
        host = (parsed.hostname or target).lower().strip()

        for pattern in self._allowed_patterns:
            p = pattern.lower()
            if p.startswith('*.'):
                suffix = p[2:]
                if host.endswith(f'.{suffix}'):
                    return True
            elif host == p or host.endswith(f'.{p}'):
                return True

        return False

    def describe(self) -> list[str]:
        return sorted(self._allowed_patterns)
