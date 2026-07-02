# FileGuard Agent

FileGuard Agent is a local file organization tool. Version 3 keeps the V1 dry-run planner and V2 approval-based execution, then adds rollback and stronger safety guardrails.

## Current Roadmap

- V1: dry-run planner
- V2: approval-based execution
- V3: rollback and safety
- V4: Claude-assisted classification
- V5: polish and docs
- V6: OpenClaw integration

## V3 Features

- Scans direct files in a selected folder.
- Skips protected or sensitive files during scanning and planning.
- Classifies files by extension and filename keywords.
- Creates a dry-run movement plan and saves it to SQLite.
- Requires explicit approval before moving files.
- Executes approved plans with duplicate-safe destination names.
- Rolls back executed plans by moving files back to their original source paths.
- Writes audit entries for approvals, execution, skips, failures, rollback start, restores, and rollback completion.
- Provides a `reset-demo` helper to recreate the original empty demo files.

## Safety Guardrails

FileGuard does not delete files and does not overwrite files. If a destination already exists, it creates a safe filename such as `resume_2.pdf`. If rollback finds the original source path occupied, it restores to a safe filename such as `resume_rollback_2.pdf`.

Protected path keywords:

```text
.ssh
.aws
.gnupg
.git
node_modules
__pycache__
.venv
venv
```

Protected filenames:

```text
.env
.env.local
.env.production
id_rsa
id_rsa.pub
credentials
credentials.json
config.json
```

Protected system paths include common Windows and Unix locations such as `C:\Windows`, `C:\Program Files`, `/etc`, `/usr`, `/bin`, `/sbin`, and `/var`.

## Important Warnings

Preview is dry-run only:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads
```

Execution physically moves files from the source folder into `Organized/`:

```powershell
python -m fileguard.main execute <PLAN_ID>
```

Rollback physically moves files back toward their original source paths:

```powershell
python -m fileguard.main rollback <PLAN_ID>
```

Do not run execution on your real Downloads folder yet. Use the demo folder or a temporary test folder first.

## Install

```powershell
pip install -r requirements.txt
```

## Run Tests

```powershell
python -m pytest
```

## CLI Usage

Create a dry-run preview plan:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads
```

Use a custom output root or database:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --output-root ./Organized --db ./fileguard.db
```

Show a saved plan:

```powershell
python -m fileguard.main show-plan <PLAN_ID>
```

Approve a saved preview plan:

```powershell
python -m fileguard.main approve <PLAN_ID>
```

Execute an approved plan:

```powershell
python -m fileguard.main execute <PLAN_ID>
```

Rollback an executed plan:

```powershell
python -m fileguard.main rollback <PLAN_ID>
```

Show audit log entries:

```powershell
python -m fileguard.main audit <PLAN_ID>
```

Recreate original empty demo files:

```powershell
python -m fileguard.main reset-demo
```

All plan commands accept `--db ./fileguard.db`.

## Manual V3 Test Flow

Step 0:

If `demo_files/messy_downloads` is empty because V2 moved the files, run:

```powershell
python -m fileguard.main reset-demo
```

Step 1:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads
```

Step 2:

Copy the printed plan id.

Step 3:

```powershell
python -m fileguard.main approve <PLAN_ID>
```

Step 4:

```powershell
python -m fileguard.main execute <PLAN_ID>
```

Expected: files move into `Organized/...`.

Step 5:

```powershell
python -m fileguard.main rollback <PLAN_ID>
```

Expected: files move back to `demo_files/messy_downloads`.

Step 6:

```powershell
python -m fileguard.main show-plan <PLAN_ID>
```

Expected: plan status should be `rolled_back`.

Step 7:

```powershell
python -m fileguard.main audit <PLAN_ID>
```

Expected: audit shows approval, execution, file moves, rollback start, file restores, and plan rolled back.

## Example Preview Output

```text
Plan ID: plan_20260702_111457
Files scanned: 10

- C:\path\to\demo_files\messy_downloads\Kalyaan_Resume_Final.pdf
  -> Organized\Documents\PDFs\Resumes\Kalyaan_Resume_Final.pdf
  confidence: 0.90
  reason: Matched extension .pdf to Documents/PDFs; Matched keyword 'resume' for Resumes

Dry run only. No files were moved.
```

