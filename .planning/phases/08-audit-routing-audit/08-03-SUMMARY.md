---
phase: 08-audit-routing-audit
plan: 03
subsystem: testing
tags: [routing, batch_audit, cluster_audit, SPLIT, AUDIT, pytest, skip-gate]

# Dependency graph
requires:
  - phase: 08-01
    provides: "batch_audit reads SPLIT/, writes audited workbooks + audit_report.json to AUDIT/; dead {vendor}_run/hp_run matchers removed"
  - phase: 08-02
    provides: "cluster_audit dual-bucket read (AUDIT+SPLIT); cluster_summary.xlsx + audit_report.json cluster-merge target AUDIT/ root"
provides:
  - "test_batch_audit.py vendor-detection-from-path tests assert the new SPLIT/<vendor>/<spec>/ layout (no dead {vendor}_run/hp_run)"
  - "test_batch_audit.py aggregate tests read audit_report.json from AUDIT/ root"
  - "test_cluster_audit.py discovery + load_candidate_rows fixtures relocated to AUDIT/ and SPLIT/ buckets; aggregate reads from AUDIT/ root"
  - "Green acceptance gate for Phase 8 ROUTE-03 + ROUTE-04 (SC#4 / TEST-01): full pytest suite passes within skip-gate, goldens byte-equal"
affects: [phase-08-verify, milestone-v1.2-complete]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Test fixtures mirror production bucket layout: audited workbooks under tmp_path/AUDIT/<vendor>/<spec>/, annotated under tmp_path/SPLIT/<vendor>/<spec>/"
    - "Vendor detection in fixtures via /<vendor>/ path segment (matches detect_vendor_from_path /{vendor}/ matcher)"

key-files:
  created: []
  modified:
    - spec_classifier/tests/test_batch_audit.py
    - spec_classifier/tests/test_cluster_audit.py

key-decisions:
  - "load_candidate_rows fixture tests (not enumerated in plan interfaces) relocated to AUDIT/SPLIT buckets — same path/layout class as the planned discovery tests; in-scope under SC#4 fix-tests-not-goldens"
  - "cluster_audit._detect_vendor_from_path parametrized tests left byte-unchanged (function not modified by Phase 8 D-07); verified still passing"

patterns-established:
  - "Pattern: Discovery/aggregate tests place fixtures in the same SPLIT/AUDIT bucket subtree that production routing now reads/writes"

requirements-completed: [ROUTE-03, ROUTE-04]

# Metrics
duration: ~8min
completed: 2026-06-07
---

# Phase 8 Plan 03: Audit-routing test realignment Summary

**Realigned batch_audit + cluster_audit path/layout tests to the Phase-7/8 `<bucket>/<vendor>/<spec>/` structure (SPLIT for annotated, AUDIT for audited + aggregates); full pytest suite green (774 passed, 1 xfailed, 0 skipped) within the skip-gate with goldens byte-equal and no `--update-golden`.**

## Performance

- **Duration:** ~8 min
- **Completed:** 2026-06-07
- **Tasks:** 3 (2 edit tasks + 1 verification gate)
- **Files modified:** 2

## Accomplishments
- `TestDetectVendorFromPath` cases assert the new `SPLIT/<vendor>/<spec>/` layout; the removed `hp_run -> hpe` alias case now asserts `unknown` (alias not re-added)
- `TestRealBugClassification` reads `audit_report.json` from the `AUDIT/` root (matching 08-01's `_generate_report` destination)
- `_collect_xlsx_files` discovery tests place audited fixtures under `AUDIT/` and annotated under `SPLIT/` with prefer-audited dedup intact
- `write_cluster_summary` tests read `cluster_summary.xlsx` + seed/read `audit_report.json` from the `AUDIT/` root
- `load_candidate_rows` fixtures relocated from the dead `{vendor}_run/run-*` flat layout to the `AUDIT/`/`SPLIT/` buckets
- Full pytest suite exits 0 within the skip-gate; all `*_expected.jsonl` goldens byte-equal

## Task Commits

Each task was committed atomically:

1. **Task 1: Realign batch_audit path/aggregate tests** - `4c90a4e` (test)
2. **Task 2: Realign cluster_audit discovery + aggregate tests** - `ced0fbc` (test)
3. **Task 3: Full pytest suite green within skip-gate, goldens byte-equal** - verification-only gate; no file edits (satisfied by the green suite from Tasks 1-2; nothing to commit)

**Plan metadata:** see final docs commit.

## Files Created/Modified
- `spec_classifier/tests/test_batch_audit.py` - vendor-detection-from-path tests assert SPLIT layout; alias-removed-unknown case; report reads from AUDIT/ root
- `spec_classifier/tests/test_cluster_audit.py` - discovery + load_candidate_rows fixtures under AUDIT/SPLIT buckets; aggregate reads from AUDIT/ root; _detect_vendor_from_path tests untouched

## Decisions Made
- **load_candidate_rows tests realigned despite not being enumerated in the plan's `<interfaces>`.** These 4 tests (`_audited_E2`, `_annotated_unknown`, `_vendor_filter`, `_hw_no_types`) plus `_filters_ok` placed fixtures under the dead `{vendor}_run/run-*` flat layout. Since `load_candidate_rows` calls `_collect_xlsx_files`, which after 08-02 reads only `AUDIT/`+`SPLIT/`, the flat fixtures were no longer discovered. This is the identical path/layout breakage class the plan addresses for the discovery tests — legitimately in-scope under SC#4 (fix tests, not goldens). Vendor detection preserved by placing fixtures under `.../<vendor>/...`.
- **`cluster_audit._detect_vendor_from_path` parametrized tests left byte-unchanged.** That function was not modified by Phase 8 (D-07 touches only batch_audit). The `_run`-path cases still pass against the unmodified function — verified, not edited (per plan constraint).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Realigned 5 load_candidate_rows fixture tests to AUDIT/SPLIT buckets**
- **Found during:** Task 2 (cluster_audit test realignment)
- **Issue:** 4 of these tests failed (`assert 0 == 1`) and 1 passed only incidentally because their fixtures used the dead `{vendor}_run/run-*` flat layout, which `_collect_xlsx_files` (rewired by 08-02 to read only `AUDIT/`+`SPLIT/`) no longer discovers. They blocked the full-suite green gate (Task 3).
- **Fix:** Relocated audited fixtures to `tmp_path/AUDIT/<vendor>/test/` and annotated fixtures to `tmp_path/SPLIT/<vendor>/test/`; vendor detection preserved via the `/<vendor>/` path segment. No assertion intent changed — only fixture placement.
- **Files modified:** spec_classifier/tests/test_cluster_audit.py
- **Verification:** `python -m pytest tests/test_cluster_audit.py -q` -> 43 passed; full suite 774 passed / 0 skipped
- **Committed in:** ced0fbc (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking — same path/layout class as the planned edits, no scope creep beyond fix-tests-not-goldens)
**Impact on plan:** Necessary to reach the green full-suite gate (Task 3). No golden content touched, no production code touched, no assertion semantics weakened.

## Issues Encountered
- The plan's `<interfaces>` enumerated the discovery + write_cluster_summary tests but not the `load_candidate_rows` tests that share the same `_collect_xlsx_files` discovery path. Caught by the Task 2 test run and resolved via fixture relocation (see Deviations).

## Verification

- `python -m pytest tests/test_batch_audit.py -q` -> 72 passed
- `python -m pytest tests/test_cluster_audit.py -q` -> 43 passed
- `python -m pytest -q` (full suite from spec_classifier/) -> **774 passed, 1 xfailed, 0 skipped** in 19.55s; exit 0. Skip ratio 0.00 < 0.50; passed > 0 (skip-gate satisfied, no "Skip guard triggered").
- `git diff --stat -- spec_classifier/golden/` -> **EMPTY** (all `*_expected.jsonl` byte-equal; no `--update-golden` used).
- `git diff --stat -- spec_classifier/batch_audit.py spec_classifier/cluster_audit.py` -> EMPTY (no production code touched this plan; routing edits remain those from 08-01/08-02).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 8 ROUTE-03 + ROUTE-04 acceptance bar (SC#1-4) met: routing rewired (08-01/08-02), tests realigned and green (08-03), goldens byte-equal.
- Ready for `/gsd-verify-work 8` and milestone v1.2 close-out steps.

## Known Stubs
None.

## Self-Check: PASSED

- spec_classifier/tests/test_batch_audit.py - FOUND
- spec_classifier/tests/test_cluster_audit.py - FOUND
- .planning/phases/08-audit-routing-audit/08-03-SUMMARY.md - FOUND
- Commit 4c90a4e - FOUND
- Commit ced0fbc - FOUND

---
*Phase: 08-audit-routing-audit*
*Completed: 2026-06-07*
