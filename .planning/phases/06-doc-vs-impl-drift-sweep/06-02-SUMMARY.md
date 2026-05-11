---
phase: 06-doc-vs-impl-drift-sweep
plan: 02
subsystem: docs
tags: [doc-sweep, drift, dev-docs, DRIFT-01]

# Dependency graph
requires:
  - phase: 04-cache-redirect
    provides: PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS canonical wiring vocabulary (D-08, D-13) used to validate cache-redirect claims (none surfaced in OPERATIONAL_NOTES.md or TESTING_GUIDE.md, so defense-in-depth check N/A here)
  - phase: 05-orphan-cleanup
    provides: post-orphan-cleanup tree (no scripts/run_full.ps1 references) used to validate ORPH invariant
  - phase: 06-doc-vs-impl-drift-sweep
    plan: 01
    provides: 06-DRIFT-AUDIT.md skeleton + audit-row column shape + no_drift-row convention (reused verbatim per Plan 01 Next-Phase Readiness)
provides:
  - 74 per-claim rows appended to 06-DRIFT-AUDIT.md for the 3 dev-docs files (Group 3 sweep order per D-14)
  - NEW_VENDOR_GUIDE.md, OPERATIONAL_NOTES.md, TESTING_GUIDE.md mechanically verified against post-Phase-4-and-5 tree
affects: [06-03, 06-04, 06-05, 06-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Append-only audit-log convention (Plans 02-05 inherit Plan 01 schema; do not rewrite)"
    - "D-12 volatile-count REMOVE-not-patch applied: dropped bare \"6\" vendor count + \"(26 and 82 rows)\" + \"25+ parametrized\" cases"
    - "D-13 remove > patch applied: line-number ref `teresa_gui.py:38` collapsed to symbol-only ref"

key-files:
  created:
    - .planning/phases/06-doc-vs-impl-drift-sweep/06-02-SUMMARY.md
  modified:
    - spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md
    - spec_classifier/docs/dev/OPERATIONAL_NOTES.md
    - spec_classifier/docs/dev/TESTING_GUIDE.md
    - .planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md

key-decisions:
  - "All 3 dev-docs files were already drift-low post-Phase-4-and-5: 1 patch + 3 removes + 67 no_drift across 71 unique claims swept"
  - "--update-golden flag in TESTING_GUIDE.md retained (real code reality at main.py:267 per Plan 02 N-3 clarification); v1.1 milestone-level no-update-golden constraint is a phase-gate, not a code property"
  - "OPERATIONAL_NOTES.md does not currently claim PYTHONPYCACHEPREFIX wiring at all, so Phase 4 D-13 defense-in-depth regression check was N/A (no single-source language to patch)"

patterns-established:
  - "Sweep mechanism unchanged from Plan 01 (D-10): for each claim, run mechanical check, default to remove on drift, patch only when load-bearing AND patched form stable, append no_drift rows to keep audit complete"
  - "Volatile-count removal preserves named enumeration: e.g., line 113 OPERATIONAL_NOTES.md kept the dell/cisco/hpe/lenovo/huawei/xfusion list and dropped only the bare \"6\" prefix"

requirements-completed: [DRIFT-01]

# Metrics
duration: ~5min
completed: 2026-05-11
---

# Phase 6 Plan 02: Dev Docs Drift Sweep Summary

**3 dev-docs files (NEW_VENDOR_GUIDE.md, OPERATIONAL_NOTES.md, TESTING_GUIDE.md) mechanically swept; 71 unique claims verified, 4 drifted (1 line-number ref + 3 volatile-count snippets) resolved via patch/remove, audit ledger appended.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-05-11T00:15:31Z
- **Completed:** 2026-05-11T00:20:40Z
- **Tasks:** 3 / 3
- **Files modified:** 3 sweep targets + 1 audit log; 0 D-22-protected files; 0 goldens

## Accomplishments

- **Task 1 — NEW_VENDOR_GUIDE.md** swept end-to-end. 28 claims verified across the adapter contract, file-create/modify checklist, golden workflow, and pre-PR checklist. The 6 abstract-method count claim cross-checked against `src/vendors/base.py` (`grep -c '@abstractmethod'` returns 6). Per-vendor `get_extra_cols()` cardinalities (HPE 5, Lenovo 1, Cisco 2) all confirmed by reading each vendor adapter. `$ALL_VENDORS` (run.ps1:71), `VENDORS_ACTIVE` (teresa_gui.py:38), and `--save-golden` (main.py:266) all real. **One drift fixed:** dropped `:38` line-number ref from `teresa_gui.py:38` reference on doc line 78 per D-13 (symbol-only form retained).
- **Task 2 — OPERATIONAL_NOTES.md** swept. 17 claims verified across single-file/batch run sections, TOTAL-folder semantics, artifact storage policy, new-dataset workflow per vendor, and `run.ps1` invocation matrix. `batch_audit.py` TOTAL exclusion confirmed at lines 1344-1345 (`if "-TOTAL" not in f.parent.name`). **One drift fixed:** removed bare `"6"` vendor count on doc line 113 per D-12 (kept the named list `dell, cisco, hpe, lenovo, huawei, xfusion` which is stable per D-12).
- **Task 3 — TESTING_GUIDE.md** swept. 26 claims verified across testing-strategy enumeration, quick-start CLI, golden workflow, CI-gate command, session-gate (`MAX_SKIP_RATIO = 0.50` at conftest.py:14, `pytest_sessionfinish` at line 141), unknown-threshold gate, and per-vendor new-dataset workflow. All 31 referenced test files confirmed present in `spec_classifier/tests/`. **Two drifts fixed:** removed volatile counts `(26 and 82 rows)` (line 9) and `25+ parametrized` (line 12) per D-12. `--update-golden` claim **retained** per Plan 02 action item #3 N-3 clarification (real code reality at main.py:267).

## Task Commits

Each task was committed atomically per D-21 (`docs(06): T<N> <description>`):

1. **Task 1: Sweep NEW_VENDOR_GUIDE.md** — `224afb7` (docs)
2. **Task 2: Sweep OPERATIONAL_NOTES.md** — `3e289bc` (docs)
3. **Task 3: Sweep TESTING_GUIDE.md** — `ac021a6` (docs)

**Plan metadata commit:** to follow this SUMMARY (records SUMMARY.md, STATE.md, ROADMAP.md updates).

## Files Created/Modified

- `.planning/phases/06-doc-vs-impl-drift-sweep/06-02-SUMMARY.md` — Created (this file).
- `.planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` — Modified. 74 new rows appended (28 NEW_VENDOR_GUIDE + 19 OPERATIONAL_NOTES + 27 TESTING_GUIDE; 1 patch + 3 remove + 70 no_drift). Plan 01 schema reused verbatim.
- `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` — Modified (1 line-number ref dropped on line 78).
- `spec_classifier/docs/dev/OPERATIONAL_NOTES.md` — Modified (1 volatile count removed on line 113).
- `spec_classifier/docs/dev/TESTING_GUIDE.md` — Modified (2 volatile-count snippets removed on lines 9 and 12).

## Decisions Made

- **Default-remove discipline applied to volatile counts.** Per D-12, all bare counts (vendor count "6", row counts "26 and 82", parametrize-case count "25+") were removed rather than patched. The named list `dell/cisco/hpe/lenovo/huawei/xfusion` was retained on OPERATIONAL_NOTES.md line 113 since per D-12 the named enumeration itself is stable (only the bare numeric prefix is volatile).
- **`--update-golden` claim retained, not removed.** Per Plan 02 action item #3 + N-3 clarification, the flag is real code reality (`main.py:267`); the v1.1 phase-gate constraint "no `--update-golden` runs sanctioned in v1.1" is a milestone constraint, not a code property. Removing the doc claim would degrade contributor knowledge of the actual code surface.
- **Defense-in-depth check N/A for OPERATIONAL_NOTES.md.** Phase 4 D-13 defense-in-depth (BOTH `run.ps1` AND `teresa_gui.py` set PYTHONPYCACHEPREFIX/PYTEST_ADDOPTS) regression check was checked but did not fire: OPERATIONAL_NOTES.md does not currently mention these env vars at all, so there's no single-source language to patch.
- **Line-number `teresa_gui.py:38` collapsed to symbol-only ref.** Per D-13 patched-form stability rule, dropped the `:38` suffix on NEW_VENDOR_GUIDE.md line 78. The surrounding prose names `VENDORS_ACTIVE` and `_build_left_column` as the symbols a contributor needs to find — line numbers add no durable knowledge.

## Deviations from Plan

None — plan executed exactly as written. All 3 tasks completed in declared order; each task's `<acceptance_criteria>` block satisfied; D-22 protected paths byte-equal; goldens byte-equal; `ONE_BUTTON_RUN.md` not touched (Plan 04 trim target); no out-of-scope file modified.

## Issues Encountered

None. The sweep was uneventful — every `Test-Path` succeeded, every CLI-switch `grep` matched, and the only drifts encountered (1 line-number ref + 3 volatile counts) were exactly the categories D-11/D-12/D-13 anticipated.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 03 (DRIFT-01 Group 4 — `spec_classifier/docs/user/`)** is unblocked. Ready to sweep `CLI_CONFIG_REFERENCE.md`, `RUN_PATHS_AND_IO_LAYOUT.md`, `USER_GUIDE.md` per D-14 sweep order. (`RUN_PATHS_AND_IO_LAYOUT.md` is also a DRIFT-02 trim target; coordinate with Plan 04.)
- Audit-row column shape and no_drift-row convention from Plan 01 reused verbatim in Plan 02; Plans 03-05 inherit the same.
- Tally counters maintained: 182 claims swept across 7 of 19 in-scope files (4 from Plan 01 + 3 from Plan 02). 1 patch + 3 remove + 178 no_drift cumulatively. Plan 06 will fill the final Tally section.
- D-22 protection holds: zero diff inside `spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` over the plan window.
- Goldens byte-equal: `git diff --stat -- spec_classifier/golden/` empty over the plan window.
- Phase 5 ORPH-01/02 invariant holds: no `scripts/run_full.ps1` references in any in-scope `*.toml` / `*.example` file.

## Self-Check: PASSED

- `test -f .planning/phases/06-doc-vs-impl-drift-sweep/06-02-SUMMARY.md` — FOUND
- Commits `224afb7`, `3e289bc`, `ac021a6` all present in `git log`
- D-22 protected paths byte-equal: PASS (`git diff --stat -- spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` empty)
- Goldens byte-equal: PASS (`git diff --stat -- spec_classifier/golden/` empty)
- `ONE_BUTTON_RUN.md` unchanged: PASS (Plan 04 trim target)
- Out-of-scope files (`spec_classifier/CLAUDE.md`, `spec_classifier/README.md`, `spec_classifier/CHANGELOG.md`, `LAUNCHER_README.md`) unchanged: PASS
- Phase 5 ORPH grep gate: PASS (zero matches via `! grep -rqI "run_full" --include='*.toml' --include='*.example' --exclude-dir=.planning --exclude=CHANGELOG.md --exclude=LAUNCHER_README.md .`)
- Audit-row count per swept file: NEW_VENDOR_GUIDE.md ≥ 1 (28 rows), OPERATIONAL_NOTES.md ≥ 1 (19 rows), TESTING_GUIDE.md ≥ 1 (27 rows)
- `grep -q "run_full"` exits non-zero in all 3 swept files: PASS

---
*Phase: 06-doc-vs-impl-drift-sweep*
*Completed: 2026-05-11*
