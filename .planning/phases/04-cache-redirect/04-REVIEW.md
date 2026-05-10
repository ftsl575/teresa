---
phase: 04-cache-redirect
reviewed: 2026-05-10T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - run.ps1
  - teresa_gui.py
  - spec_classifier/docs/dev/ONE_BUTTON_RUN.md
findings:
  critical: 0
  warning: 4
  info: 5
  total: 9
status: issues_found
---

# Phase 4: Code Review Report

**Reviewed:** 2026-05-10
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Phase 04 ("cache-redirect") wires `PYTHONPYCACHEPREFIX` and `PYTEST_ADDOPTS` from
`config.local.yaml::temp_root` into both `run.ps1` and `teresa_gui.py`, makes
`clean.ps1` default-on with a `-NoClean` opt-out switch, and updates
`ONE_BUTTON_RUN.md` to reflect the new contract.

The mechanical wiring meets the success criteria laid out in `04-CONTEXT.md` and
both implementation summaries: env vars are set in the right ordering (BEFORE
`Set-Location`, BEFORE `QApplication`, BEFORE any `subprocess.Popen`); the
`-NoClean` switch threads cleanly into `param()` and the cleanup gate; the regex
clause for `temp_root` reuses the established pattern shape verbatim. PowerShell
parses without syntax errors after the documented em-dash → `--` substitution
in 04-01-SUMMARY.

That said, the implementation has correctness and quality defects worth fixing
before this code carries production weight:

- **Path-with-spaces hazard in `PYTEST_ADDOPTS`.** Both `run.ps1` and
  `teresa_gui.py` build the `-o cache_dir=<path>` token without quoting the
  path. pytest tokenizes `PYTEST_ADDOPTS` with `shlex`-style splitting; a
  `temp_root` containing a space (e.g., `C:\Users\Some User\temp`) silently
  splits into multiple tokens, producing a malformed pytest command. The two
  test machines used in 04-01-SUMMARY happen to have space-free paths
  (`C:\Users\G\Desktop\temporary`), so the smoke didn't catch this.
- **`_discover_temp_path()` is dead code.** Added to `TeresaWindow` per the
  plan, but never invoked anywhere in `teresa_gui.py`; the GUI's "Paths" panel
  shows only Input / Output. The plan text explicitly says "do NOT add
  `_discover_temp_path()` calls into the GUI's Paths panel" — meaning the
  method exists solely to satisfy a static `grep` predicate in the plan's
  acceptance criteria, not because runtime code calls it. Net effect: a
  permanent unreferenced symbol on the class.
- **Doc-vs-impl drift in ONE_BUTTON_RUN.md.** The new step 1 says clean
  removes `__pycache__` / `.pytest_cache`, but `clean.ps1` also removes
  `.ruff_cache`, `.mypy_cache`, and `diag/`. The pre-edit doc's "Workspace
  cleanup" tail listed those caches; the rewrite drops them, leaving operators
  with an inaccurate mental model.
- **Two unrelated regressions on the existing `_discover_input_path` /
  `_discover_output_path` methods are NOT introduced by this phase but become
  more visible because the same parser is now duplicated a 3rd time** (see
  IN-04 below).

No security defects (no injection vector — values flow through `Join-Path` /
`pathlib.Path`, not `Invoke-Expression` / `subprocess(shell=True)`).

## Warnings

### WR-01: `PYTEST_ADDOPTS` `cache_dir` value is unquoted — breaks for `temp_root` paths containing spaces

**File:** `run.ps1:47` and `teresa_gui.py:554`

**Issue:**
Both launchers build the pytest cache option as a single unquoted token:

```powershell
# run.ps1:47
$pytestCacheArg = "-o cache_dir=$(Join-Path $TempRoot '.pytest_cache')"
```

```python
# teresa_gui.py:554
pytest_cache_arg = f"-o cache_dir={Path(temp_root) / '.pytest_cache'}"
```

pytest reads `PYTEST_ADDOPTS` and splits it on whitespace via `shlex`-style
parsing (`_pytest.config.get_common_ancestor` / `Config._preparse`). If
`temp_root` contains a space — e.g., `C:\Users\Some User\Desktop\temporary` —
the resulting env var value becomes:

```
-o cache_dir=C:\Users\Some User\Desktop\temporary\.pytest_cache
```

shlex tokenizes this into `["-o", "cache_dir=C:\Users\Some", "User\Desktop\temporary\.pytest_cache"]`
which makes pytest see `-o` followed by the truncated value `cache_dir=C:\Users\Some`,
then a stray positional `User\Desktop\temporary\.pytest_cache` it can't resolve.
Pytest will either fail outright or silently fall back to the default cache
location inside the repo — defeating CACHE-01/CACHE-02.

This was not caught by the 04-01 smoke because `C:\Users\G\Desktop\temporary`
has no spaces. It will silently regress on any machine where the user profile
or `temp_root` includes a space.

**Fix:** Quote the path inside the option value:

```powershell
# run.ps1
$pytestCacheArg = "-o cache_dir=`"$(Join-Path $TempRoot '.pytest_cache')`""
```

```python
# teresa_gui.py
pytest_cache_arg = f'-o cache_dir="{Path(temp_root) / ".pytest_cache"}"'
```

(In PowerShell, the backticks escape the embedded double-quote; in Python the
outer single-quoted f-string lets a literal `"` sit inside the value.)
Verify on a path with a space: pytest must still resolve the cache to the
quoted directory.

---

### WR-02: `_discover_temp_path()` is dead code — never invoked anywhere

**File:** `teresa_gui.py:423-434`

**Issue:**
The new method `_discover_temp_path()` was added to `TeresaWindow` (sibling of
`_discover_input_path` / `_discover_output_path`), but no caller exists.
`grep -n "_discover_temp_path" teresa_gui.py` shows only the definition at
line 423; the GUI's "Paths" panel (`_build_right_column`, lines 354-381)
never instantiates a `path_temp` label or calls `self._discover_temp_path()`.
`main()` does its own inline parse (lines 541-552) instead of calling the
method.

The plan's `<action>` block explicitly bans wiring this method into the UI
("Do NOT add `_discover_temp_path()` calls into the GUI's 'Paths' panel"), and
the plan's rationale for not calling it from `main()` was that `TeresaWindow`
hadn't been instantiated yet. The method therefore exists solely to satisfy
the plan's `grep -F 'def _discover_temp_path'` acceptance check — i.e., as a
test-driven artifact, not as runtime code.

Two consequences:

1. Future readers will see the method and assume it's load-bearing. They will
   propose calling it from `main()` (introducing a self-reference cycle since
   `_discover_temp_path` is on `TeresaWindow`) or from the Paths panel
   (changing GUI surface area).
2. Any future change to the parsing convention (e.g., the helper-consolidation
   milestone CONCERNS.md flags) now has 6 sites to update, one of which is
   strictly unreachable.

**Fix:** Either (a) remove the method since `main()` already inlines the
logic, or (b) actually use it — surface `temp_root` in the Paths panel
alongside Input/Output, and have `main()` instantiate via a module-level
helper that the method delegates to. Option (a) is cheaper and matches the
plan's intent ("CACHE-02 is satisfied by the env-var redirect alone, not by
visible UI state").

---

### WR-03: ONE_BUTTON_RUN.md no longer documents what `clean.ps1` actually removes

**File:** `spec_classifier/docs/dev/ONE_BUTTON_RUN.md:48-54`

**Issue:**
The pre-edit doc had an explicit cleanup contract:

> Removes `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache` from the working tree.
> Does not touch: golden files, OUTPUT.

The post-edit "Workspace cleanup" section drops both lines and replaces them
with a brief "invokes clean.ps1 automatically at the start of every run" blurb.

Reading `clean.ps1` itself: it removes `__pycache__`, `.pytest_cache`,
`.ruff_cache`, `.mypy_cache`, AND `diag/` from BOTH `$TempRoot` and the repo
working tree. The post-edit doc neither (a) documents `.ruff_cache` /
`.mypy_cache` / `diag/`, nor (b) documents the dual-target sweep
(`temp_root` + repo). The new step 1 says "from `temp_root` and the working
tree", which is correct, but the rest of the doc loses the cache-type
inventory.

This is a doc-vs-impl drift: an operator reading the doc will not know that
clean wipes their `.ruff_cache` / `.mypy_cache` / `diag/` directories on every
run. That matters because (per `clean.ps1:49-52`) `diag/` carries run logs —
operators may be surprised to find their last run's logs gone after the next
default invocation.

**Fix:** Restore the cache-type inventory in the rewritten section, e.g.:

```markdown
## Workspace cleanup

`run.ps1` invokes `.\spec_classifier\scripts\clean.ps1` automatically at the
start of every run. Pass `-NoClean` to opt out. To clean manually:

\`\`\`powershell
.\spec_classifier\scripts\clean.ps1
\`\`\`

Removes from both `$temp_root` and the repo working tree:
`__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `diag/`.
Does not touch: `golden/`, `test_data/`, `OUTPUT/`.
```

This restores the contract the pre-edit doc made and aligns with what
`clean.ps1` actually does.

---

### WR-04: GUI's `temp_root` parser silently swallows YAML parse errors and uses Desktop fallback — masks real misconfiguration

**File:** `teresa_gui.py:543-552` (and pre-existing same shape at 397-407 / 410-420)

**Issue:**
The new parsing block in `main()` wraps the read in a bare `except Exception:
pass`, mirroring the existing pattern from `_discover_input_path()` /
`_discover_output_path()`. The block silently falls back to
`Path.home() / "Desktop" / "temporary"` on ANY exception — including a typo'd
YAML key, a permission error, an encoding mismatch, or a malformed value.

Because `run.ps1` ALSO sets the env vars (D-13 defense-in-depth), the GUI's
fallback can produce a divergent `temp_root` between GUI parent and `run.ps1`
child if the YAML parse succeeds in PowerShell (different parser) but throws
in Python — e.g., a UTF-8 BOM or an unescaped backslash in the path. The two
processes then write `__pycache__` to two different locations, and `clean.ps1`
(which uses the PowerShell parser) only sweeps one of them.

This is a Phase 4 expansion of a pre-existing pattern problem (the GUI's path
discovery has always swallowed errors), so it's a Warning rather than a
Blocker — but the new env-var setting amplifies the blast radius because
divergence now affects every Python invocation, not just a UI label.

**Fix:** At minimum, log to stderr when the fallback fires, so divergence is
diagnosable:

```python
except Exception as e:
    print(f"[teresa_gui] WARN: failed to parse temp_root from {cfg}: {e}; "
          f"using fallback {temp_root}", file=sys.stderr)
```

Consolidation into a single helper that both `run.ps1` (via `python -c`) and
the GUI use is a separate milestone per CONCERNS.md, but logging the silent
swallow today is cheap.

## Info

### IN-01: `Set-Location $SpecDir` is not symmetric with later script invocations — operator's cwd is permanently changed

**File:** `run.ps1:54`

**Issue:**
The script does `Set-Location $SpecDir` on line 54 but never restores the
operator's prior cwd. If the operator dot-sources the script (`. .\run.ps1`)
or runs it inside an existing PowerShell session, their cwd is permanently
moved into `spec_classifier/` after the script returns. This is pre-existing
behavior (not introduced by Phase 4), but the new cleanup block on lines
57-68 makes the cwd dependency more obvious — `& $CleanScript` works
regardless of cwd because the path is absolute, but the pre-Phase-4 reader
might assume `Set-Location` is just a convenience.

**Fix:** None required for Phase 4. If revisited later, wrap the body in
`Push-Location $SpecDir` / `Pop-Location` and move the cleanup invocation
inside that scope; or use `Push-Location $SpecDir; try { ... } finally
{ Pop-Location }`.

---

### IN-02: `Path(temp_root)` vs raw string mixing in `os.environ` values

**File:** `teresa_gui.py:553-554`

**Issue:**
Line 553: `os.environ["PYTHONPYCACHEPREFIX"] = str(Path(temp_root) / "__pycache__")`
Line 554: `pytest_cache_arg = f"-o cache_dir={Path(temp_root) / '.pytest_cache'}"`

The first line explicitly converts to `str`; the second uses f-string
interpolation, which calls `__format__` on the `Path` object, producing the
same string but via a different code path. On Windows both produce
backslash-separated paths. Functionally identical but stylistically
inconsistent — minor maintainability snag.

**Fix:** Pick one form. Recommend the explicit `str(...)` form for both, to
match the established convention in `os.environ` assignments and to make grep
predicates easier to write.

---

### IN-03: `RUN_PATHS_AND_IO_LAYOUT.md` references `PYTHONPYCACHEPREFIX` / `PYTEST_ADDOPTS` but is not updated by Phase 4

**File:** `spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md` (out of phase scope, but cross-checked)

**Issue:**
A `grep -r PYTHONPYCACHEPREFIX spec_classifier/` shows the env var is
mentioned in `RUN_PATHS_AND_IO_LAYOUT.md` and `pyproject.toml` (line 4
comment). The Phase 4 plan (D-12) explicitly defers cross-doc reconciliation
to Phase 6's drift sweep, so this is a known-deferred item, not a defect in
Phase 4's implementation. Surfacing for completeness so Phase 6 reviewers
remember to look here.

**Fix:** Phase 6 owns this; no action in Phase 4.

---

### IN-04: Pre-existing `_discover_input_path` / `_discover_output_path` parser will misread YAML if `paths:` block has a sibling key with the same suffix

**File:** `teresa_gui.py:397-421` (pre-existing — not introduced by Phase 4)

**Issue:**
The parser uses `line.startswith("input_root:")` AFTER `line.strip()`. This
strips leading whitespace, so a nested `input_root:` (under `paths:`) matches
identically to a top-level one. Currently the actual `config.local.yaml` has
`input_root` nested under `paths:` and `temp_root` at the top level; both are
read correctly. But:

- A YAML comment line `# input_root: example` would be skipped because it
  starts with `#`, not `input_root:`. OK.
- A line like `paths_input_root:` would NOT match because of the prefix
  `paths_`. OK.
- A line like `input_root_extra: foo` would NOT match because `:` immediately
  follows `input_root`. Wait — `startswith("input_root:")` requires a colon
  right after, so `input_root_extra:` does not match. OK.

So the parser is robust for current YAML shapes. Surfaced only because Phase
4 just added a 3rd copy of this exact code, doubling the maintenance surface
the helper-consolidation milestone (CONCERNS.md § IMPORTANT) will eventually
have to consolidate.

**Fix:** No action in Phase 4. Helper consolidation is its own milestone.

---

### IN-05: Header banner uses inconsistent label widths

**File:** `run.ps1:88-94`

**Issue:**
The header lines are:

```
 Repo:     $RepoRoot
 Input:    $InputRoot
 Output:   $OutputRoot
 Vendors:  $($VendorsToRun -join ', ')
 AI audit: $(...)
 Tests:    $(...)
 Clean:    $(...)
```

The labels `Repo:`, `Input:`, `Output:`, `Vendors:`, `Tests:`, `Clean:` use 4
spaces of right-padding to the value, but `AI audit:` uses only 1 space. This
is pre-existing inconsistency (not introduced by Phase 4 — the new `Clean:`
line follows the dominant 4-space pattern correctly), but worth flagging
because the 04-01-PLAN.md explicitly claims a "9-character left-aligned label
width" which doesn't match what shipped.

**Fix:** Cosmetic. If revisited, normalize to a consistent column.

---

_Reviewed: 2026-05-10_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
