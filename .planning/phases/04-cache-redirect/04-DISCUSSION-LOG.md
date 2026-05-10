# Phase 4: Cache Redirect - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-10
**Phase:** 4-cache-redirect
**Areas discussed:** temp_root fallback + parser, clean.ps1 invocation contract, pytest cache redirect strategy, ONE_BUTTON_RUN.md edit scope

---

## Area A — temp_root fallback + parser

### A1. `temp_root` fallback when config.local.yaml is missing or omits the key

| Option | Description | Selected |
|--------|-------------|----------|
| Default to `$env:USERPROFILE\Desktop\temporary` | Mirrors clean.ps1's spirit and the example file's value. Silent, ergonomic; no-config user gets a working redirect. Same shape as the existing input_root/output_root fallbacks in run.ps1 (lines 33-34). | ✓ |
| Default to `Join-Path $RepoRoot 'temporary'` | Matches clean.ps1's actual fallback (line 8). Keeps cache adjacent to repo (but outside spec_classifier/) — risk of polluting working tree near the repo. | |
| Hard-fail with actionable message | Forces explicit configuration; less ergonomic; would trip first-time clones and CI smoke. | |
| Default to `$env:TEMP\teresa-pycache` | Uses the OS-managed temp dir. Most "correct" by Windows convention but loses locality with externalized state (INPUT/OUTPUT/temp all under Desktop today). | |

**User's choice:** Default to `$env:USERPROFILE\Desktop\temporary`
**Notes:** Captured as D-01. Python equivalent: `Path.home() / "Desktop" / "temporary"`. Mirrors existing `_discover_input_path` / `_discover_output_path` shape.

### A2. `temp_root` extraction approach in `teresa_gui.py`

| Option | Description | Selected |
|--------|-------------|----------|
| Add 5th line-by-line `startswith` block | Mirrors the existing _discover_input_path / _discover_output_path pattern in teresa_gui.py:397-421 verbatim. CONCERNS.md § IMPORTANT explicitly defers helper consolidation; extending the existing 4+-site pattern is the locked v1.1 stance. | ✓ |
| Use a Python regex matching run.ps1's pattern | Cross-language consistency between PS and Py parsers. Slightly different from the existing teresa_gui.py site (which uses startswith, not regex) — introduces a sub-pattern divergence inside one file. | |
| Use `yaml.safe_load` (pyyaml is already in stack) | Robust against quoting/multiline edge cases. But this is precisely the helper-consolidation work CONCERNS.md defers; would set a precedent the v1.1 init explicitly ruled out of scope. | |

**User's choice:** Add 5th line-by-line `startswith` block
**Notes:** Captured as D-03. Helper consolidation explicitly deferred; the regex/yaml options would set a precedent post-v1.1 owns.

---

## Area B — clean.ps1 invocation contract

### B1. When does `run.ps1` invoke `clean.ps1`?

| Option | Description | Selected |
|--------|-------------|----------|
| Once at very start of every run, before pipeline (and before -TestsOnly too) | Matches success criterion #3 verbatim ("a plain run.ps1 invokes clean.ps1 exactly once at the start of the run"). Ensures pytest, pipeline, and audit all run against a clean working tree. | ✓ |
| Start of full run only — -TestsOnly skips it | Tests-only path is currently a fast smoke; users running it back-to-back would see slower iterations if clean ran each time. Trade-off: -TestsOnly leaves prior __pycache__ in place between iterations. | |
| Conditional on `$env:PYTHONPYCACHEPREFIX` being set successfully | Defensive: only clean if redirect is wired. Adds branching complexity for a no-op safety check (env var setting can't fail). | |

**User's choice:** Once at the very start of every run, before pipeline (and before -TestsOnly too)
**Notes:** Captured as D-04. Implies the clean.ps1 call sits between line 42 (`Set-Location $SpecDir`) and line 71 (`-TestsOnly` short-circuit) of the current run.ps1.

### B2. clean.ps1 failure handling

| Option | Description | Selected |
|--------|-------------|----------|
| Warn and continue | Cleanup is non-essential to pipeline correctness — the cache redirect via PYTHONPYCACHEPREFIX is the core invariant. A locked file in $temp_root\__pycache__ shouldn't block a vendor run. | ✓ |
| Halt with non-zero exit | Strict: `$ErrorActionPreference = 'Stop'` is already set in run.ps1, so clean.ps1 throwing would naturally halt. Zero ambiguity but blocks runs on transient locks. | |
| Halt only when `-NoClean` was NOT passed AND clean.ps1 fails | Identical to halt-on-error in practice (since `-NoClean` skips the call entirely). Listed for completeness; collapses to "Halt". | |

**User's choice:** Warn and continue
**Notes:** Captured as D-06. Requires wrapping the call in `try { ... } catch { Write-Host "... — continuing" -ForegroundColor Yellow }` because `$ErrorActionPreference = "Stop"` is set globally on line 21.

---

## Area C — Pytest cache redirect strategy

### C1. Handling `.pytest_cache` (PYTHONPYCACHEPREFIX redirects only bytecode)

| Option | Description | Selected |
|--------|-------------|----------|
| Set `PYTEST_ADDOPTS='-o cache_dir=$temp_root\.pytest_cache'` in run.ps1 (and same in teresa_gui.py via os.environ) | Same env-var mechanism as PYTHONPYCACHEPREFIX. Symmetric: one env var per cache type, set at the same point in the same files. No diff in spec_classifier/ (D-22 safe). After a vanilla `.\run.ps1`, `.pytest_cache` lands in `$temp_root`, never in the repo. | ✓ |
| Rely on clean.ps1 sweep — don't redirect | Strictly meets success criterion #1 (which uses -SkipTests). But a vanilla `.\run.ps1` will create `.pytest_cache` in the repo each run; clean.ps1 wipes it at next start. Race window: between pytest finishing and next run, `.pytest_cache` exists in working tree. | |
| Add `cache_dir` to `spec_classifier/pyproject.toml [tool.pytest.ini_options]` | Persistent / declarative. But pyproject.toml is the same file ORPH-01 will rewrite line 5 in Phase 5 — adding pytest config in Phase 4 risks merge churn. And the cache_dir would have to be relative or hard-coded; can't reference `$temp_root` from yaml config. | |

**User's choice:** Set `PYTEST_ADDOPTS='-o cache_dir=$temp_root\.pytest_cache'` in run.ps1 (and same in teresa_gui.py)
**Notes:** Captured as D-08, D-09. Implementation expansion beyond literal CACHE-01/CACHE-02 wording; closes the latent gap so vanilla `.\run.ps1` (no -SkipTests) doesn't leave `.pytest_cache` in the repo. D-22 safe (no edits inside protected paths).

---

## Area D — ONE_BUTTON_RUN.md edit scope

### D1. Scope of the ONE_BUTTON_RUN.md edit (CACHE-04 + grep gate)

| Option | Description | Selected |
|--------|-------------|----------|
| Comprehensive: rewrite Workspace cleanup section + update numbered "What run.ps1 does" list (insert step 0/1: cleans cache) + add `-NoClean` to switches block | Three coordinated edits keep the doc internally consistent. A reader scanning either the numbered list, the switches table, or the Workspace cleanup section gets the same story. Acceptance gate (`-NoClean` + `clean.ps1` co-occur in Workspace cleanup) is met. | ✓ |
| Minimal: rewrite only the Workspace cleanup section to mention default-on + `-NoClean` | Smallest patch that satisfies the grep gate. But leaves the numbered "What run.ps1 does" list claiming the pipeline starts at step 1 "Finds the repo root", when it now starts with cleanup. Mild doc drift the Phase 6 sweep would catch. | |
| Minimal + switches block update only (skip the numbered list) | Middle ground. Switches block needs `-NoClean` entry to be discoverable. Numbered list drift is small; Phase 6's mechanical sweep targets "code does X" claims, and "Finds the repo root" isn't a code-does-X claim. | |

**User's choice:** Comprehensive — three coordinated edits
**Notes:** Captured as D-11. Phase 4 is the only phase that should touch ONE_BUTTON_RUN.md before Phase 6's sweep (D-12 explicitly forbids touching other docs).

---

## Wrap-up

| Question | Selected |
|----------|----------|
| Anything to add before writing CONTEXT.md? | Write CONTEXT.md now |

---

## Claude's Discretion

- Exact wording of the new run.ps1 header banner line for clean mode (D-07).
- Exact phrasing of inserted ONE_BUTTON_RUN.md numbered-list step (D-11.1).
- Whether the GUI's env-var setting block is a small helper function or inlined in `main()` — both meet CACHE-02.

## Deferred Ideas

- **`load_config_with_local()` helper consolidation** — explicit non-goal; post-v1.1.
- **`yaml.safe_load` adoption in launcher/GUI** — would set the precedent the helper-consolidation milestone owns.
- **`pyproject.toml [tool.pytest.ini_options] cache_dir`** — rejected for Phase 4 (merge churn with ORPH-01 in Phase 5; can't reference `$temp_root`).
- **GUI defense-in-depth env-var setting at button-click time** — overkill; D-13 covers it via process-level env vars.
- **POSIX `run.sh` mirror** — backlog v2.0+ (PLAT-01).
