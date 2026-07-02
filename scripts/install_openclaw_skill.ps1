$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$source = Join-Path $repoRoot "skills\fileguard-agent"
$skillFile = Join-Path $source "SKILL.md"
$destination = Join-Path $HOME ".openclaw\workspace\skills\fileguard-agent"
$destinationParent = Split-Path -Parent $destination

if (-not (Test-Path $skillFile)) {
    throw "Missing source skill file: $skillFile"
}

New-Item -ItemType Directory -Force -Path $destinationParent | Out-Null

if (Test-Path $destination) {
    Remove-Item -LiteralPath $destination -Recurse -Force
}

Copy-Item -LiteralPath $source -Destination $destination -Recurse

Write-Host "Installed FileGuard OpenClaw skill."
Write-Host "Source: $source"
Write-Host "Destination: $destination"
Write-Host ""
Write-Host "Next commands:"
Write-Host "  openclaw skills list"
Write-Host "  openclaw gateway restart"

