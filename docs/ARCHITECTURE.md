# Architecture

FileGuard is intentionally split into classification, planning, persistence, execution, and rollback layers. That separation keeps preview safe and makes execution depend on an approved stored plan rather than live ad hoc decisions.

## Flow

```text
User CLI
  |
  v
main.py
  |
  v
scanner.py -> extension_classifier.py -> claude_classifier.py / keyword_classifier.py
  |
  v
planner.py
  |
  v
db.py
  |
  v
executor.py <-> rollback.py
  |
  v
audit_log
```

## Modules

`scanner.py`: scans files safely and skips protected or sensitive files.

`extension_classifier.py`: performs deterministic top-level folder classification from file extensions.

`keyword_classifier.py`: provides rule-based semantic fallback.

`claude_classifier.py`: provides optional semantic classification for safe metadata only.

`planner.py`: creates dry-run movement plans and classification summaries.

`db.py`: stores plans, planned moves, timestamps, statuses, and audit logs in SQLite.

`executor.py`: moves files only after approval, with duplicate-safe destinations.

`rollback.py`: restores executed files back toward their original source paths.

`safety.py`: blocks protected paths, sensitive filenames, and unsafe move operations.

`main.py`: exposes the command-line interface.

## OpenClaw Skill Layer

Version 7 adds an OpenClaw skill layer.

- `skills/fileguard-agent/SKILL.md` contains workflow instructions and safety constraints.
- The agent calls FileGuard CLI commands.
- The Python engine remains the source of truth.
- A future plugin could expose typed commands, but it is unnecessary now.

## Classification And Execution Are Separate

Classification only proposes destinations. Execution only reads an approved stored plan. This prevents a classifier, including Claude, from directly performing file operations.
