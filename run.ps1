# =============================================================================
# teresa: единая точка запуска
# Заменяет: run_audit.ps1, scripts/run_full.ps1, scripts/run_tests.ps1
#
# Использование:
#   .\run.ps1                              # full pipeline + AI audit + cluster + tests
#   .\run.ps1 -NoAi                        # full pipeline + rule-only audit (без OpenAI)
#   .\run.ps1 -Vendor dell                 # только dell, остальное как обычно
#   .\run.ps1 -TestsOnly                   # только pytest
#   .\run.ps1 -SkipTests                   # full без pytest в конце
#   .\run.ps1 -Vendor huawei -NoAi -SkipTests  # минимальный smoke на одном вендоре
# =============================================================================

param(
    [string]$Vendor = "",
    [switch]$NoAi,
    [switch]$TestsOnly,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ── Self-locating paths (не привязаны к C:\Users\G) ─────────────────────────
$RepoRoot   = $PSScriptRoot
$SpecDir    = Join-Path $RepoRoot "spec_classifier"
$MainPy     = Join-Path $SpecDir  "main.py"
if (-not (Test-Path $MainPy)) {
    Write-Error "main.py not found at $MainPy. run.ps1 must be in repo root next to spec_classifier/."
}

# Read INPUT/OUTPUT from config.local.yaml (or use defaults under user's Desktop).
$InputRoot  = "$env:USERPROFILE\Desktop\INPUT"
$OutputRoot = "$env:USERPROFILE\Desktop\OUTPUT"
$ConfigLocal = Join-Path $SpecDir "config.local.yaml"
if (Test-Path $ConfigLocal) {
    $cfg = Get-Content $ConfigLocal -Raw -Encoding UTF8
    if ($cfg -match '(?m)^\s*input_root:\s*["'']?([^"''\r\n]+)["'']?\s*$')  { $InputRoot  = $Matches[1].Trim() }
    if ($cfg -match '(?m)^\s*output_root:\s*["'']?([^"''\r\n]+)["'']?\s*$') { $OutputRoot = $Matches[1].Trim() }
}

Set-Location $SpecDir

# Active vendors (kept here as single source of truth for the script).
# To add xfusion later: just append "xfusion" to this list once src/vendors/xfusion/ is ready.
$ALL_VENDORS = @("dell", "cisco", "hpe", "lenovo", "huawei")

if ($Vendor) {
    if ($ALL_VENDORS -notcontains $Vendor) {
        Write-Host "Unknown vendor: $Vendor. Known: $($ALL_VENDORS -join ', ')" -ForegroundColor Red
        exit 2
    }
    $VendorsToRun = @($Vendor)
} else {
    $VendorsToRun = $ALL_VENDORS
}

# ── Header ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " teresa run" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " Repo:     $RepoRoot"
Write-Host " Input:    $InputRoot"
Write-Host " Output:   $OutputRoot"
Write-Host " Vendors:  $($VendorsToRun -join ', ')"
Write-Host " AI audit: $(if ($NoAi) { 'OFF (rule-based only)' } else { 'ON (gpt-4o-mini)' })"
Write-Host " Tests:    $(if ($TestsOnly) { 'tests only' } elseif ($SkipTests) { 'skipped' } else { 'after pipeline' })"
Write-Host "=================================================================" -ForegroundColor Cyan

# ── 0) Tests-only short-circuit ─────────────────────────────────────────────
if ($TestsOnly) {
    Write-Host ""
    Write-Host "=== pytest (tests only) ===" -ForegroundColor Cyan
    python -m pytest tests/ -v --tb=short
    exit $LASTEXITCODE
}

# ── 1) OpenAI key (only if AI audit needed) ─────────────────────────────────
if (-not $NoAi) {
    if (-not $env:OPENAI_API_KEY) {
        Write-Host ""
        Write-Host "OPENAI_API_KEY not found in environment." -ForegroundColor Yellow
        $key = Read-Host "Enter OpenAI API Key (or press Ctrl+C to abort)" -AsSecureString
        $env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($key)
        )
    } else {
        Write-Host "OPENAI_API_KEY found in environment." -ForegroundColor Green
    }
}

# ── 2) Pipeline per vendor ──────────────────────────────────────────────────
foreach ($v in $VendorsToRun) {
    $vDir = Join-Path $InputRoot $v
    if (-not (Test-Path $vDir)) {
        Write-Host ""
        Write-Host "=== Pipeline: $v — SKIP (no input dir at $vDir) ===" -ForegroundColor Yellow
        continue
    }
    $xlsx = Get-ChildItem -Path $vDir -Filter "*.xlsx" -ErrorAction SilentlyContinue
    if (-not $xlsx) {
        Write-Host ""
        Write-Host "=== Pipeline: $v — SKIP (no .xlsx in $vDir) ===" -ForegroundColor Yellow
        continue
    }
    Write-Host ""
    Write-Host "=== Pipeline: $v ($($xlsx.Count) files) ===" -ForegroundColor Cyan
    python main.py --batch-dir $vDir --vendor $v --output-dir $OutputRoot
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Pipeline failed for $v (exit $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# ── 3) Audit (rule-based + optional AI) ─────────────────────────────────────
Write-Host ""
Write-Host "=== batch_audit: rule-based (no AI) ===" -ForegroundColor Cyan
python batch_audit.py --output-dir $OutputRoot --no-ai
if ($LASTEXITCODE -ne 0) {
    Write-Host "Rule-based audit failed (exit $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}

if (-not $NoAi) {
    Write-Host ""
    Write-Host "=== batch_audit: AI (gpt-4o-mini) ===" -ForegroundColor Cyan
    python batch_audit.py --output-dir $OutputRoot --model gpt-4o-mini
    if ($LASTEXITCODE -ne 0) {
        Write-Host "AI audit failed (exit $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# ── 4) Cluster audit ────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=== cluster_audit ===" -ForegroundColor Cyan
python cluster_audit.py --output-dir $OutputRoot
if ($LASTEXITCODE -ne 0) {
    Write-Host "Cluster audit failed (exit $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}

# ── 5) Tests (unless skipped) ───────────────────────────────────────────────
if (-not $SkipTests) {
    Write-Host ""
    Write-Host "=== pytest ===" -ForegroundColor Cyan
    python -m pytest tests/ -v --tb=short
    if ($LASTEXITCODE -ne 0) {
        Write-Host "pytest failed (exit $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# ── Done ────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host " DONE" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host " Artifacts in $OutputRoot"
Write-Host "   audit_report.json     — structured report"
Write-Host "   audit_summary.xlsx    — per-vendor summary"
Write-Host "   cluster_summary.xlsx  — UNKNOWN/AI_MISMATCH clusters"
Write-Host "   *_audited.xlsx        — per-file annotated with pipeline_check"
Write-Host "=================================================================" -ForegroundColor Green
exit 0
