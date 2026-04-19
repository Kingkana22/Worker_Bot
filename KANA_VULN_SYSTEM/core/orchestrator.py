from __future__ import annotations

from pathlib import Path

from agents.freelance_scout.scout import FreelanceScoutAgent
from agents.vulnerability_scanner.nmap_wrapper import NmapWrapper
from agents.vulnerability_scanner.nuclei_scanner import NucleiScanner
from agents.vulnerability_scanner.scanner_agent import VulnerabilityScannerAgent
from agents.vulnerability_scanner.subfinder_wrapper import SubfinderWrapper
from configs.settings import Settings
from core.scope_checker import ScopeChecker
from core.validator import FindingValidator
from integrations.upwork_api import UpworkAPI


class Orchestrator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def build_freelance_agent(self) -> FreelanceScoutAgent:
        upwork = UpworkAPI(
            base_url=self.settings.integrations.upwork.base_url,
            api_token=self.settings.integrations.upwork.api_token,
        )
        return FreelanceScoutAgent(upwork_api=upwork)

    def build_vuln_scanner_agent(self, scope_file: Path, output_dir: Path) -> VulnerabilityScannerAgent:
        checker = ScopeChecker.from_file(scope_file)
        validator = FindingValidator(scope_checker=checker, min_severity='low')

        nuclei = NucleiScanner(
            binary_path=self.settings.scanner.nuclei_binary,
            templates_dir=self.settings.scanner.nuclei_templates,
            output_dir=output_dir,
            timeout_seconds=self.settings.scanner.timeout_seconds,
        )
        nmap = NmapWrapper(
            binary_path=self.settings.scanner.nmap_binary,
            output_dir=output_dir,
            timeout_seconds=self.settings.scanner.timeout_seconds,
        )
        subfinder = SubfinderWrapper(
            binary_path=self.settings.scanner.subfinder_binary,
            timeout_seconds=self.settings.scanner.timeout_seconds,
        )

        return VulnerabilityScannerAgent(
            scope_checker=checker,
            validator=validator,
            nuclei_scanner=nuclei,
            nmap_wrapper=nmap,
            subfinder_wrapper=subfinder,
        )
