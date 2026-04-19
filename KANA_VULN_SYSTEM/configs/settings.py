from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from core.security import SecretManager


@dataclass(slots=True)
class AppConfig:
    name: str
    log_level: str


@dataclass(slots=True)
class DatabaseConfig:
    engine: str
    dsn: str


@dataclass(slots=True)
class UpworkConfig:
    base_url: str
    api_token_env: str
    api_token: str


@dataclass(slots=True)
class HackerOneConfig:
    base_url: str
    username_env: str
    token_env: str
    username: str
    token: str


@dataclass(slots=True)
class BugcrowdConfig:
    base_url: str
    api_token_env: str
    api_token: str


@dataclass(slots=True)
class IntegrationsConfig:
    upwork: UpworkConfig
    hackerone: HackerOneConfig
    bugcrowd: BugcrowdConfig


@dataclass(slots=True)
class ScannerConfig:
    nuclei_binary: str
    nuclei_templates: str
    nmap_binary: str
    subfinder_binary: str
    default_severities: list[str]
    timeout_seconds: int


@dataclass(slots=True)
class Settings:
    app: AppConfig
    database: DatabaseConfig
    integrations: IntegrationsConfig
    scanner: ScannerConfig


def _read_secret(secret_name: str, secret_manager: SecretManager) -> str:
    return secret_manager.read_secret(secret_name)


def load_settings(config_path: Path, env_path: Path | None = None) -> Settings:
    if env_path is not None and env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

    raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding='utf-8'))
    secret_manager = SecretManager.from_environment()

    app_raw = raw['app']
    db_raw = raw['database']
    integ_raw = raw['integrations']
    scanner_raw = raw['scanner']

    upwork_raw = integ_raw['upwork']
    h1_raw = integ_raw['hackerone']
    bug_raw = integ_raw['bugcrowd']

    return Settings(
        app=AppConfig(name=app_raw['name'], log_level=app_raw.get('log_level', 'INFO')),
        database=DatabaseConfig(engine=db_raw['engine'], dsn=db_raw['dsn']),
        integrations=IntegrationsConfig(
            upwork=UpworkConfig(
                base_url=upwork_raw['base_url'],
                api_token_env=upwork_raw['api_token_env'],
                api_token=_read_secret(upwork_raw['api_token_env'], secret_manager),
            ),
            hackerone=HackerOneConfig(
                base_url=h1_raw['base_url'],
                username_env=h1_raw['username_env'],
                token_env=h1_raw['token_env'],
                username=_read_secret(h1_raw['username_env'], secret_manager),
                token=_read_secret(h1_raw['token_env'], secret_manager),
            ),
            bugcrowd=BugcrowdConfig(
                base_url=bug_raw['base_url'],
                api_token_env=bug_raw['api_token_env'],
                api_token=_read_secret(bug_raw['api_token_env'], secret_manager),
            ),
        ),
        scanner=ScannerConfig(
            nuclei_binary=scanner_raw.get('nuclei_binary', 'nuclei'),
            nuclei_templates=scanner_raw.get('nuclei_templates', ''),
            nmap_binary=scanner_raw.get('nmap_binary', 'nmap'),
            subfinder_binary=scanner_raw.get('subfinder_binary', 'subfinder'),
            default_severities=list(scanner_raw.get('default_severities', ['critical', 'high', 'medium', 'low'])),
            timeout_seconds=int(scanner_raw.get('timeout_seconds', 600)),
        ),
    )
