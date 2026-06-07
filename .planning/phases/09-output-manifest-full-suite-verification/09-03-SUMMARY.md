---
phase: 09-output-manifest-full-suite-verification
plan: "03"
subsystem: tests
tags: [test-consolidation, detect-vendor, manifest, output-structure, suite-verification]

# Dependency graph
requires:
  - phase: 09-output-manifest-full-suite-verification
    plan: "01"
    provides: "run_manager.detect_vendor_from_path (shared function)"
  - phase: 09-output-manifest-full-suite-verification
    plan: "02"
    provides: "run_manager.write_manifest + main.py wiring"
provides:
  - "test_run_manager.py: consolidated detect-vendor + manifest unit tests"
  - "test_batch_audit.py: detect_vendor_from_path removed (D-14)"
  - "test_cluster_audit.py: old detect-vendor section removed (D-14)"
  - "test_output_structure.py: README presence + top-level layout assertions"
  - "09-VERIFICATION.md: full suite green + goldens byte-equal + real-data run documented"
affects:
  - spec_classifier/tests/

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Consolidated test class pattern: single TestDetectVendorFromPath in test_run_manager.py; removed from test_batch_audit.py and test_cluster_audit.py"
    - "Integration test pattern: subprocess main.py + assert (output_root / 'README.md').exists(); pytest.skip if INPUT absent"
    - "Negative layout assertion: assert no legacy *_run/*-TOTAL/run-* dirs; AUDIT/ absent check relaxed (main.py only creates READY+SPLIT)"

key-files:
  created:
    - spec_classifier/tests/test_run_manager.py
    - .planning/phases/09-output-manifest-full-suite-verification/09-VERIFICATION.md
  modified:
    - spec_classifier/tests/test_batch_audit.py
    - spec_classifier/tests/test_cluster_audit.py
    - spec_classifier/tests/test_output_structure.py

key-decisions:
  - "D-14: detect-vendor tests consolidated into test_run_manager.py only; removed from test_batch_audit.py (class deleted) and test_cluster_audit.py (section deleted)"
  - "Layout assertion adjusted: test_output_root_top_level_layout checks READY+SPLIT+README.md required + no legacy dirs; AUDIT/ not asserted absent from main.py run since batch_audit writes it later"
  - "D-09: Real-data operator run completed (dell, 5 files) — output_root tree and README.md contents documented in 09-VERIFICATION.md"

requirements-completed:
  - TEST-01
  - MANIFEST-01

# Metrics
duration: 10min
completed: 2026-06-07
---

# Phase 09 Plan 03: TEST-01 Test Consolidation + Suite Verification Summary

**One-liner:** Consolidated detect-vendor tests into test_run_manager.py (8 detect-vendor + 3 manifest tests), removed old tests from test_batch_audit.py and test_cluster_audit.py, added README/layout assertions to test_output_structure.py; full suite 770 passed / 0 failed / 0 skipped — green within skip-gate; goldens byte-equal; real-data run documented.

## Performance

- **Duration:** ~10 min
- **Started:** 2026-06-07T18:55:24Z
- **Completed:** 2026-06-07
- **Tasks:** 3 (Task 1: create test_run_manager.py; Task 2: update 3 test files; Task 3: auto-approved checkpoint verification)
- **Files modified/created:** 5

## Accomplishments

- Created `spec_classifier/tests/test_run_manager.py` with `TestDetectVendorFromPath` (8 methods, reference contract from test_batch_audit.py) + `test_write_manifest_creates_readme` + `test_write_manifest_idempotent` + `test_write_manifest_creates_output_root_if_missing`
- Removed `detect_vendor_from_path` from `test_batch_audit.py` import; deleted `TestDetectVendorFromPath` class (35 lines)
- Removed detect-vendor test section from `test_cluster_audit.py` (import + `_KNOWN` constant + parametrize + 3 test functions = ~40 lines); removed `from src.diagnostics.run_manager import detect_vendor_from_path` import
- Added `test_manifest_readme_exists_after_run` and `test_output_root_top_level_layout` to `test_output_structure.py`
- Full pytest suite: **770 passed, 1 xfailed, 0 skipped, 0 failed** (skip-gate 0% < 50%; passes > 0)
- Goldens byte-equal: 71 golden/regression tests pass with no `--update-golden`
- Real-data operator run completed and documented in `09-VERIFICATION.md`

## Task Commits

1. **Task 1: Create test_run_manager.py** — `88e93c9` (feat)
2. **Task 2: Update 3 test files** — `048835e` (refactor)

## Files Created/Modified

- `spec_classifier/tests/test_run_manager.py` — NEW: 111 lines; TestDetectVendorFromPath (8 methods) + 3 write_manifest tests; imports from `src.diagnostics.run_manager`
- `spec_classifier/tests/test_batch_audit.py` — removed `detect_vendor_from_path` from import; deleted `TestDetectVendorFromPath` class (lines 434-468); -37 lines net
- `spec_classifier/tests/test_cluster_audit.py` — removed `from src.diagnostics.run_manager import detect_vendor_from_path`; deleted `_KNOWN`, parametrize, 3 detect-vendor test functions (lines 26, 40-77); -40 lines net
- `spec_classifier/tests/test_output_structure.py` — appended `test_manifest_readme_exists_after_run` + `test_output_root_top_level_layout`; +67 lines net
- `.planning/phases/09-output-manifest-full-suite-verification/09-VERIFICATION.md` — NEW: full-suite results + goldens status + real-data run tree + README.md contents

## Decisions Made

- D-14: Consolidated detect-vendor tests into a single suite in `test_run_manager.py`. Tests previously in `test_batch_audit.py` (class `TestDetectVendorFromPath`) moved there. Tests previously in `test_cluster_audit.py` (parametrize + 3 functions, already updated in 09-01 to target run_manager) removed entirely — these are now covered by `test_run_manager.py`.
- Layout assertion scoped correctly: `test_output_root_top_level_layout` checks that `READY/`, `SPLIT/`, and `README.md` are present and no legacy dirs exist; does NOT assert `AUDIT/` must be present (AUDIT is written by batch_audit.py, not main.py).
- D-09: Real-data run used `--batch-dir INPUT/dell --vendor dell` (main.py does not have `--no-ai` flag; AI is not called by default in main.py).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_output_root_top_level_layout: AUDIT/ not present after main.py-only run**
- **Found during:** Task 2 verification (pytest run)
- **Issue:** The test asserted `top_level == {"READY", "SPLIT", "AUDIT", "README.md"}` but after a `main.py` run, `AUDIT/` does not exist (it's created by `batch_audit.py`). The test failed with `AssertionError: AUDIT not in output_root`.
- **Fix:** Changed assertion from exact equality check to required-subset check (READY + SPLIT + README.md required; AUDIT not asserted; negative legacy-dir assertions retained).
- **Files modified:** `spec_classifier/tests/test_output_structure.py`
- **Commit:** `048835e`

---

**Total deviations:** 1 auto-fixed (Rule 1 — incorrect test assertion)

## Issues Encountered

None beyond the test assertion bug resolved above.

## User Setup Required

None.

## Next Phase Readiness

- v1.2 milestone is complete: READY/SPLIT/AUDIT bucket layout delivered (Phase 7), batch_audit + cluster_audit re-pointed (Phase 8), vendor-detector deduped (09-01), manifest writer added (09-02), all tests consolidated and suite green (09-03).
- Full pytest suite baseline: 770 passed / 1 xfailed / 0 skipped — clean for v1.3 content work.
- Ready for `/gsd-verify-work 9` + `/gsd-complete-milestone`.

## Known Stubs

None. All test assertions are complete and functional.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes. Test files only; T-09-07/08/09 accepted per plan threat model.

## Self-Check: PASSED

- `spec_classifier/tests/test_run_manager.py` — FOUND (contains `class TestDetectVendorFromPath`, `test_write_manifest_creates_readme`, `test_write_manifest_idempotent`, `test_write_manifest_creates_output_root_if_missing`)
- `spec_classifier/tests/test_batch_audit.py` — detect_vendor_from_path: 0 references
- `spec_classifier/tests/test_cluster_audit.py` — _detect_vendor_from_path: 0 references; ccw_export: 0 references
- `spec_classifier/tests/test_output_structure.py` — `test_manifest_readme_exists_after_run`: FOUND; `test_output_root_top_level_layout`: FOUND
- `.planning/phases/09-output-manifest-full-suite-verification/09-VERIFICATION.md` — FOUND (770 passed + real-data run documented)
- Commit `88e93c9` — FOUND (feat(09-03): add test_run_manager.py)
- Commit `048835e` — FOUND (refactor(09-03): clean imports + remove detect-vendor tests + add README/layout assertions)
- pytest 770 passed, 1 xfailed, 0 skipped — suite green within skip-gate

---
*Phase: 09-output-manifest-full-suite-verification*
*Completed: 2026-06-07*
