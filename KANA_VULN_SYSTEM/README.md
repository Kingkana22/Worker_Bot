# KANA_VULN_SYSTEM

Autonomous and modular DevSecOps framework for legal freelance job discovery and authorized vulnerability validation.

## Legal Notice

Use this project only for targets and programs where you have explicit permission.
All scanner operations should pass through the scope-checker and approved in-scope assets.

## Quick Start

1. Copy `configs/.env.example` to `configs/.env`.
2. Generate a master key and encrypt API secrets with:
   `python main.py encrypt-secret --value "your-api-token"`
3. Update `configs/app.yaml`.
4. Initialize DB schema:
   `python main.py db-init`
5. Run a scoped scan:
   `python main.py scan --target https://example.com --scope-file data/state/in_scope.txt`
