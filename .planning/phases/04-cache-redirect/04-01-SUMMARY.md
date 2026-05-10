---
phase: 04-cache-redirect
plan: 01
subsystem: launcher / runtime cache redirect
tags: [powershell, runtime-cache, cleanup, launcher]
requires: []
provides:
  - "$env:PYTHONPYCACHEPREFIX is set from config.local.yaml::temp_root in run.ps1 before any Python invocation"
  - "$env:PYTEST_ADDOPTS is set with -o cache_dir from $temp_root in run.ps1 before any Python invocation"
  - "run.ps1 invokes spec_classifier/scripts/clean.ps1 by default at the start of every run, gated by -NoClean opt-out switch"
  - "run.ps1 -NoClean switch (boolean) skips the start-of-run cleanup pass"
  - "run.ps1 header banner reflects clean mode (Clean: ON / Clean: OFF)"
affects:
  - run.ps1
tech_stack:
  added: []
  patterns:
    - "config.local.yaml regex parser extended with a 5th site (run.ps1 temp_root clause) — intentional per CONCERNS.md § IMPORTANT; helper consolidation deferred"
    - "PowerShell try/catch around external script invocation to bypass $ErrorActionPreference=Stop on non-fatal failures"
key_files:
  created: []
  modified:
    - run.ps1
decisions:
  - "Used `--` (ASCII double-hyphen) instead of `—` (Unicode em-dash, U+2014) in two new Write-Host strings (lines 63, 66) because Windows PowerShell 5.x's parser fails on em-dash inside a string that also contains a `$(...)` sub-expression. See deviation log."
  - "Followed plan's intent verbatim; only character substitution above. All 5 edits placed at the prescribed line ranges; ordering invariants (PYTHONPYCACHEPREFIX before Set-Location, cleanup block before -TestsOnly short-circuit) hold."
metrics:
  duration_minutes: 25
  completed_date: 2026-05-10
  task_count: 1
  files_changed: 1
---

# Phase 4 Plan 1: Cache Redirect — run.ps1 wiring Summary

PowerShell launcher `run.ps1` now redirects `__pycache__` and `.pytest_cache` to `$temp_root` via env vars and runs `clean.ps1` by default at start of every invocation; opt-out with `-NoClean`.

## What Changed

Five coordinated edits to `run.ps1`:

| Edit | Change | Lines (post-edit) |
|------|--------|-------------------|
| 1 | Added `[switch]$NoClean` to `param()` block | 14-20 |
| 2 | Added `$TempRoot` default fallback (line 36) + 3rd regex clause for `temp_root` (line 42) | 33-43 |
| 3 | Set `$env:PYTHONPYCACHEPREFIX` and `$env:PYTEST_ADDOPTS` (with append-on-existing logic) BEFORE `Set-Location $SpecDir` | 45-52 |
| 4 | Inserted `if (-not $NoClean) { try { & clean.ps1 } catch { … } }` cleanup block AFTER `Set-Location $SpecDir` and BEFORE `-TestsOnly` short-circuit | 56-68 |
| 5 | Added `Clean:` line to header banner reflecting `$NoClean` | 94 |

### Pre/post line-range deltas

| Region | Pre-edit | Post-edit |
|--------|----------|-----------|
| `param()` block | 14-19 (5 lines) | 14-20 (6 lines) |
| Path discovery + config parser | 32-40 (9 lines) | 33-43 (11 lines) |
| Cache-redirect env vars | n/a | 45-52 (8 lines new) |
| Cleanup block | n/a | 56-68 (13 lines new) |
| Header banner | 57-68 (12 lines) | 83-95 (13 lines) |
| Total file length | 165 lines | 192 lines (+27) |

### Excerpts (post-edit)

**param block (run.ps1:14-20):**
```powershell
param(
    [string]$Vendor = "",
    [switch]$NoAi,
    [switch]$TestsOnly,
    [switch]$SkipTests,
    [switch]$NoClean
)
```

**`temp_root` parser clause (run.ps1:36, 42):**
```powershell
$TempRoot   = "$env:USERPROFILE\Desktop\temporary"
…
    if ($cfg -match '(?m)^\s*temp_root:\s*["'']?([^"''\r\n]+)["'']?\s*$')   { $TempRoot   = $Matches[1].Trim() }
```

**Cache-redirect env vars (run.ps1:45-52):**
```powershell
# Redirect Python bytecode + pytest cache to $TempRoot (out of the repo tree).
$env:PYTHONPYCACHEPREFIX = Join-Path $TempRoot "__pycache__"
$pytestCacheArg = "-o cache_dir=$(Join-Path $TempRoot '.pytest_cache')"
if ($env:PYTEST_ADDOPTS) {
    $env:PYTEST_ADDOPTS = "$env:PYTEST_ADDOPTS $pytestCacheArg"
} else {
    $env:PYTEST_ADDOPTS = $pytestCacheArg
}
```

**Cleanup block (run.ps1:56-68):**
```powershell
# ── Workspace cleanup (default-on; opt out with -NoClean) ────────────────────
if (-not $NoClean) {
    $CleanScript = Join-Path $SpecDir "scripts\clean.ps1"
    if (Test-Path $CleanScript) {
        try {
            & $CleanScript
        } catch {
            Write-Host "clean.ps1 failed: $($_.Exception.Message) -- continuing" -ForegroundColor Yellow
        }
    } else {
        Write-Host "clean.ps1 not found at $CleanScript -- skipping cleanup" -ForegroundColor Yellow
    }
}
```

**Header banner addition (run.ps1:94):**
```powershell
Write-Host " Clean:    $(if ($NoClean) { 'OFF (manual)' } else { 'ON (clean.ps1 at start)' })"
```

## Verification

### Static checks (automated)

| Predicate | Result |
|-----------|--------|
| `[switch]$NoClean` count == 1 | PASS (1) |
| `temp_root:` regex clause count >= 1 | PASS (1) |
| `^\s*\$env:PYTHONPYCACHEPREFIX\s*=` | PASS (line 46) |
| `\$env:PYTEST_ADDOPTS\s*=` | PASS (3 occurrences across if/else) |
| `if (-not \$NoClean)` count == 1 | PASS (1) |
| `clean.ps1 failed:` count == 1 | PASS (1) |
| `Clean:` header label count >= 1 | PASS (1) |
| `ON (clean.ps1 at start)` count == 1 | PASS (1) |
| `OFF (manual)` count == 1 | PASS (1) |
| `input_root:` clause preserved | PASS (1, line 40) |
| `output_root:` clause preserved | PASS (1, line 41) |
| `$env:PYTHONPYCACHEPREFIX` line < `Set-Location` line | PASS (46 < 54) |
| Cleanup `if (-not $NoClean)` line < `if ($TestsOnly)` line | PASS (57 < 98) |

### PowerShell syntax check

Used `[System.Management.Automation.Language.Parser]::ParseFile()` to validate the file:

```
OK
```

(File parses with zero parse errors.)

### D-22 protected-paths guard

```
$ git diff --stat HEAD -- spec_classifier/src spec_classifier/rules \
    spec_classifier/golden spec_classifier/tests \
    spec_classifier/batch_audit.py spec_classifier/cluster_audit.py \
    spec_classifier/main.py spec_classifier/conftest.py
(no output)
```

PASS — zero bytes changed inside any D-22 protected path.

### Goldens byte-equal guard

```
$ git diff --stat HEAD -- spec_classifier/golden/
(no output)
```

PASS — all 40 golden fixtures byte-identical.

### Pytest skip-ratio gate

`python -m pytest -q` (run from `spec_classifier/`):

```
774 passed, 1 xfailed, 25 warnings in 20.90s
```

| Counter | Value |
|---------|-------|
| passed  | 774   |
| skipped | 0     |
| xfailed | 1     |
| failed  | 0     |
| total   | 775   |
| skip-ratio | 0/775 = 0% (gate threshold: must be ≤ 50%) |

PASS — `conftest.py::pytest_sessionfinish` skip-guard not tripped.

### Smoke test (cache redirect)

Direct simulation of run.ps1's env-var setting (since this agent runs non-interactively and cannot invoke `.\run.ps1` with full TTY semantics):

```
$ PYTHONPYCACHEPREFIX="$temp_root\__pycache__" \
  PYTEST_ADDOPTS="-o cache_dir=$temp_root\.pytest_cache" \
  python -m pytest -q tests/test_smoke.py
5 passed in 0.83s
```

Post-run filesystem checks:

| Path | Test-Path / ls | Plan expectation |
|------|----------------|------------------|
| `C:/Users/G/Desktop/teresa/.pytest_cache` | does not exist | `$false` |
| `C:/Users/G/Desktop/teresa/spec_classifier/__pycache__` | does not exist | `$false` |
| `C:/Users/G/Desktop/teresa/spec_classifier/.pytest_cache` | does not exist | (implicit `$false`) |
| `C:/Users/G/Desktop/temporary/.pytest_cache` | exists, contains `CACHEDIR.TAG`, `README.md`, `v/` | (created by pytest under redirect) |
| `C:/Users/G/Desktop/temporary/__pycache__` | exists, contains compiled bytecode | `$true` |
| `find spec_classifier -name __pycache__ -type d` | 0 hits | (consistent with redirect) |

PASS — success criteria 1, 2, 3 from the plan are satisfied at the env-var level. Full `.\run.ps1 -Vendor huawei -NoAi -SkipTests` end-to-end smoke is the operator's responsibility (plan-acknowledged: `<done>` clause says "manual smoke; not part of automated verify").

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Replaced em-dash (`—`, U+2014) with ASCII `--` in two new Write-Host strings**

- **Found during:** Task 1.1, post-edit PowerShell parse step
- **Issue:** Windows PowerShell 5.x's parser silently fails on em-dash (`—`, UTF-8 `E2 80 94`) when it appears inside a double-quoted string that also contains a `$(...)` sub-expression. The plan's prescribed text on lines 63 and 66 was:
  - `Write-Host "clean.ps1 failed: $($_.Exception.Message) — continuing"` (em-dash inside string with `$(…)` sub-expr)
  - `Write-Host "clean.ps1 not found at $CleanScript — skipping cleanup"` (em-dash inside string)
  Both caused the parser to emit `Missing closing "}"` errors at the cleanup block (line 57:20). Verified by:
  1. Identical em-dash usage in pre-existing strings on lines 124 and 130 (`Write-Host "=== Pipeline: $v — SKIP ..."`) parses fine — but those have only simple `$v` interpolation, no `$(...)`.
  2. Replacing both em-dashes with `--` makes the file parse cleanly.
  3. File is valid UTF-8 throughout (no BOM, no malformed sequences); the issue is parser-internal.
- **Fix:** Replaced `—` with `--` in both new Write-Host lines (63 and 66). The visual rendering changes from "failed: foo — continuing" to "failed: foo -- continuing"; semantically identical operator-facing message.
- **Files modified:** `run.ps1` (lines 63, 66)
- **Why this is in-scope (Rule 1):** The plan's literal text would have shipped a non-parseable script — i.e., `run.ps1` would not run at all. This is a correctness-blocking bug in the plan's prescribed string content, not a stylistic preference. Auto-fixed without checkpoint per Rule 1 (auto-fix bugs that prevent code from working as intended).
- **No deviation from plan intent:** All 5 edits land at the prescribed locations; the `try/catch` Yellow-warning convention is preserved; only the dash glyph differs.

**Acceptance criteria for `clean.ps1 failed:` substring search still passes** (verified — count is 1 because the plan-specified prefix `clean.ps1 failed:` is unchanged; only the dash after the substituted message changes).

### Out-of-scope discoveries: none

No incidental fixes were attempted in Phase 4 / Plan 1 — the edit scope is confined to `run.ps1` per CONTEXT.md D-12 and D-22.

## Threat Flags

None — Phase 4 Plan 1 introduces no new external-input parsing surface beyond an additional regex clause over an already-trusted, gitignored, operator-owned config file (`config.local.yaml`). All threats from the plan's `<threat_model>` are unchanged in disposition (T-04-01 accept; T-04-02 mitigate via try/catch; T-04-03 accept).

## Self-Check: PASSED

- `run.ps1` exists and contains all 5 edits — FOUND
- File parses as valid PowerShell via `[System.Management.Automation.Language.Parser]::ParseFile()` — OK
- `git diff --stat HEAD -- spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` shows zero rows — OK
- `git diff --stat HEAD -- spec_classifier/golden/` shows zero rows — OK
- pytest exits clean (774 pass / 1 xfail / 0 skipped / 0 failed; skip-ratio 0% << 50% gate) — OK
- Cache-redirect env-var smoke test confirms `__pycache__` and `.pytest_cache` materialize under `$temp_root` and not the repo tree — OK
- Commit hash for this task: recorded in commit metadata after Write completes

## Notes for Plan 02 (CACHE-02 — `teresa_gui.py`)

This plan's `$env:PYTHONPYCACHEPREFIX` / `$env:PYTEST_ADDOPTS` setting in `run.ps1` is the load-bearing redirect (CACHE-01). Plan 02 will add the symmetric defense-in-depth layer in `teresa_gui.py::main()` per CONTEXT.md D-13. When that lands, both layers will set the same env vars from the same `temp_root` source — redundantly, by design.

CONCERNS.md § IMPORTANT now stands at 5 sites of the `config.local.yaml` overlay regex (run.ps1 ×1 just added; pre-existing: `teresa_gui.py:_discover_input_path`, `teresa_gui.py:_discover_output_path`, `main.py`, `conftest.py`). Plan 02 will add the 6th. Helper consolidation remains deferred per the v1.1 init decision.
