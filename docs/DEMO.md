# Demo

Reset the demo state first:

```powershell
python scripts/reset_demo.py
```

## Step 1: Preview

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --rules-only
```

Expected:

- A plan is created.
- No files are moved.

## Step 2: Approve

```powershell
python -m fileguard.main approve <PLAN_ID>
```

Expected:

- The plan is approved.
- No files are moved yet.

## Step 3: Execute

```powershell
python -m fileguard.main execute <PLAN_ID>
```

Expected:

- Files move into `Organized/`.

## Step 4: Rollback

```powershell
python -m fileguard.main rollback <PLAN_ID>
```

Expected:

- Files are restored to the demo folder.

## Step 5: Audit

```powershell
python -m fileguard.main audit <PLAN_ID>
```

Expected:

- Approval, execution, file moves, rollback start, restore, and completion entries are shown.

## Optional Claude-First Demo

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads
```

Without an API key, FileGuard falls back to rules. With an API key, Claude classifies semantic subfolders while extension grouping remains deterministic.

