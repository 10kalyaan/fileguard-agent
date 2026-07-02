#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE="${REPO_ROOT}/skills/fileguard-agent"
DESTINATION="${HOME}/.openclaw/workspace/skills/fileguard-agent"

if [[ ! -f "${SOURCE}/SKILL.md" ]]; then
  echo "Missing source skill file: ${SOURCE}/SKILL.md" >&2
  exit 1
fi

mkdir -p "$(dirname "${DESTINATION}")"
rm -rf "${DESTINATION}"
cp -R "${SOURCE}" "${DESTINATION}"

echo "Installed FileGuard OpenClaw skill."
echo "Source: ${SOURCE}"
echo "Destination: ${DESTINATION}"
echo ""
echo "Next commands:"
echo "  openclaw skills list"
echo "  openclaw gateway restart"

