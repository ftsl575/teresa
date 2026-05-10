---
phase: 04-cache-redirect
fixed_at: 2026-05-10T00:00:00Z
review_path: .planning/phases/04-cache-redirect/04-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 2
skipped: 2
status: partial
---

# Phase 4: Code Review Fix Report

**Fixed at:** 2026-05-10
**Source review:** `.planning/phases/04-cache-redirect/04-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope (Critical + Warning): 4
- Fixed: 2 (WR-01, WR-04)
- Skipped: 2 (WR-02, WR-03 — both deferred per orchestrator guidance)

Pytest baseline (774 passed / 1 xfailed / 0 failed) preserved across both
fix commits. D-22 protected paths
(`spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}`)
remain unchanged — the only files modified are `run.ps1` and
`teresa_gui.py`, both of which are at the repo root and outside the D-22
boundary.

## Fixed Issues

### WR-01: `PYTEST_ADDOPTS` `cache_dir` value is unquoted — breaks for `temp_root` paths containing spaces

**Files modified:** `run.ps1`, `teresa_gui.py`
**Commit:** `03e717f`
**Applied fix:**

- `run.ps1:47` — wrapped the path inside the option value with backtick-escaped
  double quotes:
  `"-o cache_dir=`"$(Join-Path $TempRoot '.pytest_cache')`""`
- `teresa_gui.py:554` — switched outer f-string delimiter to single quotes
  so a literal `"` can sit inside the value:
  `f'-o cache_dir="{Path(temp_root) / ".pytest_cache"}"'`

**Verification:**

1. PowerShell syntax check: `[ScriptBlock]::Create((Get-Content run.ps1 -Raw))` — OK.
2. Python AST parse on `teresa_gui.py` — OK.
3. Round-trip: a path containing a space (`C:\Users\Some User\Desktop\temporary`)
   passed through PowerShell to `$env:PYTEST_ADDOPTS` to Python
   `shlex.split()` (the same call pytest's `_pytest/config/__init__.py:1390`
   makes) yields exactly two tokens:
   `['-o', 'cache_dir=C:\\Users\\Some User\\Desktop\\temporary\\.pytest_cache']`.
   The Python f-string variant produces the same shlex output.
4. Pytest: 774 passed / 1 xfailed / 0 failed (no regression from baseline).

### WR-04: GUI's `temp_root` parser silently swallows YAML parse errors and uses Desktop fallback

**Files modified:** `teresa_gui.py`
**Commit:** `e5557d5`
**Applied fix:**

In `main()` only (the new parsing block at lines 543-552), replaced
`except Exception: pass` with `except Exception as e: print(... WARN ...,
file=sys.stderr)`. The existing fallback semantics are preserved
(`temp_root` still defaults to `~/Desktop/temporary` on parse failure) —
only the silent-swallow is upgraded to a stderr warning so divergence
between GUI parent and `run.ps1` child becomes diagnosable.

**Conservative scope:** the pre-existing same-shape blocks in
`_discover_input_path` (lines 397-407) and `_discover_output_path`
(lines 410-420) were deliberately NOT touched. Per IN-04 and the
helper-consolidation note in `.planning/codebase/CONCERNS.md`, those are
a separate milestone and changing all 3 sites at once expands the blast
radius beyond what the orchestrator authorized ("be conservative — only
convert silent `except Exception: pass` to a logged warning that
doesn't break the existing fallback semantics").

**Verification:**

1. Python AST parse on `teresa_gui.py` — OK.
2. `sys` already imported at line 21, no import change required.
3. Pytest: 774 passed / 1 xfailed / 0 failed (no regression).

## Skipped Issues

### WR-02: `_discover_temp_path()` is dead code — never invoked anywhere

**File:** `teresa_gui.py:423-434`
**Reason:** `decision: deferred — load-bearing for plan grep predicate`

Per orchestrator guidance and the explicit note in `04-VERIFICATION.md` /
`04-02-SUMMARY.md`, `_discover_temp_path()` exists deliberately to
satisfy a `grep -F 'def _discover_temp_path'` static acceptance predicate
in the phase plan. The plan also explicitly bans wiring this method into
the Paths panel ("Do NOT add `_discover_temp_path()` calls into the GUI's
'Paths' panel"). Removing the method would break the plan's grep
predicate; calling it from the existing GUI runtime would violate the
plan's explicit prohibition. Both options have side effects beyond a
straightforward fix.

A future helper-consolidation milestone (CONCERNS.md § IMPORTANT) is the
correct place to retire this dead-code artifact alongside its 3 siblings;
fixing it in isolation in the current phase trades one debt for another.

**Original issue:** Method `_discover_temp_path()` defined on
`TeresaWindow` but never called. Future readers will assume it's
load-bearing and either (a) propose calling it from `main()` — introducing
a self-reference cycle — or (b) wire it into the Paths panel and change
GUI surface area.

### WR-03: ONE_BUTTON_RUN.md no longer documents what `clean.ps1` actually removes

**File:** `spec_classifier/docs/dev/ONE_BUTTON_RUN.md:48-54`
**Reason:** `decision: deferred — phase 6 (DRIFT sweep) territory`

Per the reviewer's own note in REVIEW.md ("Phase 6 territory") and the
orchestrator guidance, the doc-vs-impl drift sweep is owned by Phase 6.
Fixing this in Phase 4 risks pre-empting Phase 6's broader drift audit
(IN-03 surfaces `RUN_PATHS_AND_IO_LAYOUT.md` as another doc that
references `PYTHONPYCACHEPREFIX` / `PYTEST_ADDOPTS` and is also deferred
to Phase 6). Phase 6 has the full drift inventory in scope; fixing one
doc here in isolation creates churn the Phase 6 author will then have to
re-coordinate against.

**Original issue:** The post-edit "Workspace cleanup" section dropped the
cache-type inventory (`__pycache__`, `.pytest_cache`, `.ruff_cache`,
`.mypy_cache`, `diag/`) and the dual-target sweep (`temp_root` + repo)
that the pre-edit doc documented. Operators reading the post-edit doc
will not know that clean wipes `.ruff_cache` / `.mypy_cache` / `diag/`
on every run.

---

_Fixed: 2026-05-10_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
