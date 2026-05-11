---
phase: 06-doc-vs-impl-drift-sweep
plan: 04
subsystem: docs
tags: [doc-trim, run-ps1-help, drift-02, drift-01, sweep]
requirements_satisfied: [DRIFT-02]
requirements_partial: [DRIFT-01]
dependency_graph:
  requires:
    - phase-04-cache-redirect (env-var vocabulary used in PYTHONPYCACHEPREFIX patch)
    - phase-05-orphan-cleanup (no run_full ORPH gate inherited)
    - 06-01 (sweep schema + 06-DRIFT-AUDIT.md skeleton)
  provides:
    - "run.ps1 -? returns useful help (DOC_INVARIANTS #8 prerequisite)"
    - "DRIFT-02 trim done on both named docs with literal pointer to run.ps1 -?"
    - "DRIFT-01 sweep portion done for the 2 trim-target docs (44 claim rows added: 16 ONE_BUTTON_RUN + 28 RUN_PATHS)"
  affects:
    - run.ps1 (comment-based help block; comments-only edit per D-08)
    - spec_classifier/docs/dev/ONE_BUTTON_RUN.md (trimmed 54 → 50)
    - spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md (trimmed 281 → 264)
    - .planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md (sweep rows appended)
tech-stack:
  added: []
  patterns:
    - "PowerShell comment-based help (`<#.SYNOPSIS / .DESCRIPTION / .PARAMETER (×5) / .EXAMPLE (×6) #>`) — ships canonical RFC-style help that `Get-Help .\\run.ps1` and `.\\run.ps1 -?` both render."
    - "Trim-and-pointer: duplicated CLI prose collapsed into a one-line cross-reference to the canonical doc + the new in-shell help, retaining tables (load-bearing) per D-09."
    - "Defense-in-depth env-var vocabulary (Phase 4 D-13): wherever PYTHONPYCACHEPREFIX is mentioned, both `run.ps1` AND `teresa_gui.py` are co-named alongside `PYTEST_ADDOPTS`. Single-source language was the v1.0 DOC-03 regression vector."
key-files:
  created: []
  modified:
    - run.ps1 (50 insertions, 0 deletions)
    - spec_classifier/docs/dev/ONE_BUTTON_RUN.md (54 → 50 lines)
    - spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md (281 → 264 lines)
    - .planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md (44 sweep rows appended; tally still placeholder for Plan 06)
decisions:
  - "Help block placed BELOW the existing RU header (immediately above `param(`) per Specifics 'reads more naturally'; satisfies D-04+D-06."
  - "PYTHONPYCACHEPREFIX claim in RUN_PATHS_AND_IO_LAYOUT.md PATCHED rather than removed: it is load-bearing (explains why caches don't pollute the repo) AND patched form is stable (env-var name is stable). This is the file v1.0 DOC-03 missed; Phase 4 D-13 vocabulary now cited verbatim."
  - "Trimmed sections in ONE_BUTTON_RUN.md were the two redundant pipeline-step bullets (`Find the repo root`, `Saves logs to OUTPUT`) and a now-merged 'Setting up config.local.yaml' subsection; Phase 4 CACHE-04 co-occurrence (`-NoClean` + `clean.ps1`) preserved as gate."
  - "Trimmed sections in RUN_PATHS_AND_IO_LAYOUT.md: the 'Run tests' pytest example block (covered by ONE_BUTTON_RUN.md), the 'Common mistakes' `python -m pytest` directly bullet (now covered by clean.ps1 default-on + new pointer), and the 'Checklist: nothing is written to the repo' section (Phase 4 CACHE-04 made it trivially-passing post-clean.ps1 default-on)."
  - "All 44 sweep rows recorded resolution=no_drift except 1 PATCH (PYTHONPYCACHEPREFIX defense-in-depth). No removes — both files were already aligned with current code modulo the documented patch."
metrics:
  duration_min: 6
  completed_date: "2026-05-11"
  commits: 3
  files_modified: 4
  files_created: 0
  tasks_completed: 3
  pre_phase_lines:
    ONE_BUTTON_RUN_md: 54
    RUN_PATHS_AND_IO_LAYOUT_md: 281
    run_ps1: 192
  post_phase_lines:
    ONE_BUTTON_RUN_md: 50
    RUN_PATHS_AND_IO_LAYOUT_md: 264
    run_ps1: 242
  sweep_rows_added:
    ONE_BUTTON_RUN_md: 16
    RUN_PATHS_AND_IO_LAYOUT_md: 28
  sweep_resolutions:
    no_drift: 43
    patch: 1
    remove: 0
---

# Phase 6 Plan 04: DRIFT-02 Trim + Help Block + Sweep Summary

DRIFT-02 closed end-to-end: `run.ps1` now ships a canonical PowerShell comment-based help block (5 `.PARAMETER`s mirroring the `param()` declarations, 6 `.EXAMPLE`s mirroring the existing RU header), making the ROADMAP DRIFT-02 phrase "pointer to `run.ps1 -?`" literally true; both named CLI-prose docs (`ONE_BUTTON_RUN.md` 54→50, `RUN_PATHS_AND_IO_LAYOUT.md` 281→264) are trimmed with that pointer added, and 44 swept claims (16 + 28) are recorded in `06-DRIFT-AUDIT.md` (1 patch — PYTHONPYCACHEPREFIX defense-in-depth — and 43 no_drift).

## Commits

| Task | Commit | Type | Subject | Files | +/- |
|------|--------|------|---------|-------|-----|
| T1 | `84072f3` | chore(06) | T1 add comment-based help block to run.ps1 (DRIFT-02) | `run.ps1` | +50 / 0 |
| T2 | `e19c1ad` | docs(06) | T2 trim ONE_BUTTON_RUN.md and sweep (DRIFT-01, DRIFT-02) | `ONE_BUTTON_RUN.md`, `06-DRIFT-AUDIT.md` | +25 / -13 |
| T3 | `d45f3fb` | docs(06) | T3 trim RUN_PATHS_AND_IO_LAYOUT.md and sweep (DRIFT-01, DRIFT-02) | `RUN_PATHS_AND_IO_LAYOUT.md`, `06-DRIFT-AUDIT.md` | +32 / -21 |

## Acceptance Criteria — All Pass

| Criterion | Result |
|-----------|--------|
| `grep -q '\.SYNOPSIS' run.ps1` | OK (DOC_INVARIANTS #8 unblocked) |
| `grep -c '\.EXAMPLE' run.ps1` = 6 | 6 |
| `grep -c '\.PARAMETER' run.ps1` = 5 | 5 |
| 5 PARAMETER names present (Vendor, NoAi, TestsOnly, SkipTests, NoClean) | All present |
| 5 `param()` switch declarations intact | All present |
| RU-header SHA-256 frozen at `2c7dd607da4a860554b22409748fe3df6c8becdadd9c240bf8f6d66409c99c70` | Match |
| Zero deletion lines in `git diff run.ps1` (B-3 insertion-only gate) | 0 |
| RU header literal `Заменяет: run_audit.ps1, scripts/run_full.ps1, scripts/run_tests.ps1` preserved | OK |
| `wc -l ONE_BUTTON_RUN.md` < 54 | 50 |
| `wc -l RUN_PATHS_AND_IO_LAYOUT.md` < 281 | 264 |
| `run.ps1 -?` pointer in ONE_BUTTON_RUN.md | OK (line 37) |
| `run.ps1 -?` pointer in RUN_PATHS_AND_IO_LAYOUT.md | OK (line 3) |
| ONE_BUTTON_RUN cross-link in RUN_PATHS_AND_IO_LAYOUT.md | OK (line 3) |
| ONE_BUTTON_RUN.md preserves `clean.ps1` + `-NoClean` co-occurrence (Phase 4 CACHE-04) | OK |
| PYTHONPYCACHEPREFIX defense-in-depth wording in RUN_PATHS_AND_IO_LAYOUT.md (run.ps1 + teresa_gui co-mention) | OK |
| Audit log has rows for both files (≥1 each) | 16 + 28 = 44 new rows |
| `git diff --stat` over D-22 protected paths empty | Empty |
| `git diff --stat -- spec_classifier/golden/` empty | Empty |
| Phase 5 ORPH grep gate (no `run_full` in `*.toml`/`*.example`) | OK |
| No `run_full` reference in either trimmed doc | OK |

## Trim Detail

### ONE_BUTTON_RUN.md (54 → 50 lines, -4)

Removed:
- Two redundant numbered bullets in §"What run.ps1 does" (`2. Finds the repo root`, `6. Saves logs to the OUTPUT directory`) — implementation details that don't help a one-button reader.
- Standalone §"Setting up config.local.yaml" — merged into §"Configuration" as a single inline imperative.

Kept (load-bearing per D-09):
- `clean.ps1` + `-NoClean` co-occurrence (Phase 4 CACHE-04 verification gate).
- All 6 switches in §"Useful run.ps1 switches".
- Quick-start one-liner.

Added:
- Pointer line above the switches block: `These switches are also documented in run.ps1's comment-based help (run .\run.ps1 -?).`

### RUN_PATHS_AND_IO_LAYOUT.md (281 → 264 lines, -17)

Removed:
- §"Run tests" pytest example block (lines 199-204 of pre-trim) — duplicated `ONE_BUTTON_RUN.md`.
- §"Common mistakes" bullet `Do not run python -m pytest directly without run.ps1` (lines 213-214 pre-trim) — superseded by the new top pointer + the cleanup paragraph.
- §"Checklist: nothing is written to the repo" (lines 217-223 pre-trim) — Phase 4 CACHE-04 made `run.ps1` invoke `clean.ps1` automatically; the manual checklist became trivially-passing-on-default-run.

Kept (load-bearing tables per D-09):
- §"Data Isolation Policy" 4-row table.
- §"Default folders" 3-row table.
- §"Recommended INPUT folder structure" tree + the 6-line `python main.py --batch-dir` invocation block.
- §"Configuration path priority" 3-tier list.
- §"Exact output tree" Dell/Cisco/HPE/Batch sections.
- §"Audit & Cluster Output Paths" tables.

Added:
- Top pointer paragraph (line 3): `For run.ps1 switches, see run.ps1 -? or [docs/dev/ONE_BUTTON_RUN.md](../dev/ONE_BUTTON_RUN.md). For path discovery internals, see below.`
- §"How this is enforced" item 3 rewritten to Phase 4 D-13 vocabulary: `PYTHONPYCACHEPREFIX and PYTEST_ADDOPTS env vars are exported by both run.ps1 and teresa_gui.py from config.local.yaml::temp_root (Phase 4 defense-in-depth)`.
- §"How this is enforced" item 5 augmented: `clean.ps1 ... (also invoked by run.ps1 at the start of every run unless -NoClean)`.

## Sweep Detail (DRIFT-01 portion)

44 claim rows appended to `06-DRIFT-AUDIT.md` covering the post-trim state of both files.

### ONE_BUTTON_RUN.md (16 rows, all `no_drift`)

Categories (per D-11):
- 6 switch/CLI-flag claims (each verified via `grep` against `run.ps1` post-T1).
- 7 path/file existence + behavior claims (vendor list, batch_audit/cluster_audit invocation, config-overlay layering, clean.ps1 default-on).
- 1 cross-link (the new `run.ps1 -?` pointer — verified via `grep -q '.SYNOPSIS' run.ps1` post-T1).
- 2 generic structural claims (Quick start, Workspace cleanup co-occurrence).

### RUN_PATHS_AND_IO_LAYOUT.md (28 rows, 27 `no_drift` + 1 `patch`)

Categories (per D-11):
- 1 patch — line 22 PYTHONPYCACHEPREFIX defense-in-depth (Phase 4 D-13 vocabulary). The PATCH disposition is the load-bearing decision: this is the file the v1.0 DOC-03 sweep missed because the prior wording was single-source ("`run.ps1` sets PYTHONPYCACHEPREFIX"), which silently went stale when teresa_gui.py picked up the same wiring in Phase 4. The patched wording cites BOTH entry points + BOTH env vars + the temp_root source.
- 11 path/file existence claims (CODE/INPUT/OUTPUT/TEMPORARY layout, gitignore, config.local.yaml, pyproject.toml, clean.ps1).
- 12 CLI shape claims (`python main.py --input/--batch-dir/--vendor`, `batch_audit.py --output-dir/--no-ai/--vendor`, `cluster_audit.py --output-dir/--dry-run`).
- 4 output-tree claims (Dell/Cisco/HPE/TOTAL artifact layouts, all matching `spec_classifier/CLAUDE.md` § OUTPUT layout).
- 2 cross-link claims (CLI_CONFIG_REFERENCE.md + DOCS_INDEX.md "See also").

Sweep ordering note: per D-14, this plan operates in Group 4 (`docs/user/`) and Group 3 (`docs/dev/`). Files were swept post-trim (T1 help block landed before T2/T3 sweeps so the `run.ps1 -?` cross-link is verifiable; T2 ONE_BUTTON_RUN landed before T3 RUN_PATHS so the `[docs/dev/ONE_BUTTON_RUN.md]` link target was sweepable).

## Decisions Made

1. **Help block placement (D-04+D-06 discretion):** Placed BELOW the existing RU header (`run.ps1:1-13`), immediately above `param(`. Satisfies both decisions and reads more naturally per Specifics. SHA-256 of `head -n 13 run.ps1` = `2c7dd607...c99c70` — byte-identical to phase start.

2. **PYTHONPYCACHEPREFIX wording: PATCH not REMOVE.** D-13 says `default removal`; this is the documented exception (BOTH conditions: load-bearing for the reader's mental model AND patched form is stable). The patched wording is now the single canonical phrasing across `.planning/codebase/STACK.md` (Phase 6 Plan 06 will cover), `INTEGRATIONS.md` (same), and this user-facing doc.

3. **Trim depth in ONE_BUTTON_RUN.md (D-09 discretion):** Aimed for the minimum strict decrease (-4) while preserving the Phase 4 CACHE-04 co-occurrence gate. Could have been more aggressive but the file is already terse; further trimming would degrade reader comprehension without measurable gain.

4. **Trim depth in RUN_PATHS_AND_IO_LAYOUT.md (D-09 discretion):** Aimed for ~5% line reduction (-17). Tables (load-bearing per D-09) all preserved; only prose duplication with `ONE_BUTTON_RUN.md` and the now-trivially-passing checklist were dropped.

5. **Sweep verification mode (D-10 — hybrid manual + scripted-subset):** Each row's check_command is a Bash one-liner that an executor could re-run; this mirrors the DOC_INVARIANTS.md pattern Plan 06 will materialize. No row was marked `no_drift` without an explicit verification path.

## Deviations from Plan

None. Plan executed exactly as written. T1 → T2 → T3 ordering honored (T1 help block landed before the sweep rows verified `grep -q '.SYNOPSIS' run.ps1`; T2 ONE_BUTTON_RUN trim landed before T3 RUN_PATHS rewrite that cross-links to it).

The plan's grep escaping for the `for p in Vendor NoAi ... done` shell loop check has a known cosmetic glitch in nested-quote contexts (the `\\\$` escape doesn't survive PowerShell-relayed bash invocations cleanly), but the underlying file content is correct and verifiable via direct `grep -E '^\s*\[(string|switch)\]\$' run.ps1` (returns the 5 expected lines).

## Threat Flags

None. The help block is documentation already published in `ONE_BUTTON_RUN.md` / `CLI_CONFIG_REFERENCE.md` (T-06-11 accept). The trims removed prose duplications, not security-relevant content. No new network endpoints, auth paths, file access patterns, or schema changes introduced.

## Self-Check: PASSED

Verifications performed (all return-zero or matching values):

- `[ -f run.ps1 ]` → FOUND
- `[ -f spec_classifier/docs/dev/ONE_BUTTON_RUN.md ]` → FOUND
- `[ -f spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md ]` → FOUND
- `[ -f .planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md ]` → FOUND
- `git log --oneline | grep -q 84072f3` → FOUND (T1 commit)
- `git log --oneline | grep -q e19c1ad` → FOUND (T2 commit)
- `git log --oneline | grep -q d45f3fb` → FOUND (T3 commit)
- `head -n 13 run.ps1 | sha256sum` → matches frozen `2c7dd607...c99c70`
- `wc -l ONE_BUTTON_RUN.md` → 50 (< 54)
- `wc -l RUN_PATHS_AND_IO_LAYOUT.md` → 264 (< 281)
- `git diff --stat` over D-22 protected paths → empty
- `git diff --stat -- spec_classifier/golden/` → empty
