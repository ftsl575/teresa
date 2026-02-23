# Generate golden files: run main.py --save-golden for dl1-dl5.
# Run from repo root (dell_spec_classifier) or from scripts/; CWD is set to repo root.
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Get-Item $ScriptDir).Parent.FullName
Set-Location $Root

$items = @("dl1", "dl2", "dl3", "dl4", "dl5")
foreach ($d in $items) {
  $xlsx = "test_data\$d.xlsx"
  if (-not (Test-Path $xlsx)) {
    Write-Host "Skipping $d : $xlsx not found"
    continue
  }
  Write-Host "Generating golden for $d..."
  python main.py --save-golden --input $xlsx
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
Write-Host "Done. Golden files in golden/"
