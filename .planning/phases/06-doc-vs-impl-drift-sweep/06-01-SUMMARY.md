---
phase: 06-doc-vs-impl-drift-sweep
plan: 01
subsystem: docs
tags: [doc-sweep, drift, root-docs, audit-log, DRIFT-01]

# Dependency graph
requires:
  - phase: 04-cache-redirect
    provides: PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS canonical wiring vocabulary (D-08, D-13) used to validate cache-redirect claims in swept files
  - phase: 05-orphan-cleanup
    provides: post-orphan-cleanup tree (no scripts/run_full.ps1 references in *.toml/*.example) used to validate ORPH invariant in swept files
provides:
  - 06-DRIFT-AUDIT.md skeleton + 108 per-claim rows for the 4 root/index files (Plans 02-05 will append more rows; Plan 06 fills the Tally section)
  - README.md, CLAUDE.md, CONTRIBUTING.md, spec_classifier/docs/DOCS_INDEX.md mechanically verified against post-Phase-4-and-5 tree (zero drift found)
affects: [06-02, 06-03, 06-04, 06-05, 06-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-claim audit ledger as 5th per-phase artifact (sibling to PLAN/CONTEXT/VERIFICATION/SUMMARY)"
    - "no_drift rows recorded for full-inventory audit (per Specifics + ROADMAP §SC-5 'every claim flagged')"

key-files:
  created:
    - .planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md
    - .planning/phases/06-doc-vs-impl-drift-sweep/06-01-SUMMARY.md
  modified: []

key-decisions:
  - "All 4 swept files were already drift-free post-Phase-4-and-5; no remove or patch resolutions needed in Plan 01"
  - "108 no_drift rows recorded as full-inventory baseline (31 README + 25 CLAUDE + 27 CONTRIBUTING + 25 DOCS_INDEX); Plans 02-05 inherit the same column shape"
  - "Audit-row check_command column favors symbol/section refs over file:line refs (D-13 patched-form stability rule, applied even to no_drift rows)"

patterns-established:
  - "Sweep mechanism (D-10): for each claim, run mechanical check (Test-Path / grep / runtime), default to remove on drift, patch only when load-bearing AND patched form stable, append no_drift rows to keep audit complete"
  - "Audit-row column shape: `| <file> | <line_or_range> | \"<short claim quote>\" | \`<exact check command>\` | <remove|patch|no_drift> |`"
  - "Per-task atomic commits with `docs(06): T<N> <description>` subject (D-21)"

requirements-completed: [DRIFT-01]

# Metrics
duration: ~25min
completed: 2026-05-11
---

# Phase 6 Plan 01: Root Documentation Sweep Summary

**4 root/index docs (README.md, CLAUDE.md, CONTRIBUTING.md, DOCS_INDEX.md) mechanically swept against the post-Phase-4-and-5 tree; 108 claims verified, zero drift found, audit ledger initialized.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-05-11
- **Completed:** 2026-05-11
- **Tasks:** 4 / 4
- **Files modified:** 0 sweep targets (all byte-equal); 1 new artifact (06-DRIFT-AUDIT.md)

## Accomplishments

- `06-DRIFT-AUDIT.md` initialized at `.planning/phases/06-doc-vs-impl-drift-sweep/` with the canonical D-22 schema (`| file | line | claim_summary | check_command | resolution |`), Purpose section, sweep-order reference, claim-category reference, and Tally placeholder for Plan 06 to fill.
- `README.md` swept end-to-end: 31 `code does X` claims (path/file existence, switch/CLI flags, behavior summaries) verified — every `Test-Path` resolves, every CLI switch (`-NoAi`, `-Vendor`, `-TestsOnly`, `-SkipTests`) present in `run.ps1`, six vendors confirmed in `$ALL_VENDORS` (line 71), no `scripts/run_full.ps1` orphan ref. Zero patches needed.
- `CLAUDE.md` (root) swept: 25 claims verified — load-bearing business-rules text (power_cord, LOGISTIC, BASE/HW/CONFIG semantics) cross-checked against `batch_audit.py:_E8_NO_HW_TYPE_DEVICES` (line 506) and `dell_rules.yaml` "intentionally unmapped" comment (line 278). All "Where to look first" table entries resolve. Zero patches.
- `CONTRIBUTING.md` swept: 27 claims verified — GSD cycle commands, pytest skip-ratio gate (`MAX_SKIP_RATIO = 0.50` at `conftest.py:14`), `--update-golden` (`main.py:267`), `VENDORS_ACTIVE`/`VENDORS_DISABLED` (`teresa_gui.py:38-39`), 5-item "Do not fix" list. Historical commit examples preserved per D-18. Zero patches.
- `spec_classifier/docs/DOCS_INDEX.md` swept: 25 entries verified 1:1 against actual filesystem (10 `docs/<area>/*.md` + 4 sibling `.md`/`.py` + root `README.md` + `CONTRIBUTING.md`); `DOC_INVARIANTS.md` correctly NOT yet listed (Plan 06 will add it). Zero patches.

## Task Commits

Each task was committed atomically per D-21 (`docs(06): T<N> <description>`):

1. **Task 1: Initialize 06-DRIFT-AUDIT.md skeleton** — `a3db170` (docs)
2. **Task 2: Sweep root README.md** — `77e2693` (docs)
3. **Task 3: Sweep CLAUDE.md and CONTRIBUTING.md** — `e149634` (docs)
4. **Task 4: Sweep spec_classifier/docs/DOCS_INDEX.md** — `3624abb` (docs)

**Plan metadata commit:** to follow this SUMMARY (records SUMMARY.md, STATE.md, ROADMAP.md updates).

## Files Created/Modified

- `.planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` — Created. Skeleton + 108 audit rows (31 README + 25 CLAUDE + 27 CONTRIBUTING + 25 DOCS_INDEX, all `no_drift`).
- `.planning/phases/06-doc-vs-impl-drift-sweep/06-01-SUMMARY.md` — Created (this file).
- `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `spec_classifier/docs/DOCS_INDEX.md` — **Unchanged** (zero drift found; sweep target byte-equal over the plan window).

## Decisions Made

- **All 4 files drift-free.** The post-Phase-4-and-5 tree honors every "code does X" claim in the 4 swept files. Phase 4 (cache-redirect wiring) and Phase 5 (orphan cleanup) closed cleanly enough that the root docs did not need any remove/patch work.
- **Full-inventory audit recorded.** Per Specifics + ROADMAP §SC-5 ("every file checked, every claim flagged"), every claim considered was logged as a `no_drift` row, not just claims that needed change. This gives Plans 02-06 a complete baseline and supports the SC #5 "every claim flagged" wording.
- **Audit-row check_command column favors symbol/section refs over `file.py:N` refs** even for `no_drift` rows, matching D-13's patched-form stability rule. The few line-number references retained in the check_command column (e.g., `run.ps1:71`, `batch_audit.py:506`) are stable structural anchors expected to persist across cosmetic edits, and they appear in the audit-log column (not in committed source docs).

## Deviations from Plan

None — plan executed exactly as written. All 4 tasks completed in declared order; each task's `<acceptance_criteria>` block satisfied; D-22 protected paths byte-equal; goldens byte-equal; no out-of-scope file modified.

## Issues Encountered

None. The sweep was uneventful — every `Test-Path` succeeded, every CLI-switch `grep` matched, every business-rule citation cross-referenced cleanly to its source-of-truth file.

One minor execution note: a single `Edit` call had a typo (trailing `>`) on first attempt and was retried successfully. Not a deviation; not material to plan outcomes.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 02 (DRIFT-01 Group 3 — `spec_classifier/docs/dev/`)** is unblocked. Ready to sweep `NEW_VENDOR_GUIDE.md`, `ONE_BUTTON_RUN.md`, `OPERATIONAL_NOTES.md`, `TESTING_GUIDE.md` per D-14 sweep order.
- The audit-row column shape and `no_drift`-row convention established in Plan 01 should be reused verbatim by Plans 02-05.
- Tally counters for Plan 06 to maintain: 108 claims swept so far (0 remove / 0 patch / 108 no_drift) across 4 of 19 in-scope files.
- D-22 protection holds: zero diff inside `spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` over the plan window.
- Phase 5 ORPH-01/02 invariant holds: no `scripts/run_full.ps1` references in any in-scope `*.toml` / `*.example` file.

## Self-Check: PASSED

- `test -f .planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` — FOUND
- `test -f .planning/phases/06-doc-vs-impl-drift-sweep/06-01-SUMMARY.md` — FOUND
- Commits `a3db170`, `77e2693`, `e149634`, `3624abb` all present in `git log`
- D-22 protected paths byte-equal: PASS
- Goldens byte-equal: PASS
- Out-of-scope files (`spec_classifier/CLAUDE.md`, `spec_classifier/README.md`, `spec_classifier/CHANGELOG.md`, `LAUNCHER_README.md`) unchanged: PASS
- Phase 5 ORPH grep gate: PASS (zero matches)

---
*Phase: 06-doc-vs-impl-drift-sweep*
*Completed: 2026-05-11*
