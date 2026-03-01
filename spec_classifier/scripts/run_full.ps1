# One-button run: pytest + batch per vendor. UTF-8.
# Usage: .\scripts\run_full.ps1 [-InputRoot path] [-OutputRoot path] [-Vendor dell|cisco] [-TestsOnly]
param(
    [string]$InputRoot = "",
    [string]$OutputRoot = "",
    [string]$Vendor = "",
    [switch]$TestsOnly
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# a) RepoRoot = directory containing main.py (walk up from script location)
$RepoRoot = Split-Path -Parent $PSScriptRoot
$MainPy = Join-Path $RepoRoot "main.py"
if (-not (Test-Path $MainPy)) {
    Write-Error "main.py not found at $MainPy"
}
Set-Location $RepoRoot

# b) Read temp_root from config.local.yaml (simple regex), default: $RepoRoot/temporary
$TempRoot = Join-Path $RepoRoot "temporary"
$ConfigLocal = Join-Path $RepoRoot "config.local.yaml"
if (Test-Path $ConfigLocal) {
    $content = Get-Content $ConfigLocal -Raw -Encoding UTF8
    if ($content -match 'temp_root:\s*["'']([^"'']+)["'']') {
        $TempRoot = $Matches[1].Trim()
    }
    if (-not $InputRoot -and ($content -match 'input_root:\s*["'']([^"'']+)["'']')) {
        $InputRoot = $Matches[1].Trim()
    }
    if (-not $OutputRoot -and ($content -match 'output_root:\s*["'']([^"'']+)["'']')) {
        $OutputRoot = $Matches[1].Trim()
    }
}
if (-not $InputRoot) { $InputRoot = Join-Path $RepoRoot "input" }
if (-not $OutputRoot) { $OutputRoot = Join-Path $RepoRoot "output" }

# c) Environment for Python cache
$PyCacheDir = Join-Path $TempRoot "__pycache__"
$env:PYTHONPYCACHEPREFIX = $PyCacheDir
if (-not (Test-Path $TempRoot)) { New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null }

# d) Timestamped diag folder
$DiagDir = Join-Path $RepoRoot "diag\runs\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $DiagDir -Force | Out-Null

# e) Pytest
$PytestCacheDir = Join-Path $TempRoot ".pytest_cache"
$pytestExit = 0
python -m pytest tests/ -v --tb=short --override-ini="cache_dir=$PytestCacheDir" 2>&1 | Tee-Object -FilePath (Join-Path $DiagDir "pytest.log")
$pytestExit = $LASTEXITCODE

$batchExit = 0
if (-not $TestsOnly) {
    $vendorsToRun = @()
    if ($Vendor) {
        $vendorsToRun = @($Vendor)
    } else {
        if (Test-Path (Join-Path $InputRoot "dell")) { $vendorsToRun += "dell" }
        if (Test-Path (Join-Path $InputRoot "cisco")) { $vendorsToRun += "cisco" }
    }
    foreach ($v in $vendorsToRun) {
        $vendorInput = Join-Path $InputRoot $v
        if (-not (Test-Path $vendorInput)) { continue }
        $xlsx = Get-ChildItem -Path $vendorInput -Filter "*.xlsx" -ErrorAction SilentlyContinue
        if (-not $xlsx) { continue }
        Write-Host "Batch vendor: $v"
        $batchLog = Join-Path $DiagDir "batch.log"
        python main.py --batch-dir $vendorInput --vendor $v --output-dir $OutputRoot 2>&1 | Tee-Object -Append -FilePath $batchLog
        if ($LASTEXITCODE -ne 0) { $batchExit = $LASTEXITCODE }
    }
}

# g) Summary
Write-Host ""
Write-Host "--- Summary ---"
Write-Host "pytest exit code: $pytestExit"
Write-Host "batch exit code: $batchExit"
Write-Host "Diag folder: $DiagDir"
Write-Host "Output root: $OutputRoot"

# h) Return non-zero if anything failed
if ($pytestExit -ne 0 -or $batchExit -ne 0) { exit 1 }
exit 0
