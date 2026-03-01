# Remove __pycache__ and .pytest_cache from temp_root and working tree. UTF-8.
# Removes: __pycache__, .pytest_cache, .ruff_cache, .mypy_cache, diag/ (from temp_root and repo). Does NOT remove: golden/, test_data/, output/

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

# .ruff_cache
foreach ($target in @((Join-Path $TempRoot ".ruff_cache"), (Join-Path $RepoRoot ".ruff_cache"))) {
    if (Test-Path $target) { Remove-Item -Recurse -Force $target; $removed += $target }
}
# .mypy_cache
foreach ($target in @((Join-Path $TempRoot ".mypy_cache"), (Join-Path $RepoRoot ".mypy_cache"))) {
    if (Test-Path $target) { Remove-Item -Recurse -Force $target; $removed += $target }
}
# diag (логи прогонов, теперь в temp_root)
$tempDiag = Join-Path $TempRoot "diag"
if (Test-Path $tempDiag) { Remove-Item -Recurse -Force $tempDiag; $removed += $tempDiag }
# diag внутри репо (старые запуски до фикса)
$repoDiag = Join-Path $RepoRoot "diag"
if (Test-Path $repoDiag) { Remove-Item -Recurse -Force $repoDiag; $removed += $repoDiag }

if ($removed.Count -gt 0) {
    Write-Host "Removed:"
    $removed | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "Nothing to remove."
}
