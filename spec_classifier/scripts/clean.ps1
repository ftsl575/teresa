# Remove __pycache__ and .pytest_cache from temp_root and working tree. UTF-8.
# Does NOT remove: golden/, test_data/, diag/runs/, output/

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$RepoRoot = Split-Path -Parent $PSScriptRoot
$TempRoot = Join-Path $RepoRoot "temporary"
$ConfigLocal = Join-Path $RepoRoot "config.local.yaml"
if (Test-Path $ConfigLocal) {
    $content = Get-Content $ConfigLocal -Raw -Encoding UTF8
    if ($content -match 'temp_root:\s*["'']([^"'']+)["'']') { $TempRoot = $Matches[1].Trim() }
}

$removed = @()

$tempPyCache = Join-Path $TempRoot "__pycache__"
if (Test-Path $tempPyCache) {
    Remove-Item -Recurse -Force $tempPyCache
    $removed += $tempPyCache
}
$tempPytest = Join-Path $TempRoot ".pytest_cache"
if (Test-Path $tempPytest) {
    Remove-Item -Recurse -Force $tempPytest
    $removed += $tempPytest
}

$repoPytest = Join-Path $RepoRoot ".pytest_cache"
if (Test-Path $repoPytest) {
    Remove-Item -Recurse -Force $repoPytest
    $removed += $repoPytest
}

Get-ChildItem -Path $RepoRoot -Filter "__pycache__" -Recurse -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Recurse -Force $_.FullName
    $removed += $_.FullName
}

if ($removed.Count -gt 0) {
    Write-Host "Removed:"
    $removed | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "Nothing to remove."
}
