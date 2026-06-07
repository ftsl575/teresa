---
phase: 07-bucket-layout-main-py-routing-ready-split
plan: 01
subsystem: diagnostics/routing
tags: [run_manager, pathlib, shutil, bucket-layout, wipe-first]

# Dependency graph
requires: []
provides:
  - create_spec_folder(output_root, bucket, vendor, spec) -> Path with wipe-first semantics in run_manager.py
affects:
  - 07-02 (main.py routing — imports create_spec_folder from run_manager)
  - 07-03 (any test realignment for path/layout assertions)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Wipe-first bucket creation: rmtree if exists, then mkdir (no exist_ok) — guarantees no stale artifacts survive a re-run"
    - "Centralized path construction in run_manager.py: all bucket/vendor/spec path logic lives in one testable function"

key-files:
  created: []
  modified:
    - spec_classifier/src/diagnostics/run_manager.py

key-decisions:
  - "Delete all four dead helpers (get_session_stamp, create_run_folder, create_total_folder, copy_to_total) and datetime import — no dead code carried forward (D-09)"
  - "create_spec_folder uses no exist_ok on mkdir — wipe-first guarantees the directory is always fresh"

patterns-established:
  - "run_manager.py exports exactly one function: create_spec_folder. No helper sprawl."

requirements-completed:
  - LAYOUT-01
  - LAYOUT-02
  - LAYOUT-03
  - ROUTE-05

# Metrics
duration: 3min
completed: 2026-06-07
---

# Phase 7 Plan 01: run_manager.py Rewrite Summary

**Replaced four timestamp/TOTAL helpers in run_manager.py with a single wipe-first bucket helper (create_spec_folder), shrinking the file from 72 to 32 lines**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-06-07T14:02:24Z
- **Completed:** 2026-06-07T14:05:02Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Rewrote run_manager.py from scratch: new module docstring, two imports (shutil + pathlib.Path), one exported function
- Deleted all dead helpers: get_session_stamp, create_run_folder, create_total_folder, copy_to_total
- Removed datetime import — no timestamp logic remains in the module
- create_spec_folder implements wipe-first semantics: rmtree if exists, mkdir(parents=True) without exist_ok
- All 9 acceptance criteria verified (import check, negative import checks, grep checks, line count)

## Task Commits

1. **Task 1: Rewrite run_manager.py** - `cc27d66` (feat)

## Files Created/Modified

- `spec_classifier/src/diagnostics/run_manager.py` - Rewritten: single export create_spec_folder; all dead helpers and datetime import removed; 32 lines (was 72)

## Decisions Made

None - plan executed exactly as specified. All implementation details (exact function signature, wipe-first semantics, no exist_ok, no default args) were prescribed by the plan.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- create_spec_folder is importable and verified: `python -c "from src.diagnostics.run_manager import create_spec_folder; print('OK')"`
- Plan 02 (main.py routing) can import create_spec_folder immediately — dependency satisfied
- No test breakage: existing tests do not import run_manager directly (verified by negative check — old helpers raise ImportError as expected)

---
*Phase: 07-bucket-layout-main-py-routing-ready-split*
*Completed: 2026-06-07*
