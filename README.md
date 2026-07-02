# FileGuard Agent

A permission-aware local file organization agent that uses extension-based grouping, Claude-first semantic classification, rule-based fallback, dry-run planning, approval-gated execution, audit logs, and rollback.

Current version: `0.7.0`

## Why I Built This

Local AI agents can be useful, but they become risky the moment they touch files. FileGuard explores how an agent-style workflow can organize local files without jumping straight to destructive automation.

The focus is not only classification. The real design goal is a safe workflow: preview first, store an auditable plan, require explicit approval, execute without overwriting, and support rollback.

## Features

- Folder scanning
- Extension-based top-level grouping
- Claude-first semantic subfolder classification
- Rule-based fallback when Claude is unavailable
- Rules-only mode
- Low-confidence Claude mode
- Dry-run plans
- Explicit approval before execution
- Duplicate-safe renaming
- Protected path blocking
- Audit logging
- Rollback support
- SQLite-backed plan storage

## Architecture

```text
User CLI
  |
  v
FileGuard CLI
  |
  v
Scanner
  |
  v
Extension Classifier
  |
  v
Claude / Rule Semantic Classifier
  |
  v
Planner
  |
  v
SQLite Plan Store
  |
  v
Approval Gate
  |
  v
Executor
  |
  v
Audit Log / Rollback
```

OpenClaw integration is planned as the next layer. OpenClaw will wrap this safe Python engine rather than replace it.

## Classification Strategy

1. Extension classification decides the top-level folder.
2. Claude classifies the semantic subfolder when available.
3. Rules fallback when Claude is unavailable, disabled, fails, or max calls are reached.
4. Claude never executes file operations.
5. Claude never changes top-level extension grouping.

Example:

```text
Kalyaan_Resume_Final.pdf
-> Documents/PDFs/Resumes
```

## Safety Model

- Preview first
- Approval required before execution
- No deletion
- No overwriting
- Duplicate-safe filenames
- Protected paths blocked
- Sensitive filenames blocked
- Audit trail
- Rollback

## CLI Usage

Install:

```powershell
pip install -r requirements.txt
```

Run tests:

```powershell
python -m pytest
```

Rule-only preview:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --rules-only
```

Default Claude-first preview:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads
```

Low-confidence mode:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --low-confidence
```

Show plan:

```powershell
python -m fileguard.main show-plan <PLAN_ID>
```

Approve:

```powershell
python -m fileguard.main approve <PLAN_ID>
```

Execute:

```powershell
python -m fileguard.main execute <PLAN_ID>
```

Rollback:

```powershell
python -m fileguard.main rollback <PLAN_ID>
```

Audit:

```powershell
python -m fileguard.main audit <PLAN_ID>
```

Version:

```powershell
python -m fileguard.main version
```

## Claude Setup

Claude API usage is optional. Without an API key, FileGuard falls back to rules. Do not commit `.env`.

PowerShell example:

```powershell
$env:FILEGUARD_CLAUDE_ENABLED="auto"
$env:ANTHROPIC_API_KEY="your_key_here"
$env:FILEGUARD_CLAUDE_MODEL="claude-haiku-4-5-20251001"
$env:FILEGUARD_MAX_CLAUDE_CALLS="5"
```

## Demo Flow

Reset the demo:

```powershell
python scripts/reset_demo.py
```

Run a full demo:

```powershell
.\scripts\run_demo.ps1
```

Manual flow:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --rules-only
python -m fileguard.main approve <PLAN_ID>
python -m fileguard.main execute <PLAN_ID>
python -m fileguard.main rollback <PLAN_ID>
python -m fileguard.main audit <PLAN_ID>
```

## OpenClaw Integration

V7 adds an OpenClaw skill integration. OpenClaw wraps the FileGuard CLI and follows the preview-first workflow described in `skills/fileguard-agent/SKILL.md`.

Install the skill:

PowerShell:

```powershell
.\scripts\install_openclaw_skill.ps1
```

macOS/Linux:

```bash
bash scripts/install_openclaw_skill.sh
```

Verify:

```text
openclaw skills list
```

Restart or start a new session:

```text
openclaw gateway restart
```

Example OpenClaw prompt:

```text
Use FileGuard to preview organize demo_files/messy_downloads with rules only.
```

## Roadmap

- V1 Dry-run planner
- V2 Approval-based execution
- V3 Rollback and safety guardrails
- V4 Optional Claude semantic classification
- V5 Claude-first classification with rules fallback
- V6 Polish and demo
- V7 OpenClaw skill integration

## Resume Bullet

Built a permission-aware local file organization agent using Python, SQLite, and Claude-assisted semantic classification, with dry-run planning, approval-gated execution, protected-path blocking, audit logs, and rollback support.
