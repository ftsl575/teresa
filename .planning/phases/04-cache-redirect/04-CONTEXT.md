# Phase 4: Cache Redirect - Context

**Gathered:** 2026-05-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire `PYTHONPYCACHEPREFIX` (and pytest's `cache_dir`) from `config.local.yaml::temp_root`
through both runtime entry points — `run.ps1` (CLI/`teresa.bat`) and `teresa_gui.py`
(GUI dispatch) — so that runtime `__pycache__` and `.pytest_cache` artifacts land in
`$temp_root\__pycache__` and `$temp_root\.pytest_cache`, never inside the repo working
tree, for any vendor pipeline run.

Make `clean.ps1` invocation default-on at the start of every `run.ps1` invocation
(including `-TestsOnly`), with a `-NoClean` switch as the explicit opt-out. Reflect the
new contract in `spec_classifier/docs/dev/ONE_BUTTON_RUN.md`.

**Strictly out of scope** (explicit non-goals from v1.1 init):
- Consolidating the 4+ `config.local.yaml` regex/parse sites into a single
  `load_config_with_local()` helper. Phase 4 *extends* the existing pattern with a 5th
  site (PowerShell + Python both); helper consolidation is deferred per CONCERNS.md
  § IMPORTANT.
- Any diff inside D-22 protected paths
  (`spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}`).
  Phase gate fails on a non-empty diff there.
- Goldens regen, classifier behavior changes, or test refactors.

</domain>

<decisions>
## Implementation Decisions

### Area A — `temp_root` resolution

- **D-01 (fallback value):** When `config.local.yaml` is missing OR present but omits
  `temp_root`, both `run.ps1` and `teresa_gui.py` default to
  `$env:USERPROFILE\Desktop\temporary` (Python equivalent: `Path.home() / "Desktop" / "temporary"`).
  Mirrors the existing `input_root`/`output_root` fallback shape in `run.ps1:33-34` and
  `teresa_gui.py:408,421`. No-config users get a working redirect silently.
- **D-02 (PowerShell parser):** `run.ps1` reads `temp_root` via the same regex pattern
  already used at `run.ps1:36-40` for `input_root`/`output_root`. Add one more
  `if ($cfg -match ...)` block after the existing two. Pattern:
  `'(?m)^\s*temp_root:\s*["'']?([^"''\r\n]+)["'']?\s*$'`. Note: `temp_root` in the
  example file is currently a **top-level** key, not nested under `paths:` — keep that
  shape; do not nest. Confirm by re-reading `spec_classifier/config.local.yaml.example:12`.
- **D-03 (Python parser in GUI):** `teresa_gui.py` adds a new
  `_discover_temp_path()` method that mirrors `_discover_input_path()` /
  `_discover_output_path()` (lines 397-421) verbatim — line-by-line `text.splitlines()`
  loop with `line.startswith("temp_root:")`. This is the **5th site** of the regex
  pattern CONCERNS.md flags; consolidation is explicitly deferred. Do NOT introduce
  `yaml.safe_load` here (would set the precedent the v1.1 init ruled out).

### Area B — `clean.ps1` invocation contract

- **D-04 (timing):** `run.ps1` invokes `clean.ps1` exactly once at the very start of
  every run, immediately after path discovery (after `Set-Location $SpecDir` on line 42)
  and BEFORE the `-TestsOnly` short-circuit (line 71). Tests-only runs also benefit
  from a clean working tree. Matches success criterion #3 verbatim ("a plain run.ps1
  invokes clean.ps1 exactly once at the start of the run").
- **D-05 (`-NoClean` flag):** Add `[switch]$NoClean` to the `param()` block
  (`run.ps1:14-19`). When `-NoClean` is passed, skip the `clean.ps1` invocation
  entirely. No other behavior changes — pipeline, audit, and tests run as today.
- **D-06 (failure handling):** Wrap the `clean.ps1` invocation in `try { ... } catch {
  Write-Host "clean.ps1 failed: $($_.Exception.Message) — continuing" -ForegroundColor
  Yellow }`. Required because `$ErrorActionPreference = "Stop"` is set globally on
  `run.ps1:21` and would otherwise halt the run on a transient lock. Cleanup is
  non-essential to pipeline correctness — the cache redirect itself is the load-bearing
  invariant; sweeping is best-effort.
- **D-07 (header reflection):** Update the header banner block (`run.ps1:57-68`) to add
  one line indicating clean mode, e.g. `Clean: $(if ($NoClean) { 'OFF (manual)' } else
  { 'ON (clean.ps1 at start)' })`. Cosmetic but consistent with how `AI audit:` and
  `Tests:` are surfaced today.

### Area C — pytest cache redirect

- **D-08 (mechanism):** Set `$env:PYTEST_ADDOPTS = "-o cache_dir=$temp_root\.pytest_cache"`
  in `run.ps1` immediately alongside the `$env:PYTHONPYCACHEPREFIX` assignment. In
  `teresa_gui.py`, set `os.environ["PYTEST_ADDOPTS"] = f"-o cache_dir={temp_root}\\.pytest_cache"`
  in the same block as `os.environ["PYTHONPYCACHEPREFIX"]`. This is the symmetric
  partner to PYTHONPYCACHEPREFIX — one env var per cache type, set at the same point in
  the same files. **D-22 safe** because it touches launchers only, never `conftest.py`
  or `pyproject.toml` inside `spec_classifier/`.
- **D-09 (extends CACHE-01/CACHE-02 wording):** The literal CACHE-01 / CACHE-02
  requirement text mentions only `PYTHONPYCACHEPREFIX`. Adding `PYTEST_ADDOPTS` is an
  implementation expansion, not a scope change — without it, vanilla `.\run.ps1`
  (without `-SkipTests`) leaves `.pytest_cache` in the repo until next clean. Success
  criterion #1 happens to use `-SkipTests` so it would pass either way; the env-var
  partner closes the latent gap without a separate requirement.
- **D-10 (PYTEST_ADDOPTS overwrite policy):** If `$env:PYTEST_ADDOPTS` is already set
  in the user's shell, append to it rather than overwrite (e.g.
  `"$env:PYTEST_ADDOPTS -o cache_dir=..."`). Defensive; uncommon but cheap.

### Area D — `ONE_BUTTON_RUN.md` edit scope (CACHE-04)

- **D-11 (scope):** Apply three coordinated edits to `spec_classifier/docs/dev/ONE_BUTTON_RUN.md`:
  1. **"What run.ps1 does" numbered list (lines 10-19):** Insert a new step 1 ("Cleans
     prior `__pycache__` / `.pytest_cache` from temp_root and working tree (skip with
     `-NoClean`)") and renumber subsequent steps.
  2. **Useful run.ps1 switches block (lines 36-44):** Add a `-NoClean` entry with a
     one-line description (e.g. `.\run.ps1 -NoClean   # skip the start-of-run clean.ps1 sweep`).
  3. **Workspace cleanup section (lines 46-53):** Rewrite to: "`run.ps1` invokes
     `.\spec_classifier\scripts\clean.ps1` automatically at the start of every run.
     Pass `-NoClean` to opt out. To clean manually without running the pipeline:
     `.\spec_classifier\scripts\clean.ps1`." Acceptance gate (`-NoClean` and
     `clean.ps1` co-occur in the Workspace cleanup section) is met by item 3.
- **D-12 (no other docs touched):** ONE_BUTTON_RUN.md is the only doc CACHE-04 names.
  Do NOT edit `RUN_PATHS_AND_IO_LAYOUT.md`, README.md, or any other doc in Phase 4 —
  Phase 6's mechanical drift sweep handles cross-doc reconciliation against the
  post-Phase-4-and-5 tree.

### Cross-cutting

- **D-13 (set-env precedence in GUI):** `teresa_gui.py` sets `os.environ["PYTHONPYCACHEPREFIX"]`
  and `os.environ["PYTEST_ADDOPTS"]` in `__main__` (i.e., inside `main()` on
  `teresa_gui.py:523` BEFORE `app = QApplication(sys.argv)`), so any subprocess spawned
  later (`subprocess.Popen` for PowerShell launches at `teresa_gui.py:225`) inherits
  them. `run.ps1` will then re-set them from `temp_root` redundantly — by design,
  defense in depth, identical values, no observable conflict.
- **D-14 (vendor `temp_root` doc note):** `spec_classifier/config.local.yaml.example:11`
  currently says `# Used by scripts/clean.ps1 and scripts/run_full.ps1.` (the second
  reference is stale and is fixed by ORPH-02 in Phase 5). Phase 4 leaves that comment
  alone — Phase 5 owns the rewrite. Coordination is intentional per the v1.1
  sequential-execution decision.

### Claude's Discretion

- Exact wording of header banner addition in run.ps1 (D-07) — any clear short label.
- Exact phrasing of inserted ONE_BUTTON_RUN.md numbered-list step (D-11.1).
- Whether the GUI's env-var setting block is a small helper function or inline in
  `main()` — matter of style; both meet CACHE-02.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope, requirements, gates
- `.planning/ROADMAP.md` § "Phase 4: Cache Redirect" — goal, success criteria 1-5,
  D-22 / pytest-skip / goldens-byte-equal gates verbatim
- `.planning/REQUIREMENTS.md` § "Cache Redirect (CACHE) — Plan 1" — CACHE-01..04
  verbatim, smoke-verification commands
- `.planning/PROJECT.md` § "Current Milestone: v1.1" + "Constraints" — milestone goals,
  no-tech-stack-additions, sequential-plan dependency
- `.planning/STATE.md` § "Decisions" — `[v1.1 Init]` lines locking helper-consolidation
  exclusion and sequential plan dependency

### Architectural guards (do NOT touch)
- `.planning/codebase/CONCERNS.md` § BLOCKER — full list of "do-not-fix" items
  (`power_cord` taxonomy, Dell-specific parser, audit-reads-Excel, etc.) that remain
  load-bearing during Phase 4
- `.planning/codebase/CONCERNS.md` § IMPORTANT § "config.local.yaml overlay logic is
  duplicated in 4+ places" — the explicit guard that Phase 4 extends the pattern
  rather than consolidating it. Helper extraction deferred post-v1.1.
- `CLAUDE.md` (root) § "Critical business rules" + § "Code-only repository policy" —
  D-22 protected paths and "do not fix" rules
- `spec_classifier/CLAUDE.md` § "Business Rules" + § "Known Tech Debt" — deep
  reference for the same exclusions

### Files Phase 4 will edit
- `run.ps1` — current state at lines 14-19 (`param()`), 21 (`$ErrorActionPreference =
  "Stop"`), 33-40 (`config.local.yaml` regex parsing), 42 (`Set-Location $SpecDir`),
  57-68 (header banner), 71-76 (`-TestsOnly` short-circuit). Edits per D-02, D-04..D-08.
- `teresa_gui.py` — current state at lines 397-421 (`_discover_input_path` /
  `_discover_output_path`), 211-229 (`launch_run_ps1` / `subprocess.Popen` boundary),
  523-528 (`main()` entry). Edits per D-03, D-08, D-13.
- `spec_classifier/docs/dev/ONE_BUTTON_RUN.md` — current state at lines 10-19, 36-44,
  46-53. Edits per D-11.

### Files Phase 4 reads but does NOT edit
- `spec_classifier/scripts/clean.ps1` — already exists, already reads `temp_root` from
  `config.local.yaml` (line 12), already sweeps `__pycache__`, `.pytest_cache`,
  `.ruff_cache`, `.mypy_cache`, and `diag/` from both temp and repo. Phase 4 wires its
  invocation; no edits to its body.
- `spec_classifier/config.local.yaml.example` — confirms `temp_root` is a top-level
  key (line 12), not nested. ORPH-02 (Phase 5) edits the comment on line 11; Phase 4
  leaves it alone.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`run.ps1:36-40`** — existing two-clause regex parsing of `config.local.yaml` for
  `input_root` / `output_root`. Pattern is `'(?m)^\s*<key>:\s*["'']?([^"''\r\n]+)["'']?\s*$'`.
  Phase 4 adds a third clause for `temp_root` using the identical pattern shape.
- **`run.ps1:33-34`** — `$env:USERPROFILE\Desktop\<NAME>` fallback shape for
  `InputRoot` / `OutputRoot`. Phase 4 reuses it for `TempRoot`.
- **`teresa_gui.py:397-421`** — line-by-line `text.splitlines()` parser for `input_root`
  / `output_root` with `Path.home() / "Desktop" / "<NAME>"` fallback. Phase 4 clones it
  for `temp_root` (D-03).
- **`teresa_gui.py:217-229` (`launch_run_ps1`)** — `subprocess.Popen` with
  `creationflags=CREATE_NEW_CONSOLE`. Already inherits the parent process's environment;
  any env vars set in `main()` propagate to the spawned PowerShell.
- **`spec_classifier/scripts/clean.ps1`** — full-fat sweep already exists: temp_root
  `__pycache__`, temp_root `.pytest_cache`, repo-tree `.pytest_cache`, recursive
  `__pycache__` under repo (line 34), `.ruff_cache`, `.mypy_cache`, `diag/`. No edits
  needed — Phase 4 just calls it.

### Established Patterns
- **First-match-wins YAML rule order is load-bearing** — irrelevant to Phase 4 (no
  rules edits) but reaffirmed by D-22 protection.
- **Self-locating paths** — `run.ps1:25` uses `$PSScriptRoot`; `teresa_gui.py:41` uses
  `Path(__file__).resolve().parent`. Phase 4 follows the same pattern when resolving
  `temp_root` defaults.
- **Defense-in-depth env-var setting** (D-13) — both GUI and run.ps1 set the env vars
  independently from the same `temp_root` source. Redundant but consistent.

### Integration Points
- **GUI → PowerShell handoff:** `teresa_gui.py:225` `subprocess.Popen` is the boundary.
  Setting env vars before `main()` returns guarantees inheritance.
- **PowerShell → Python invocations:** `run.ps1:74,108,118,127,137,147` all call
  `python ...` after `Set-Location $SpecDir`. `$env:PYTHONPYCACHEPREFIX` and
  `$env:PYTEST_ADDOPTS` must be set before the first such call (i.e., before line 74's
  `-TestsOnly` short-circuit).

</code_context>

<specifics>
## Specific Ideas

- Reuse the **exact** regex pattern shape from `run.ps1:38-39` for `temp_root`. Don't
  introduce a new pattern style; mechanical consistency is what makes Phase 6's drift
  sweep tractable.
- Cleanup error handling (D-06) — `try { & $CleanScript } catch { Write-Host "..." }`
  with the warning printed in Yellow, matching the existing colored-output convention
  used throughout `run.ps1` (Cyan for headers, Yellow for warnings, Red for errors,
  Green for success).
- ONE_BUTTON_RUN.md edits (D-11) keep the existing tone: imperative, terse, code-fenced
  PowerShell. Don't add prose explaining *why* the cache is redirected — that belongs
  in `RUN_PATHS_AND_IO_LAYOUT.md`, not the one-button quick start.

</specifics>

<deferred>
## Deferred Ideas

- **`load_config_with_local()` helper consolidation** — explicit non-goal; deferred
  to its own post-v1.1 milestone per CONCERNS.md § IMPORTANT and the v1.1 init
  decision in STATE.md. After Phase 4 lands, the regex pattern will exist at 5+ sites
  (`run.ps1`, `teresa_gui.py:_discover_input_path`,
  `teresa_gui.py:_discover_output_path`, `teresa_gui.py:_discover_temp_path` (new),
  plus `main.py`, `conftest.py`, `batch_audit.py`, `cluster_audit.py` overlays).
  Consolidation deserves its own discussion + plan.
- **`yaml.safe_load` adoption in launcher/GUI** — would set the precedent that the
  helper-consolidation milestone needs to set; not Phase 4's call.
- **`pyproject.toml [tool.pytest.ini_options] cache_dir`** — declarative pytest cache
  config considered and rejected for Phase 4: pyproject.toml is the file ORPH-01
  rewrites in Phase 5 (line 5 reference fix), and a static `cache_dir` can't reference
  `$temp_root` from `config.local.yaml`. Env-var approach (D-08) wins on both axes.
- **GUI defense-in-depth env-var setting at `_run_vendor` / `_run_full` button-click
  time** (rather than once at `main()`) — overkill; D-13 covers it via the
  process-level env vars. Reopen if a regression appears.
- **POSIX `run.sh` mirror** — backlog v2.0+ (PLAT-01); explicitly out of scope per
  REQUIREMENTS.md § Out of Scope.

</deferred>

---

*Phase: 4-cache-redirect*
*Context gathered: 2026-05-10*
