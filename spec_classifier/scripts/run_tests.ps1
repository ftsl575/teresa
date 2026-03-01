# Run pytest only; cache redirected to temp_root. UTF-8.
# Equivalent to run_full.ps1 -TestsOnly
param()

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$RepoRoot = Split-Path -Parent $PSScriptRoot
$MainPy = Join-Path $RepoRoot "main.py"
if (-not (Test-Path $MainPy)) { Write-Error "main.py not found at $MainPy" }
Set-Location $RepoRoot

$TempRoot = Join-Path $RepoRoot "temporary"
$ConfigLocal = Join-Path $RepoRoot "config.local.yaml"
if (Test-Path $ConfigLocal) {
    $content = Get-Content $ConfigLocal -Raw -Encoding UTF8
    if ($content -match 'temp_root:\s*["'']([^"'']+)["'']') { $TempRoot = $Matches[1].Trim() }
}
$env:PYTHONPYCACHEPREFIX = Join-Path $TempRoot "__pycache__"
if (-not (Test-Path $TempRoot)) { New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null }

$PytestCacheDir = Join-Path $TempRoot ".pytest_cache"
python -m pytest tests/ -v --tb=short --override-ini="cache_dir=$PytestCacheDir"
exit $LASTEXITCODE
