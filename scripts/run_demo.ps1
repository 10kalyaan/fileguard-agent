$ErrorActionPreference = "Stop"

python scripts/reset_demo.py
python -m pytest

$previewOutput = python -m fileguard.main preview --path ./demo_files/messy_downloads --rules-only
$previewOutput

$planLine = $previewOutput | Select-String -Pattern "Plan ID: "
$planId = ($planLine -replace "Plan ID: ", "").Trim()

if (-not $planId) {
    throw "Could not parse PLAN_ID from preview output."
}

Write-Host ""
Write-Host "Parsed PLAN_ID: $planId"
Write-Host ""

python -m fileguard.main approve $planId
python -m fileguard.main execute $planId
python -m fileguard.main rollback $planId
python -m fileguard.main audit $planId

