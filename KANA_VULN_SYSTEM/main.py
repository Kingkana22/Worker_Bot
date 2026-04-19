from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger

from configs.settings import Settings, load_settings
from core.orchestrator import Orchestrator
from core.security import SecretManager
from data.db import DatabaseClient
from reporting.json_reporter import JSONReporter
from reporting.markdown_reporter import MarkdownReporter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='KANA_VULN_SYSTEM',
        description='Legal freelance scouting + authorized vulnerability scanning framework.',
    )
    parser.add_argument('--config', default='configs/app.yaml', help='Path to YAML config')
    parser.add_argument('--env-file', default='configs/.env', help='Path to env file')

    sub = parser.add_subparsers(dest='command', required=True)

    scout = sub.add_parser('scout', help='Find freelance jobs using official APIs')
    scout.add_argument('--keywords', nargs='+', required=True)
    scout.add_argument('--limit', type=int, default=20)
    scout.add_argument('--persist', action='store_true', help='Persist jobs to configured DB')

    scan = sub.add_parser('scan', help='Run authorized vulnerability scanning workflow')
    scan.add_argument('--target', required=True, help='URL or hostname to scan')
    scan.add_argument('--scope-file', required=True, help='File with in-scope entries')
    scan.add_argument('--severities', nargs='+', default=[])
    scan.add_argument('--output-dir', default='outputs/reports')
    scan.add_argument('--persist', action='store_true', help='Persist results to configured DB')
    scan.add_argument('--skip-nmap', action='store_true')
    scan.add_argument('--skip-subfinder', action='store_true')

    db_init = sub.add_parser('db-init', help='Initialize database schema')
    db_init.add_argument('--schema-dir', default='data/schema')

    enc = sub.add_parser('encrypt-secret', help='Encrypt a secret using KANA_MASTER_KEY')
    enc.add_argument('--value', required=True)

    return parser


def configure_logging(log_level: str) -> None:
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=''),
        colorize=True,
        level=log_level.upper(),
        format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>',
    )


async def handle_scout(args: argparse.Namespace, settings: Settings) -> int:
    orchestrator = Orchestrator(settings)
    agent = orchestrator.build_freelance_agent()

    jobs = await agent.find_jobs(keywords=args.keywords, limit=args.limit)
    logger.info('Freelance scout returned {} jobs', len(jobs))

    ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    report_name = f'jobs_{ts}'
    output_dir = Path('outputs/reports')

    md_path = MarkdownReporter(output_dir).write_jobs_report(report_name, jobs)
    json_path = JSONReporter(output_dir).write_jobs_report(report_name, jobs)
    logger.info('Reports written: {} and {}', md_path, json_path)

    if args.persist:
        db = DatabaseClient(settings.database.engine, settings.database.dsn)
        await db.save_jobs(jobs)
        logger.info('Jobs persisted to database')

    return 0


async def handle_scan(args: argparse.Namespace, settings: Settings) -> int:
    output_dir = Path(args.output_dir)
    scope_file = Path(args.scope_file)

    orchestrator = Orchestrator(settings)
    scanner = orchestrator.build_vuln_scanner_agent(scope_file=scope_file, output_dir=output_dir)

    severities = args.severities or settings.scanner.default_severities
    result = await scanner.scan_authorized_target(
        target=args.target,
        severities=severities,
        run_nmap=not args.skip_nmap,
        run_subfinder=not args.skip_subfinder,
    )

    ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    report_name = f'scan_{ts}'

    md_path = MarkdownReporter(output_dir).write_scan_report(report_name, result)
    json_path = JSONReporter(output_dir).write_scan_report(report_name, result)
    logger.info('Reports written: {} and {}', md_path, json_path)
    logger.info(
        'Scan summary target={} blocked={} raw_findings={} validated_findings={}',
        result.target,
        result.blocked,
        len(result.raw_findings),
        len(result.validated_findings),
    )

    if args.persist:
        db = DatabaseClient(settings.database.engine, settings.database.dsn)
        await db.save_scan_result(result)
        logger.info('Scan result persisted to database')

    return 0


async def handle_db_init(args: argparse.Namespace, settings: Settings) -> int:
    schema_dir = Path(args.schema_dir)
    schema_name = 'sqlite.sql' if settings.database.engine.lower() == 'sqlite' else 'postgres.sql'
    schema_path = schema_dir / schema_name

    db = DatabaseClient(settings.database.engine, settings.database.dsn)
    await db.initialize_schema(schema_path)
    logger.info('Initialized database using schema {}', schema_path)
    return 0


def handle_encrypt_secret(args: argparse.Namespace) -> int:
    manager = SecretManager.from_environment()
    encrypted = manager.encrypt(args.value)
    print(encrypted)
    return 0


async def async_main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == 'encrypt-secret':
        return handle_encrypt_secret(args)

    settings = load_settings(config_path=Path(args.config), env_path=Path(args.env_file))
    configure_logging(settings.app.log_level)

    if args.command == 'scout':
        return await handle_scout(args, settings)
    if args.command == 'scan':
        return await handle_scan(args, settings)
    if args.command == 'db-init':
        return await handle_db_init(args, settings)

    parser.print_help()
    return 1


if __name__ == '__main__':
    raise SystemExit(asyncio.run(async_main()))
