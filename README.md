# FileGuard Agent

FileGuard Agent is a local file organization tool. Version 5 keeps dry-run planning, approval-based execution, rollback, safety guardrails, and audit logs, then makes Claude-first semantic sorting the default when an Anthropic API key is available.

## Current Roadmap

- V1: dry-run planner
- V2: approval-based execution
- V3: rollback and safety guardrails
- V4: optional Claude semantic classification
- V5: Claude-first classification with rules fallback
- V6: project polish and demo
- V7: OpenClaw integration

## V5 Classification Behavior

Top-level folders are always deterministic and rule-based by extension. Claude can only choose the semantic subfolder.

Supported preview modes:

- `claude-first`: default. Uses Claude when available, falls back to rules when unavailable, disabled, missing an API key, failing, or over the max call limit.
- `rules-only`: never calls Claude and only uses keyword rules.
- `low-confidence`: V4 smart behavior. Uses rules first, then calls Claude only for low-confidence rule matches.

Claude receives only safe metadata: filename, extension, and already-decided top-level folder. FileGuard does not send absolute source paths, protected files, API keys, or file contents to Claude.

## Safety Guardrails

Preview is dry-run only. Claude classification only happens during preview/plan creation and never executes file operations.

FileGuard does not delete files and does not overwrite files. Execution still requires approval. Rollback still restores executed plans.

Protected path keywords include `.ssh`, `.aws`, `.gnupg`, `.git`, `node_modules`, `__pycache__`, `.venv`, and `venv`.

Protected filenames include `.env`, `.env.local`, `.env.production`, `id_rsa`, `id_rsa.pub`, `credentials`, `credentials.json`, and `config.json`.

Do not run execution on your real Downloads folder yet. Use the demo folder or a temporary test folder first.

## Install

```powershell
pip install -r requirements.txt
```

## Optional Claude Setup

Copy `.env.example` to `.env` if you want a template. The app reads environment variables directly.

PowerShell:

```powershell
$env:FILEGUARD_CLAUDE_ENABLED="auto"
$env:ANTHROPIC_API_KEY="your_key_here"
$env:FILEGUARD_CLAUDE_MODEL="claude-haiku-4-5-20251001"
$env:FILEGUARD_MAX_CLAUDE_CALLS="5"
```

## Preview Examples

Default Claude-first mode:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads
```

Rules-only mode:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --rules-only
```

Low-confidence mode:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --low-confidence
```

Backward-compatible smart alias:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --smart
```

## Plan Commands

```powershell
python -m fileguard.main show-plan <PLAN_ID>
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

## Manual V5 Tests

Test 1: unit tests

```powershell
python -m pytest
```

Test 2: default preview without API key

```powershell
Remove-Item Env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:FILEGUARD_CLAUDE_ENABLED -ErrorAction SilentlyContinue
python -m fileguard.main preview --path ./demo_files/messy_downloads
```

Expected: app does not crash, reports Claude-first fallback to rules, dry run only, and no files are moved.

Test 3: rules-only mode

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --rules-only
```

Expected: no Claude calls, classifiers are `rules`, and no files are moved.

Test 4: Claude-first real test, optional

```powershell
$env:FILEGUARD_CLAUDE_ENABLED="auto"
$env:ANTHROPIC_API_KEY="your_real_key_here"
$env:FILEGUARD_CLAUDE_MODEL="claude-haiku-4-5-20251001"
$env:FILEGUARD_MAX_CLAUDE_CALLS="5"
python -m fileguard.main preview --path ./demo_files/messy_downloads
```

Expected: Claude calls used is greater than 0 and at most 5, some files show `classifier: claude`, remaining files may show `rules_fallback` if max calls is reached, dry run only, and no files are moved.

Test 5: approval, execution, rollback, audit

```powershell
python -m fileguard.main approve <PLAN_ID>
python -m fileguard.main execute <PLAN_ID>
python -m fileguard.main rollback <PLAN_ID>
python -m fileguard.main audit <PLAN_ID>
```

Expected: execution still requires approval, files move only after approval, rollback restores files, and audit logs include actions.

