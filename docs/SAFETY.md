# Safety

FileGuard is designed around conservative local file operations.

## Principles

- No automatic execution
- Dry-run first
- Explicit approval
- No delete operation
- No overwrite operation
- Duplicate-safe renaming
- Protected path blocking
- Sensitive file blocking
- Audit logs
- Rollback

## Protected Examples

Protected path keywords:

- `.ssh`
- `.aws`
- `.git`
- `node_modules`

Sensitive filenames:

- `.env`
- `id_rsa`

Protected system locations:

- `C:\Windows`
- `C:\Program Files`
- `/etc`
- `/usr`
- `/bin`

## Claude Metadata Boundary

Claude only receives safe file metadata:

- filename
- extension
- top-level folder

The current version does not send full absolute paths or file contents to Claude.

