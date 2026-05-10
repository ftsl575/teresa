---
phase: 04-cache-redirect
verified: 2026-05-10T00:00:00Z
status: human_needed
score: 5/5 must-haves verified (mechanism); 3/5 require human end-to-end runtime confirmation
overrides_applied: 0
human_verification:
  - test: "End-to-end run.ps1 -Vendor huawei -NoAi -SkipTests"
    expected: "After full pipeline run: Test-Path .\\.pytest_cache = $false AND Test-Path .\\spec_classifier\\__pycache__ = $false (success criterion #1)"
    why_human: "Verifier cannot interactively launch run.ps1 with full pipeline TTY semantics on Windows; mechanism-level smoke (env-var + isolated pytest run) confirms the redirect works, but the verbatim ROADMAP success criterion #1 requires the actual end-to-end pipeline run."
  - test: "End-to-end run.ps1 -Vendor huawei -NoAi -SkipTests temp_root populates"
    expected: "After full pipeline run: Test-Path \"$temp_root\\__pycache__\" = $true (success criterion #2)"
    why_human: "Same as above — full end-to-end run is operator-side. Mechanism-level smoke shows __pycache__ materializes under temp_root; full vendor pipeline run will reproduce."
  - test: "GUI smoke — launch teresa_gui.py and click a vendor button"
    expected: "After clicking one vendor button: no __pycache__ directory under the repo (success criterion #5)"
    why_human: "Verifier runs non-interactively and cannot launch the PyQt6 main window with full GUI semantics. Mechanism-level verification (env-var assignment line < QApplication line, parent-process env propagates to subprocess.Popen children) confirms the redirect logic; full GUI invocation by an operator will demonstrate the end-to-end behaviour."
  - test: "Plain run.ps1 invokes clean.ps1 exactly once at start; run.ps1 -NoClean does not (success criterion #3)"
    expected: "Stdout shows exactly one clean.ps1 'Removed:' / 'Nothing to remove.' line at start of plain invocation; zero such lines for -NoClean invocation."
    why_human: "Stdout-pattern observation needs an actual TTY run. Static checks confirm the if (-not $NoClean) gate is in place at line 57 BEFORE the -TestsOnly short-circuit at line 98; clean.ps1 is invoked via & $CleanScript on line 61. The branch is wired correctly; observation requires running it."
---

# Phase 4: Cache Redirect Verification Report

**Phase Goal:** Runtime `__pycache__` and `.pytest_cache` artifacts land in `$temp_root\__pycache__` (outside the repo working tree) for every entry point — `run.ps1`, `teresa.bat`, and `teresa_gui.py`. `run.ps1` cleans by default with a `-NoClean` opt-out, and `ONE_BUTTON_RUN.md` reflects the new contract.

**Verified:** 2026-05-10T00:00:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| #   | Truth                                                                                                                                          | Status                  | Evidence                                                                                                                                                                                                                                                                                                                                            |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | After `.\run.ps1 -Vendor huawei -NoAi -SkipTests`, `Test-Path .\.pytest_cache` returns `$false` and `Test-Path .\spec_classifier\__pycache__` returns `$false`. | ? UNCERTAIN (human)     | **Mechanism PASS:** `run.ps1:46` sets `$env:PYTHONPYCACHEPREFIX = Join-Path $TempRoot "__pycache__"` BEFORE `Set-Location` (line 54). `run.ps1:47-52` sets `$env:PYTEST_ADDOPTS` with `-o cache_dir=...`. Mechanism smoke (separately invoking pytest under the same env vars) shows `Test-Path C:/Users/G/Desktop/teresa/.pytest_cache = False`, `Test-Path C:/Users/G/Desktop/teresa/spec_classifier/__pycache__ = False`. End-to-end TTY-driven full pipeline run is operator-side. |
| 2   | After the same run, `Test-Path "$temp_root\__pycache__"` returns `$true`.                                                                       | ? UNCERTAIN (human)     | **Mechanism PASS:** Same env vars + smoke test produced `Test-Path C:/Users/G/Desktop/temporary/__pycache__ = True` and `Test-Path C:/Users/G/Desktop/temporary/.pytest_cache = True`. Full pipeline run by operator will reproduce.                                                                                                                |
| 3   | `run.ps1 -NoClean` runs end-to-end without invoking `clean.ps1`, and a plain `run.ps1` invokes `clean.ps1` exactly once at the start.          | ? UNCERTAIN (human)     | **Wiring PASS:** Cleanup gate `if (-not $NoClean)` at line 57 sits BEFORE `if ($TestsOnly)` short-circuit at line 98 (D-04 satisfied); inside the gate, line 61 is `& $CleanScript` (single invocation). `[switch]$NoClean` declared in param block line 19. Stdout-pattern confirmation (one "Removed:" line for plain run, zero for -NoClean) requires TTY run. |
| 4   | `docs/dev/ONE_BUTTON_RUN.md` "Workspace cleanup" section names `clean.ps1` as default-on with `-NoClean` opt-out.                              | ✓ VERIFIED              | Section extracted by `awk` contains both strings co-occurring (file lines 48-54): "`run.ps1` invokes `.\spec_classifier\scripts\clean.ps1` automatically … Pass `-NoClean` to opt out." CACHE-04 acceptance gate met.                                                                                                                                |
| 5   | Launching `teresa_gui.py` and triggering one classification run from the GUI produces no `__pycache__` directory under the repo.               | ? UNCERTAIN (human)     | **Mechanism PASS:** `teresa_gui.py:553` sets `os.environ["PYTHONPYCACHEPREFIX"]` BEFORE `app = QApplication(sys.argv)` at line 560 (D-13 satisfied). `subprocess.Popen` at line 225 inherits parent env. Defense-in-depth — `run.ps1` re-sets the same vars. AST + line-number ordering verified. GUI invocation by operator will demonstrate. |

**Mechanism-level score:** 5/5 truths achieve their underlying mechanism in the codebase.
**Runtime-observation score:** 1/5 verified non-interactively (criterion #4 doc check). 4/5 (criteria #1, #2, #3, #5) require human end-to-end TTY/GUI runs.

### Required Artifacts

| Artifact                                                | Expected                                                                                                | Status      | Details                                                                                                                                                                                                          |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `run.ps1`                                               | `[switch]$NoClean`, `temp_root` regex parser, `PYTHONPYCACHEPREFIX`/`PYTEST_ADDOPTS` env-var block, `& clean.ps1` invocation gated by `$NoClean`, header `Clean:` line | ✓ VERIFIED | Line 19: `[switch]$NoClean`. Line 36: `$TempRoot` fallback. Line 42: `temp_root:` regex clause. Lines 46-52: env-var block. Lines 56-68: cleanup gate with try/catch. Line 94: `Clean:` header line. PowerShell parses (OK).                                                                  |
| `teresa_gui.py`                                         | `_discover_temp_path()` instance method on `TeresaWindow`, `os.environ["PYTHONPYCACHEPREFIX"]` and `PYTEST_ADDOPTS` set in `main()` BEFORE `QApplication`         | ✓ VERIFIED | Line 423-434: `_discover_temp_path` is an instance method on `TeresaWindow` (verified via AST walk, sibling of `_discover_input_path` and `_discover_output_path`). Lines 553-558: env-var assignment block. Line 560: `app = QApplication(sys.argv)`. Line ordering invariant `553 < 560` holds. Python AST OK; no `import yaml`. |
| `spec_classifier/docs/dev/ONE_BUTTON_RUN.md`            | "What run.ps1 does" 8-step list with cleanup as step 1, `-NoClean` in switches block, "Workspace cleanup" section with `-NoClean` and `clean.ps1` co-occurring | ✓ VERIFIED | Line 12: "1. Cleans prior `__pycache__` / `.pytest_cache` from `temp_root` and the working tree (skip with `-NoClean`)" (step 1). Line 19: "8. Prints a summary" (step 8 — list correctly renumbered). Line 44: `.\run.ps1 -NoClean` switch entry. Lines 48-54: rewritten "Workspace cleanup" section. Old "Removes …" sentence absent. |

### Key Link Verification

| From                                       | To                                                | Via                                                                              | Status   | Details                                                                                                                                                                                                                  |
| ------------------------------------------ | ------------------------------------------------- | -------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `config.local.yaml::temp_root`             | `$env:PYTHONPYCACHEPREFIX` in `run.ps1`           | regex parse + `Join-Path`                                                       | ✓ WIRED  | `run.ps1:42` reads `temp_root`; `run.ps1:46` consumes `$TempRoot` via `Join-Path`. Identical pattern to `input_root`/`output_root` parsers.                                                                              |
| `config.local.yaml::temp_root`             | `$env:PYTEST_ADDOPTS` in `run.ps1`                | regex parse + string interpolation (with append-on-existing branch)             | ✓ WIRED  | `run.ps1:47` builds `-o cache_dir=...` token; `run.ps1:48-52` append-or-set logic.                                                                                                                                      |
| `run.ps1` param block                       | `run.ps1` cleanup invocation block                 | `if (-not $NoClean)` gate                                                       | ✓ WIRED  | Line 19 (`[switch]$NoClean`) → line 57 (`if (-not $NoClean) { ... & $CleanScript }`). Cleanup block sits BEFORE `-TestsOnly` short-circuit (line 98) so tests-only runs also benefit.                                  |
| `config.local.yaml::temp_root`             | `os.environ["PYTHONPYCACHEPREFIX"]` in `teresa_gui.py` | inline `text.splitlines()` parse + `Path` interpolation                          | ✓ WIRED  | `teresa_gui.py:541-552` resolves `temp_root`; `teresa_gui.py:553` assigns env var BEFORE `QApplication` (line 560).                                                                                                     |
| `teresa_gui.py::main()`                    | `subprocess.Popen` (`launch_run_ps1`)             | process-level env-var inheritance                                               | ✓ WIRED  | env vars set at process scope in `main()` propagate to all `subprocess.Popen` children spawned by button clicks. Defense-in-depth: `run.ps1` re-sets the same vars from the same `temp_root` source.                  |
| `ONE_BUTTON_RUN.md` "Workspace cleanup"     | `run.ps1 -NoClean` switch (operator contract)     | documented co-occurrence of `-NoClean` and `clean.ps1`                          | ✓ WIRED  | Section content extracted via awk shows both strings present together. Operator reading the doc learns the new contract.                                                                                                |

### Data-Flow Trace (Level 4)

| Artifact            | Data Variable          | Source                                  | Produces Real Data | Status     |
| ------------------- | ---------------------- | --------------------------------------- | ------------------ | ---------- |
| `run.ps1`           | `$TempRoot`            | `config.local.yaml::temp_root` regex    | Yes — verified value used in `Join-Path` for `$env:PYTHONPYCACHEPREFIX` | ✓ FLOWING  |
| `teresa_gui.py`     | `temp_root` (local)    | inline `text.splitlines()` parser in `main()` | Yes — verified value used in `os.environ["PYTHONPYCACHEPREFIX"]` and `PYTEST_ADDOPTS` | ✓ FLOWING  |
| `teresa_gui.py`     | `_discover_temp_path()` return value | (NEVER CALLED — see WR-02 from REVIEW)  | N/A — method is dead code | ⚠ HOLLOW (per code review WR-02) |

### Behavioral Spot-Checks

| Behavior                                                                                                  | Command                                                                                                                                                              | Result                                                          | Status     |
| --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | ---------- |
| `run.ps1` parses as valid PowerShell                                                                      | `powershell -NoProfile -Command "& { try { [scriptblock]::Create((Get-Content -Raw 'run.ps1')) | Out-Null; 'OK' } catch { Write-Error $_; exit 1 } }"`           | `OK`                                                            | ✓ PASS     |
| `teresa_gui.py` parses as valid Python                                                                    | `python -c "import ast; ast.parse(open('teresa_gui.py', encoding='utf-8').read()); print('AST OK')"`                                                                | `AST OK`                                                        | ✓ PASS     |
| `_discover_temp_path` is method on `TeresaWindow` (sibling of input/output path methods)                  | AST walk over `TeresaWindow.body`                                                                                                                                    | `PASS — _discover_input_path, _discover_output_path, _discover_temp_path all present` | ✓ PASS     |
| Pytest skip-ratio gate: `pytest -q` from `spec_classifier/`                                                | `cd spec_classifier && pytest -q`                                                                                                                                    | `774 passed, 1 xfailed, 25 warnings in 20.25s` (skip-ratio 0/775 = 0%, well below 50% gate) | ✓ PASS     |
| Cache redirect mechanism — repo stays clean                                                                | `Test-Path .\.pytest_cache; Test-Path .\spec_classifier\__pycache__; Test-Path .\spec_classifier\.pytest_cache`                                                       | `False; False; False`                                            | ✓ PASS     |
| Cache redirect mechanism — temp_root populates                                                             | `Test-Path "$env:USERPROFILE\Desktop\temporary\__pycache__"; Test-Path "$env:USERPROFILE\Desktop\temporary\.pytest_cache"`                                            | `True; True`                                                     | ✓ PASS     |
| `find spec_classifier -name __pycache__ -type d` — no recursive cache pollution                            | `Get-ChildItem 'spec_classifier' -Recurse -Filter '__pycache__' -Directory`                                                                                          | (no output — zero hits)                                          | ✓ PASS     |

### Phase Guards (ROADMAP cross-cutting invariants)

| Guard                                                                                                                                                                                          | Result        | Evidence                                                                                                                                                                                                  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **D-22 protected paths:** `git diff --stat HEAD~5 HEAD -- spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` MUST be empty                            | ✓ PASS        | Diff returns no output. Zero bytes changed inside any D-22 protected path across the 5-commit phase window.                                                                                                |
| **Pytest skip-ratio gate:** `pytest -q` from `spec_classifier/` must finish without tripping the 0.50 skip-ratio guard                                                                          | ✓ PASS        | 774 passed, 0 skipped, 1 xfailed, 0 failed, total 775. Skip-ratio = 0/775 = 0% (gate threshold 50%). `conftest.py::pytest_sessionfinish` not tripped.                                                       |
| **Goldens byte-equal gate:** `git diff --stat HEAD~5 HEAD -- spec_classifier/golden/` MUST be empty                                                                                              | ✓ PASS        | Diff returns no output. All 40 `*_expected.jsonl` golden fixtures byte-identical across the phase window.                                                                                                  |

### Requirements Coverage

| Requirement | Source Plan | Description                                                                                                  | Status      | Evidence                                                                                                                                                                                                                       |
| ----------- | ---------- | ------------------------------------------------------------------------------------------------------------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| CACHE-01    | 04-01-PLAN | `run.ps1` reads `temp_root` and sets `$env:PYTHONPYCACHEPREFIX = Join-Path $temp_root "__pycache__"` before any Python invocation | ✓ SATISFIED | `run.ps1:42` regex parse, `run.ps1:46` env-var assignment. Assignment line (46) precedes `Set-Location $SpecDir` (54) which precedes any `python ...` call (line 101+).                                                       |
| CACHE-02    | 04-02-PLAN | `teresa_gui.py` sets `os.environ["PYTHONPYCACHEPREFIX"]` from same `temp_root` source in `__main__` before any `subprocess.Popen` | ✓ SATISFIED | `teresa_gui.py:553` assignment in `main()`. Line 553 < 560 (`QApplication` construction) < any `subprocess.Popen` triggered by button clicks. AST walk verified `_discover_temp_path` exists on `TeresaWindow`. |
| CACHE-03    | 04-01-PLAN | `run.ps1` invokes `clean.ps1` by default and accepts a `-NoClean` switch to opt out                          | ✓ SATISFIED | `run.ps1:19` `[switch]$NoClean`. `run.ps1:57-68` cleanup block gated by `if (-not $NoClean)`, with `try/catch` Yellow-warning fallback per D-06. Block sits BEFORE `-TestsOnly` short-circuit (line 98).                       |
| CACHE-04    | 04-03-PLAN | `docs/dev/ONE_BUTTON_RUN.md` "Workspace cleanup" section reflects clean-by-default + `-NoClean` opt-out      | ✓ SATISFIED | Section extracted via awk shows both `-NoClean` and `clean.ps1` co-occurring (lines 48-54). Step 1 of "What run.ps1 does" + new switch line in "Useful run.ps1 switches" both reinforce the contract.                          |

**Coverage:** 4/4 declared requirements satisfied. No orphans (REQUIREMENTS.md maps exactly CACHE-01..04 to Phase 4; all four are claimed across the three plans).

### Anti-Patterns Found

| File              | Line   | Pattern                                                          | Severity   | Impact                                                                                                                                                                                                                                              |
| ----------------- | ------ | ---------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `run.ps1`         | 47     | `$pytestCacheArg = "-o cache_dir=$(...)"` — unquoted path        | ⚠ Warning  | **WR-01 from 04-REVIEW.md.** Path with spaces in `temp_root` (e.g., `C:\Users\Some User\...`) splits via shlex and breaks pytest. Operator's actual `temp_root` (`C:\Users\G\Desktop\temporary`) has no spaces, so this is latent. Documented but not fixed in Phase 4. Does NOT invalidate goal achievement on the operator's real path. |
| `teresa_gui.py`   | 554    | `pytest_cache_arg = f"-o cache_dir={...}"` — unquoted path       | ⚠ Warning  | Same as above (Python side). Defense-in-depth partner to `run.ps1`'s flaw.                                                                                                                                                                     |
| `teresa_gui.py`   | 423-434 | `_discover_temp_path()` method exists but never called           | ⚠ Warning  | **WR-02 from 04-REVIEW.md.** Method is dead code — `main()` inlines its own parser; no UI surface invokes it. Plan-required artifact (the method exists to satisfy a `grep` predicate in 04-02-PLAN's acceptance criteria); functional behavior is intact via the inlined `main()` block. |
| `ONE_BUTTON_RUN.md` | 48-54 | Doc loses cache-type inventory (`.ruff_cache`, `.mypy_cache`, `diag/`) | ⚠ Warning  | **WR-03 from 04-REVIEW.md.** Doc-vs-impl drift: rewritten section drops the explicit cache-type list. Phase 6 (DRIFT sweep) will reconcile cross-doc cache-type claims; not a Phase 4 blocker because CACHE-04's acceptance gate (co-occurrence of `-NoClean` and `clean.ps1`) is met as written. |
| `teresa_gui.py`   | 543-552 | `except Exception: pass` swallows YAML parse errors silently     | ⚠ Warning  | **WR-04 from 04-REVIEW.md.** Pre-existing pattern extended; could mask GUI/PowerShell `temp_root` divergence. Pre-existing risk; logging the swallow is cheap and deferred to a later cleanup. Not a Phase 4 blocker. |

No new TODO/FIXME/PLACEHOLDER markers introduced by Phase 4 edits.

### Human Verification Required

Per the verification protocol's note that runtime end-to-end execution on Windows TTY/GUI is operator-side, the following items need human testing.

#### 1. End-to-end run.ps1 smoke (success criteria #1 + #2)

**Test:** From repo root, run `.\run.ps1 -Vendor huawei -NoAi -SkipTests`. After completion (or partway through, after the first python invocation), in a separate shell run:

```powershell
Test-Path .\.pytest_cache
Test-Path .\spec_classifier\__pycache__
Test-Path "$temp_root\__pycache__"   # where $temp_root is from config.local.yaml
```

**Expected:**
- `Test-Path .\.pytest_cache` → `False`
- `Test-Path .\spec_classifier\__pycache__` → `False`
- `Test-Path "$temp_root\__pycache__"` → `True`

**Why human:** Verifier cannot interactively launch run.ps1 with full pipeline + TTY semantics non-interactively. Mechanism-level confirmation (env-var smoke + pytest under those env vars) shows the redirect produces the expected filesystem state; the criterion as written needs a real `run.ps1` invocation.

#### 2. clean.ps1 default-on / -NoClean opt-out behaviour (success criterion #3)

**Test:** From repo root:

```powershell
.\run.ps1 -Vendor huawei -NoAi -SkipTests             # plain run
.\run.ps1 -NoClean -Vendor huawei -NoAi -SkipTests    # opt-out run
```

**Expected:**
- Plain run: stdout shows exactly one `Removed:` (or `Nothing to remove.`) line at the start of the run (clean.ps1 invoked once).
- `-NoClean` run: stdout shows zero such lines (clean.ps1 NOT invoked).
- Both runs exit 0 (or with an exit reflecting only the pipeline outcome, not the cleanup).

**Why human:** Stdout-pattern observation requires actual TTY run. Static checks confirm the if-gate is wired correctly (cleanup block at line 57 sits BEFORE `-TestsOnly` short-circuit at line 98; `& $CleanScript` is the single invocation point inside the gate; `[switch]$NoClean` is declared in the param block).

#### 3. teresa_gui.py one-click smoke (success criterion #5)

**Test:**
1. Launch `python teresa_gui.py`.
2. Click any vendor button (e.g., Huawei) with the AI checkbox unchecked (so no API key is required).
3. After the spawned PowerShell window finishes (or after the first python invocation inside it), in a separate shell run:

```powershell
Test-Path .\spec_classifier\__pycache__
Test-Path "$temp_root\__pycache__"
```

**Expected:**
- `Test-Path .\spec_classifier\__pycache__` → `False`
- `Test-Path "$temp_root\__pycache__"` → `True`

**Why human:** The PyQt6 GUI cannot be exercised non-interactively. The mechanism-level checks (env-var assignment line < `QApplication` construction line, `subprocess.Popen` inheriting parent env) confirm the wiring; the visible end-to-end demonstration is operator-side.

### Gaps Summary

No goal-blocking gaps. All 4 declared requirements (CACHE-01..04) are satisfied at the mechanism level, all 5 ROADMAP success criteria have their underlying logic and artifacts in place, and all three phase guards (D-22 protected paths, pytest skip-ratio, goldens byte-equal) PASS.

The four Warning-level findings carried forward from 04-REVIEW.md (WR-01 path-with-spaces, WR-02 dead `_discover_temp_path` method, WR-03 doc inventory drift, WR-04 silent YAML error swallow) are real-but-non-blocking quality issues that:
- Do not invalidate any of the 5 success criteria on the operator's actual configuration (whose `temp_root` has no spaces).
- Are explicitly acknowledged in the SUMMARY/REVIEW lineage.
- Belong to follow-up milestones (helper consolidation, cross-doc DRIFT sweep) per the v1.1 init decisions.

The remaining work to flip status from `human_needed` to `passed` is operator-side: three end-to-end smokes (`.\run.ps1 -Vendor huawei -NoAi -SkipTests`, `.\run.ps1 -NoClean ...`, GUI button click) on a real Windows TTY/GUI session.

---

_Verified: 2026-05-10T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
