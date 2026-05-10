---
status: partial
phase: 04-cache-redirect
source: [04-VERIFICATION.md]
started: 2026-05-10T14:50:00Z
updated: 2026-05-10T14:50:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. End-to-end run.ps1 -Vendor huawei -NoAi -SkipTests — repo cache absent
expected: After full pipeline run, `Test-Path .\.pytest_cache` returns `$false` AND `Test-Path .\spec_classifier\__pycache__` returns `$false` (success criterion #1).
result: [pending]

### 2. End-to-end run.ps1 -Vendor huawei -NoAi -SkipTests — temp_root cache populates
expected: After full pipeline run, `Test-Path "$temp_root\__pycache__"` returns `$true` (success criterion #2).
result: [pending]

### 3. clean.ps1 default-on vs -NoClean opt-out
expected: Plain `run.ps1` shows exactly one clean.ps1 "Removed:" / "Nothing to remove." line at start; `run.ps1 -NoClean` shows zero such lines (success criterion #3).
result: [pending]

### 4. GUI smoke — teresa_gui.py classification run
expected: Launch `python teresa_gui.py`, click one vendor button, then `Test-Path .\spec_classifier\__pycache__` returns `$false` (success criterion #5).
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
