# FileGuard Agent

FileGuard Agent is a local file organization tool. Version 4 keeps the V1 dry-run planner, V2 approval-based execution, and V3 rollback/safety guardrails, then adds optional Claude-assisted semantic classification for low-confidence files.

## Current Roadmap

- V1: dry-run planner
- V2: approval-based execution
- V3: rollback and safety
- V4: Claude-assisted classification
- V5: polish and docs
- V6: OpenClaw integration

## V4 Features

- Default mode is free, local, and rule-based.
- Smart mode can optionally use Claude for low-confidence semantic classification.
- Claude is disabled by default and never required for normal operation.
- Missing API keys do not break preview.
- Claude never changes the top-level extension folder.
- API calls are capped with `FILEGUARD_MAX_CLAUDE_CALLS`.
- Tests mock Claude and do not call the real API.
- Preview is still dry-run only.
- Execution still requires approval.
- Rollback still restores executed plans.

## Safety Guardrails

FileGuard does not delete files and does not overwrite files. If a destination already exists, it creates a safe filename such as `resume_2.pdf`. If rollback finds the original source path occupied, it restores to a safe filename such as `resume_rollback_2.pdf`.

Protected path keywords include `.ssh`, `.aws`, `.gnupg`, `.git`, `node_modules`, `__pycache__`, `.venv`, and `venv`.

Protected filenames include `.env`, `.env.local`, `.env.production`, `id_rsa`, `id_rsa.pub`, `credentials`, `credentials.json`, and `config.json`.

Protected system paths include common Windows and Unix locations such as `C:\Windows`, `C:\Program Files`, `/etc`, `/usr`, `/bin`, `/sbin`, and `/var`.

## Install

```powershell
pip install -r requirements.txt
```

## Optional Claude Config

Copy `.env.example` to `.env` if you want a template. The app reads environment variables directly.

PowerShell example:

```powershell
$env:FILEGUARD_CLAUDE_ENABLED="true"
$env:ANTHROPIC_API_KEY="your_key_here"
$env:FILEGUARD_MAX_CLAUDE_CALLS="5"
```

Rule-only mode:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads
```

Smart mode:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --smart
```

## CLI Usage

Create a dry-run preview plan:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads
```

Use smart mode:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --smart
```

Show a saved plan:

```powershell
python -m fileguard.main show-plan <PLAN_ID>
```

Approve, execute, audit, and rollback:

```powershell
python -m fileguard.main approve <PLAN_ID>
python -m fileguard.main execute <PLAN_ID>
python -m fileguard.main audit <PLAN_ID>
python -m fileguard.main rollback <PLAN_ID>
```

Recreate original empty demo files:

```powershell
python -m fileguard.main reset-demo
```

All plan commands accept `--db ./fileguard.db`.

## Manual V4 Tests

Test 1: normal rule-based mode

```powershell
python -m pytest
python -m fileguard.main preview --path ./demo_files/messy_downloads
```

Expected: tests pass, preview works, no Claude calls, and no files are moved.

Test 2: smart mode without API key

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --smart
```

Expected: the app does not crash, prints a Claude disabled or missing key message, falls back to rule-based classification, and no files are moved.

Test 3: smart mode with API key, optional

```powershell
$env:FILEGUARD_CLAUDE_ENABLED="true"
$env:ANTHROPIC_API_KEY="your_key_here"
$env:FILEGUARD_MAX_CLAUDE_CALLS="5"
python -m fileguard.main preview --path ./demo_files/messy_downloads --smart
```

Expected: Claude only runs for low-confidence files, high-confidence files stay rule-based, output shows Claude calls used, and no files are moved.

## Execution And Rollback Warning

Preview is dry-run only. Claude classification only happens during preview/plan creation and never executes file operations.

Execution physically moves files from the source folder into `Organized/`:

```powershell
python -m fileguard.main execute <PLAN_ID>
```

Rollback physically moves files back toward their original source paths:

```powershell
python -m fileguard.main rollback <PLAN_ID>
```

Do not run execution on your real Downloads folder yet. Use the demo folder or a temporary test folder first.

