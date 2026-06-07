---
phase: 07-bucket-layout-main-py-routing-ready-split
plan: 03
subsystem: tests
tags: [tests, bucket-layout, split, ready, test-realignment]

# Dependency graph
requires:
  - 07-02 (main.py SPLIT/READY routing — tests must assert new paths)
provides:
  - test_output_structure.py asserting SPLIT/<vendor>/<spec>/ and READY/<vendor>/<spec>/ bucket layout
  - test_cli.py asserting SPLIT/dell/dl1/ direct path
  - test_smoke.py importable (create_spec_folder call)
  - Cisco branded bug fixed (generates_branded_spec returns False)
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Direct-path assertions: split_folder = output_root / 'SPLIT' / vendor / stem"
    - "Negative assertions: assert not (output_root / 'dell_run').exists()"

key-files:
  created: []
  modified:
    - spec_classifier/tests/test_output_structure.py
    - spec_classifier/tests/test_cli.py
    - spec_classifier/tests/test_smoke.py
    - spec_classifier/src/vendors/cisco/adapter.py

key-decisions:
  - "cisco/adapter.py generates_branded_spec() fixed to False — base.py docstring explicitly says 'Cisco no'; adapter had True (Rule 1 bug)"
  - "test_smoke.py create_run_folder import replaced with create_spec_folder (Rule 3: blocking collection error)"
  - "Cisco READY negative assertion: assert not dir.is_dir() OR not any(dir.iterdir()) — handles both no-folder and empty-folder cases"

# Metrics
duration: ~8min
completed: 2026-06-07
---

# Phase 7 Plan 03: Test Realignment (SPLIT/READY Bucket Layout) Summary

**Realigned test_output_structure.py and test_cli.py to assert SPLIT/<vendor>/<spec>/ and READY/dell/<spec>/Коммерческое предложение_<spec>.xlsx; fixed Cisco branded bug and test_smoke.py import breakage; full suite 774 passed, 1 xfailed, 0 failed**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-06-07T14:13:00Z
- **Completed:** 2026-06-07T14:19:30Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

### Task 1: Realign test_output_structure.py to bucket layout

- Removed `import re` and `RUN_FOLDER_PATTERN` constant (no longer used after timestamp-folder removal)
- Updated module docstring to describe the new SPLIT/READY bucket structure
- Replaced Dell test assertions: `dell_run / run-*` → `SPLIT/dell/dl1/` + `READY/dell/dl1/Коммерческое предложение_dl1.xlsx`
- Replaced Cisco test assertions: `cisco_run / run-*` → `SPLIT/cisco/ccw_1/` — removed false-positive branded assertion; added negative assertion (Cisco must not produce READY output)
- Replaced `test_output_root_configurable_via_cli` assertions: `dell_run / run-*` glob → `SPLIT/dell/` direct check
- Added negative assertions: `assert not (output_root / "dell_run").exists()` and `assert not (output_root / "cisco_run").exists()`
- All 3 tests collect cleanly: `pytest --collect-only -q` exits 0

### Task 2: Realign test_cli.py + fix blocking issues

- Replaced `dell_run / run-*` path walk with `split_folder = output_dir / "SPLIT" / "dell" / "dl1"` direct assertion
- Fixed `test_smoke.py` import: replaced `create_run_folder` (deleted in Plan 01) with `create_spec_folder`; updated call site to `create_spec_folder(output_root, "SPLIT", "dell", input_path.stem)` (Rule 3 — blocking collection error)
- Fixed `cisco/adapter.py`: `generates_branded_spec()` corrected from `True` to `False` (Rule 1 — bug; base.py docstring states "Cisco no"; test assertion was correct, adapter was wrong)
- Full suite result: **774 passed, 1 xfailed, 0 failed, 0 skipped** in 18.45s
- Skip ratio: 0/774 = 0% — well within the < 50% gate
- Goldens byte-equal: `git diff golden/` shows no changes

## Task Commits

1. **Task 1: Realign test_output_structure.py** — `9d9ddc6` (test)
2. **Task 2: Realign test_cli.py + fix smoke + fix Cisco** — `13a0ea4` (test)

## Files Created/Modified

- `spec_classifier/tests/test_output_structure.py` — Rewritten: removed `import re` + `RUN_FOLDER_PATTERN`; all three tests assert new SPLIT/READY bucket layout; Cisco branded false-positive fixed
- `spec_classifier/tests/test_cli.py` — Surgical change: `dell_run / run-*` path walk replaced with `SPLIT/dell/dl1/` direct path
- `spec_classifier/tests/test_smoke.py` — Import fix: `create_run_folder` → `create_spec_folder` + call site updated (Rule 3 deviation)
- `spec_classifier/src/vendors/cisco/adapter.py` — Bug fix: `generates_branded_spec()` returns `False` (Rule 1 deviation)

## Decisions Made

- cisco/adapter.py generates_branded_spec() was `True` — confirmed bug vs base.py docstring ("e.g. Dell yes, Cisco no"); corrected to `False`.
- test_smoke.py was not in the plan's `files_modified` list but its `create_run_folder` import caused a collection error (ERROR phase) blocking all 770+ other tests — fixed as Rule 3 (blocking issue).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed test_smoke.py import error blocking test collection**
- **Found during:** Task 2 (pre-run verification `pytest --collect-only`)
- **Issue:** `test_smoke.py` imported `create_run_folder` from `run_manager`, which was deleted in Plan 01. The ImportError caused pytest's collection phase to abort with `ERROR` before any tests ran.
- **Fix:** Replaced `from src.diagnostics.run_manager import create_run_folder` with `create_spec_folder`; updated the call site: `create_run_folder(str(vendor_base), input_path.name)` → `create_spec_folder(output_root, "SPLIT", "dell", input_path.stem)`
- **Files modified:** `spec_classifier/tests/test_smoke.py`
- **Commit:** `13a0ea4`

**2. [Rule 1 - Bug] Fixed Cisco adapter generates_branded_spec() returning True**
- **Found during:** Task 2 (pytest run — `test_output_tree_shape_cisco_run` FAILED)
- **Issue:** `cisco/adapter.py:generates_branded_spec()` returned `True`; Cisco was producing a `READY/cisco/ccw_1/Коммерческое предложение_ccw_1.xlsx` file. The test assertion (Cisco must not produce READY output) was correct per spec; the adapter was wrong.
- **Fix:** Changed `return True` to `return False` in `CiscoAdapter.generates_branded_spec()`
- **Files modified:** `spec_classifier/src/vendors/cisco/adapter.py`
- **Commit:** `13a0ea4`

## Known Stubs

None — test assertions are fully wired to the new bucket layout; no placeholder values.

## Threat Flags

No new security-relevant surface introduced. Tests use pytest `tmp_path` (unique OS temp dir per test). T-07-09 (golden tampering) confirmed: `git diff golden/` shows no changes. T-07-10 (skip ratio) confirmed: 0/774 = 0% < 50% gate.

## Self-Check: PASSED

- tests/test_output_structure.py: FOUND
- tests/test_cli.py: FOUND
- tests/test_smoke.py: FOUND
- src/vendors/cisco/adapter.py: FOUND
- Commit 9d9ddc6: FOUND
- Commit 13a0ea4: FOUND
