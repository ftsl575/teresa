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

# Helper: run a native command with stderr merged into stdout so PS 5.1 does not create
# NativeCommandError records from log/warning output. Streams output to console, optionally
# tees to a file, and returns the process exit code (caller must exit non-zero on failure).
function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Executable,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [string]$TeePath = "",
        [switch]$AppendTee
    )
    $prevEap = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = & $Executable @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $prevEap
    }
    # Normalize: in PS 5.1, stderr lines from 2>&1 can be ErrorRecord; convert to string for display/log
    $lines = $output | ForEach-Object { if ($_ -is [System.Management.Automation.ErrorRecord]) { $_.ToString() } else { $_ } }
    # Stream merged stdout+stderr to console (do not treat as PowerShell errors)
    $lines | ForEach-Object { Write-Host $_ }
    if ($TeePath) {
        if ($AppendTee) {
            $lines | Out-File -FilePath $TeePath -Append -Encoding utf8
        } else {
            $lines | Out-File -FilePath $TeePath -Encoding utf8
        }
    }
    return $exitCode
}

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

# e) Pytest (stderr merged to stdout via Invoke-Native so warnings do not trigger NativeCommandError)
$PytestCacheDir = Join-Path $TempRoot ".pytest_cache"
$pytestExit = Invoke-Native -Executable "python" -Arguments @("-m", "pytest", "tests/", "-v", "--tb=short", "--override-ini=cache_dir=$PytestCacheDir") -TeePath (Join-Path $DiagDir "pytest.log")
if ($pytestExit -ne 0) {
    Write-Host "pytest failed with exit code $pytestExit"
    exit [Math]::Min(255, [Math]::Max(1, $pytestExit))
}

$batchExit = 0
if (-not $TestsOnly) {
    $vendorsToRun = @()
    if ($Vendor) {
        $vendorsToRun = @($Vendor)
    } else {
        if (Test-Path (Join-Path $InputRoot "dell")) { $vendorsToRun += "dell" }
        if (Test-Path (Join-Path $InputRoot "cisco")) { $vendorsToRun += "cisco" }
    }
    $batchLog = Join-Path $DiagDir "batch.log"
    foreach ($v in $vendorsToRun) {
        $vendorInput = Join-Path $InputRoot $v
        if (-not (Test-Path $vendorInput)) { continue }
        $xlsx = Get-ChildItem -Path $vendorInput -Filter "*.xlsx" -ErrorAction SilentlyContinue
        if (-not $xlsx) { continue }
        Write-Host "Batch vendor: $v"
        $batchExit = Invoke-Native -Executable "python" -Arguments @("main.py", "--batch-dir", $vendorInput, "--vendor", $v, "--output-dir", $OutputRoot) -TeePath $batchLog -AppendTee
        if ($batchExit -ne 0) {
            Write-Host "Batch failed (vendor $v) with exit code $batchExit"
            exit [Math]::Min(255, [Math]::Max(1, $batchExit))
        }
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
