# FileGuard Agent

FileGuard Agent is a local file organization tool. Version 2 keeps the V1 dry-run planner and adds approval-based execution with an audit log.

## V2 Features

- Scans direct files in a selected folder.
- Classifies files by extension and filename keywords.
- Creates a dry-run movement plan and saves it to SQLite.
- Requires explicit approval before moving files.
- Executes approved plans with duplicate-safe destination names.
- Writes audit entries for approvals, moves, skips, failures, and execution.
- Shows saved plans and audit history from the CLI.

## Safety Rules

- Preview is dry-run only.
- Files only move after a saved plan is approved and executed.
- FileGuard does not delete files.
- FileGuard does not overwrite files.
- If a destination exists, FileGuard creates a safe name like `resume_2.pdf`.
- V2 does not use Claude, OpenClaw, or external APIs.

## Important Warning

The command below physically moves files from the source folder into `Organized/`:

```powershell
python -m fileguard.main execute <PLAN_ID>
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

Show audit log entries:

```powershell
python -m fileguard.main audit <PLAN_ID>
```

All commands accept `--db ./fileguard.db`.

## Manual V2 Test Flow

Step 1:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads
```

Step 2:

Copy the printed plan id.

Step 3:

```powershell
python -m fileguard.main show-plan <PLAN_ID>
```

Step 4:

```powershell
python -m fileguard.main execute <PLAN_ID>
```

Expected: execution fails because the plan is not approved.

Step 5:

```powershell
python -m fileguard.main approve <PLAN_ID>
```

Step 6:

```powershell
python -m fileguard.main execute <PLAN_ID>
```

Expected: files move into `Organized/...` folders.

Step 7:

```powershell
python -m fileguard.main audit <PLAN_ID>
```

Expected: audit entries show approval, file moves, and plan execution.

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

