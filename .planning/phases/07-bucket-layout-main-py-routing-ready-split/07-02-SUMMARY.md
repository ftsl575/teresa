---
phase: 07-bucket-layout-main-py-routing-ready-split
plan: 02
subsystem: routing/main
tags: [main-py, routing, bucket-layout, split, ready, wipe-first]

# Dependency graph
requires:
  - 07-01 (create_spec_folder in run_manager.py)
provides:
  - main.py routing all nine artifacts to SPLIT/<vendor>/<spec>/ and branded to READY/<vendor>/<spec>/Коммерческое предложение_<spec>.xlsx
affects:
  - 07-03 (test realignment — test_output_structure.py, test_cli.py path assertions must update to new bucket layout)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-bucket routing in _run_single: split_folder for nine artifacts, ready_folder for branded workbook"
    - "Dead parameter removal: session_stamp and total_folder stripped from _run_single signature and all call sites"

key-files:
  created: []
  modified:
    - spec_classifier/main.py

key-decisions:
  - "Replace four-symbol run_manager import with single create_spec_folder import — no dead symbols carried forward"
  - "source_filename=input_path.name kept unchanged in generate_branded_spec call — D-07 byte-equality guard preserved"
  - "Batch completion print reworded from 'TOTAL: {total_folder}' to 'Output: {output_dir}' — no behavioral change, wording update only"

# Metrics
duration: ~3min
completed: 2026-06-07
---

# Phase 7 Plan 02: main.py Routing Rewrite Summary

**Rerouted all nine per-spec artifacts to SPLIT/<vendor>/<spec>/ and branded workbook to READY/<vendor>/<spec>/Коммерческое предложение_<spec>.xlsx, stripping all TOTAL/timestamp dead code from main.py (387 lines → 367 lines)**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-06-07T14:08:11Z
- **Completed:** 2026-06-07T14:11:23Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

### Task 1: Update imports and _run_single routing
- Replaced four-symbol `from src.diagnostics.run_manager import (create_run_folder, get_session_stamp, create_total_folder, copy_to_total)` with single `from src.diagnostics.run_manager import create_spec_folder`
- Removed `session_stamp: str = None` and `total_folder: Path = None` parameters from `_run_single` signature (9 params → 7 params)
- Replaced `vendor_base / create_run_folder(...)` with two `create_spec_folder` calls: `split_folder` (SPLIT bucket) and `ready_folder` (READY bucket)
- Routed `run_log_path` and all nine artifact writes to `split_folder`
- Changed branded path from `run_folder / f"{input_path.stem}_branded.xlsx"` to `ready_folder / f"Коммерческое предложение_{input_path.stem}.xlsx"`
- Kept `source_filename=input_path.name` unchanged (D-07 byte-equality guard)
- Removed TOTAL copy block (`copy_to_total` call site deleted)
- Updated summary print from `run_folder` to `split_folder`

### Task 2: Remove TOTAL preamble from batch block
- Deleted `session_stamp = get_session_stamp()`, `vendor_base = ...`, `total_folder = create_total_folder(...)` from batch preamble (3 lines → 1 log line)
- New log line: `"Batch mode: %d files, output_root: %s"`
- Removed `session_stamp=session_stamp` and `total_folder=total_folder` kwargs from `_run_single` call in batch loop
- Removed `session_stamp=None` and `total_folder=None` kwargs from single-file `_run_single` call
- Updated batch completion print from `TOTAL: {total_folder}` to `Output: {output_dir}`

## Task Commits

1. **Task 1: Update _run_single imports and routing** — `4a34852` (feat)
2. **Task 2: Remove TOTAL preamble from batch block** — `c3feaf4` (feat)

## Files Created/Modified

- `spec_classifier/main.py` — Routing rewrite: 387 → 367 lines; create_spec_folder imported; _run_single signature trimmed; SPLIT/READY buckets wired; TOTAL/timestamp dead code removed; Cyrillic branded filename; D-07 guard intact

## Decisions Made

- source_filename=input_path.name kept unchanged per D-07 — only output_path argument changes; branded workbook bytes are unchanged.
- Batch completion print reworded to "Output: {output_dir}" (planner discretion, no behavioral requirement).
- datetime import retained — still used at line 161 for run_timestamp (datetime.now(timezone.utc)).

## Deviations from Plan

None — plan executed exactly as written. All eight changes in Task 1 and four changes in Task 2 applied as specified. All acceptance criteria pass.

## Issues Encountered

None.

## Known Stubs

None — main.py routing is fully wired; no placeholder values or hardcoded empty returns.

## Threat Flags

No new security-relevant surface introduced. Both create_spec_folder calls use string literals "SPLIT" and "READY" as bucket arguments — T-07-05 (D-05 structural constraint) confirmed: "AUDIT" does not appear anywhere in main.py. T-07-04 vendor parameter validation via _get_adapter() is unchanged. T-07-06 source_filename=input_path.name preserved (D-07).

## Next Phase Readiness

- main.py imports cleanly: `python -c "import main; print('OK')"` → OK
- CLI intact: `python main.py --help` → exit 0
- All 16 acceptance criteria pass (grep + import + help)
- Plan 03 (test realignment) can proceed — test_output_structure.py and test_cli.py path assertions reference old `dell_run / run-*` scheme and must be updated to SPLIT/dell/dl1/ and READY/dell/dl1/ layout

---
*Phase: 07-bucket-layout-main-py-routing-ready-split*
*Completed: 2026-06-07*
