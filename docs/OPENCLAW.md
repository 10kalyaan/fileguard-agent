# OpenClaw Integration

## What OpenClaw Does

OpenClaw is the chat and agent layer. FileGuard remains the Python engine.

OpenClaw does not directly classify or move files by itself. The `fileguard-agent` skill teaches OpenClaw how to call FileGuard safely through the existing CLI.

```text
User chat
  |
  v
OpenClaw
  |
  v
fileguard-agent skill
  |
  v
FileGuard CLI
  |
  v
Scanner / Classifier / Planner / Executor / Rollback
```

## Why Skill, Not Plugin

FileGuard already has working CLI commands, tests, audit logs, approval gates, and rollback. The V7 integration only needs to teach workflow and safety rules.

A full plugin would be unnecessary for V7. A future plugin can expose typed tool APIs if the project needs a richer OpenClaw integration.

## Installation

Option A: Use workspace skill directly.

If OpenClaw is running from this repository as the workspace, it should discover:

```text
skills/fileguard-agent/SKILL.md
```

Option B: Copy skill to OpenClaw workspace.

PowerShell:

```powershell
.\scripts\install_openclaw_skill.ps1
```

macOS/Linux:

```bash
bash scripts/install_openclaw_skill.sh
```

OpenClaw may need:

```text
openclaw skills list
openclaw gateway restart
```

You may also need a new agent/chat session because skills may be snapshotted when a session starts.

## Example OpenClaw Commands

```text
Use /skill fileguard-agent to preview organize demo_files/messy_downloads.
Preview organize demo_files/messy_downloads rules-only.
Approve plan_...
Execute plan_...
Rollback plan_...
Audit plan_...
```

## Safety

- Preview first
- Explicit approval before execution
- No deletion
- No overwrite
- Rollback available
- Audit logs available
- Protected paths blocked
- No API keys in chat
- Demo folder first

## Limitations

- Current integration is skill-based, not a native plugin.
- It relies on Python CLI availability.
- OpenClaw must run in or have access to the repository workspace.
- The real Downloads folder should be tested only after the demo flow works.

