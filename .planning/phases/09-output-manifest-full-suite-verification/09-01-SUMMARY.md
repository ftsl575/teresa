---
phase: 09-output-manifest-full-suite-verification
plan: "01"
subsystem: diagnostics
tags: [run_manager, batch_audit, cluster_audit, vendor-detection, deduplication, refactor]

# Dependency graph
requires:
  - phase: 08-audit-routing-audit
    provides: "batch_audit.detect_vendor_from_path (canonical cleaned version, D-07/D-08)"
  - phase: 08-audit-routing-audit
    provides: "cluster_audit._detect_vendor_from_path (stale copy with dead _run/hp_run/ccw branches)"
provides:
  - "run_manager.detect_vendor_from_path: single shared vendor-from-path function, pure path+list->vendor"
  - "batch_audit: local copy deleted; imports from run_manager; re-exports at module level"
  - "cluster_audit: local copy deleted; imports from run_manager; caller now passes known_vendors explicitly"
  - "test_cluster_audit: old _run/ccw_export assertions removed; tests aligned to SPLIT/<vendor>/ contract"
affects:
  - 09-02
  - 09-03

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pure function pattern: detect_vendor_from_path(path, known_vendors) in run_manager.py; no config dependency; callers resolve and pass the list"
    - "Module-level re-export: importing in batch_audit.py makes detect_vendor_from_path available to test_batch_audit.py without changes"

key-files:
  created: []
  modified:
    - spec_classifier/src/diagnostics/run_manager.py
    - spec_classifier/batch_audit.py
    - spec_classifier/cluster_audit.py
    - spec_classifier/tests/test_cluster_audit.py

key-decisions:
  - "D-13 gate: exactly 3 behavioral divergences confirmed (ccw alias, match mechanism, WARN print); no fourth found; merge proceeded"
  - "D-11: known_vendors is required param (no None default) — callers must resolve and pass; run_manager stays config-free"
  - "D-14: old cluster _run/ccw_export test assertions removed; test suite realigned to SPLIT/<vendor>/ layout contract"

patterns-established:
  - "Shared path-helper in run_manager.py: pure function beside create_spec_folder; no config loading inside"
  - "Caller resolves known_vendors from own config, passes explicitly — run_manager has no config dependency"

requirements-completed:
  - TEST-01

# Metrics
duration: 12min
completed: 2026-06-07
---

# Phase 09 Plan 01: WR-01 Vendor-Detector Deduplication Summary

**Single shared detect_vendor_from_path extracted into run_manager.py — both local copies deleted, cluster caller updated to pass known_vendors explicitly, test suite realigned to SPLIT/<vendor>/ layout**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-06-07T18:43:43Z
- **Completed:** 2026-06-07T18:55:00Z
- **Tasks:** 2 (Task 1: analysis gate; Task 2: extraction + test fix)
- **Files modified:** 4

## Accomplishments
- Pre-merge equivalence gate confirmed exactly 3 divergences (ccw alias, match mechanism, WARN print) — no fourth found; merge approved
- Extracted canonical `detect_vendor_from_path(path: Path, known_vendors: list[str]) -> str` into run_manager.py; `import sys` added; no config dependency
- Deleted local `detect_vendor_from_path` from batch_audit.py; `from src.diagnostics.run_manager import detect_vendor_from_path` import added at line 35; live caller at line 1441 unchanged (already passes `known_vendors`)
- Deleted local `_detect_vendor_from_path` from cluster_audit.py (dead `_run`/`hp_run`/ccw branches gone); `from src.diagnostics.run_manager import detect_vendor_from_path` added; live caller at line 177 updated to pass `known_vendors` explicitly (via `_load_config` + `_get_known_vendors`)
- test_cluster_audit.py: import updated to shared function from run_manager; old `*_run`/`ccw_export` assertions removed (D-14); parametrize table updated to SPLIT/<vendor>/<spec>/ layout contract
- Full pytest suite: 776 passed, 1 xfailed, 0 skipped (skip-gate clear; goldens byte-equal)

## Task Commits

1. **Task 1: Pre-merge equivalence gate** - analysis only (no files modified; gate passed)
2. **Task 2: Extract + delete + update + fix tests** - `d54247b` (refactor)

**Plan metadata:** *(pending)*

## Files Created/Modified
- `spec_classifier/src/diagnostics/run_manager.py` — added `import sys`; added `detect_vendor_from_path(path, known_vendors)` at end of file
- `spec_classifier/batch_audit.py` — deleted local `detect_vendor_from_path` (10 lines); added `from src.diagnostics.run_manager import detect_vendor_from_path` at line 35
- `spec_classifier/cluster_audit.py` — deleted local `_detect_vendor_from_path` (22 lines); added shared import; updated caller to pass `(path, known_vendors)` with explicit `_load_config` + `_get_known_vendors` resolution
- `spec_classifier/tests/test_cluster_audit.py` — removed `_detect_vendor_from_path` from cluster_audit import; added `from src.diagnostics.run_manager import detect_vendor_from_path`; updated parametrize table to SPLIT/<vendor>/ paths; removed `test_detect_vendor_ccw_alias_returns_cisco`; removed `lenovo_run` -> lenovo assertion; added `lenovo_run` -> unknown assertion

## Decisions Made
- D-13 gate passed (3 divergences confirmed, no fourth): hp_run alias treated as part of divergence #2 (different match mechanism), consistent with plan framing of "dead `_run`/`hp_run` branches" vs. "ccw alias" as two separate items among the three
- test_cluster_audit.py updated in the same commit as the production code changes (D-14 consolidation) — no separate test commit needed since this was a refactor (not TDD)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] test_cluster_audit.py imported deleted `_detect_vendor_from_path`**
- **Found during:** Task 2 verification (pytest run after edits)
- **Issue:** `test_cluster_audit.py:15` imported `_detect_vendor_from_path` from `cluster_audit` — function deleted; test collection failed with ImportError
- **Fix:** Updated import to `from src.diagnostics.run_manager import detect_vendor_from_path`; updated test body to call `detect_vendor_from_path` (no underscore); aligned parametrize test cases to SPLIT/<vendor>/ layout (per D-14); removed old `*_run`/`ccw_export` assertions
- **Files modified:** `spec_classifier/tests/test_cluster_audit.py`
- **Verification:** 776 passed, 1 xfailed, 0 skipped
- **Committed in:** `d54247b`

---

**Total deviations:** 1 auto-fixed (Rule 3 — blocking import error)
**Impact on plan:** Fix was required for test suite to run; D-14 explicitly mandated removing the old `_run`/`ccw_export` assertions. No scope creep.

## Issues Encountered
None beyond the blocking import error resolved above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- run_manager.py now has both `create_spec_folder` and `detect_vendor_from_path` — ready for Phase 09-02 (manifest writer adds `write_manifest` as the third helper)
- Both audit modules import from run_manager — any future path-detection changes need only touch one place
- Full pytest suite green (776p/1xf/0s) — clean baseline for remaining Phase 9 plans

## Known Stubs
None.

## Threat Flags
None — no new network endpoints, auth paths, file I/O patterns, or schema changes introduced. Function is pure path-string inspection with no I/O (T-09-01 accepted per plan threat model).

## Self-Check: PASSED

- `spec_classifier/src/diagnostics/run_manager.py` — file exists, contains `detect_vendor_from_path` with required signature
- `spec_classifier/batch_audit.py` — local definition deleted, shared import present
- `spec_classifier/cluster_audit.py` — local definition deleted, shared import present, caller passes `(path, known_vendors)`
- `spec_classifier/tests/test_cluster_audit.py` — updated import and assertions
- Commit `d54247b` exists in git log
- pytest 776 passed, 1 xfailed, 0 skipped

---
*Phase: 09-output-manifest-full-suite-verification*
*Completed: 2026-06-07*
