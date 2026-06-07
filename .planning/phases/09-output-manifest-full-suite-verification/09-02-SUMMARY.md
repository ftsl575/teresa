---
phase: 09-output-manifest-full-suite-verification
plan: "02"
subsystem: run_manager / main
tags: [manifest, readme, output-structure, russian, idempotent]
dependency_graph:
  requires: ["09-01"]
  provides: ["MANIFEST-01"]
  affects: ["spec_classifier/src/diagnostics/run_manager.py", "spec_classifier/main.py"]
tech_stack:
  added: []
  patterns: ["static module-level constant + thin writer function", "idempotent write_text"]
key_files:
  modified:
    - spec_classifier/src/diagnostics/run_manager.py
    - spec_classifier/main.py
decisions:
  - "write_manifest placed after output_dir resolution and before batch/single dispatch — single call covers both paths"
  - "_MANIFEST_CONTENT defined as module-level constant; write_manifest stays a thin writer with no logic"
  - "output_root.mkdir(parents=True, exist_ok=True) added defensively (belt-and-suspenders; output_dir always pre-exists)"
metrics:
  duration: "~3 minutes"
  completed: "2026-06-07"
  tasks: 2
  files_modified: 2
---

# Phase 9 Plan 02: MANIFEST-01 — Output Manifest Writer Summary

**One-liner:** Static README.md artifact index (14-row Russian-purpose table grouped by READY/SPLIT/AUDIT) written idempotently at output_root on every main() invocation via write_manifest helper in run_manager.py.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Add write_manifest helper to run_manager.py | 9d66e82 | spec_classifier/src/diagnostics/run_manager.py |
| 2 | Wire write_manifest call in main.py | adfeda2 | spec_classifier/main.py |

## What Was Built

### Task 1: write_manifest helper (run_manager.py)

Added two items to `spec_classifier/src/diagnostics/run_manager.py` (appended before `detect_vendor_from_path`):

1. `_MANIFEST_CONTENT` — module-level string constant containing the complete static README.md table. Hardcoded, never dynamically scanned. Groups 14 artifact rows under three headings (READY / SPLIT / AUDIT). Purpose column in Russian (Cyrillic); file names, bucket names, and path structure in original form.

2. `write_manifest(output_root: Path) -> None` — thin writer that coerces the argument to Path, ensures the directory exists (mkdir parents/exist_ok), and writes `output_root / "README.md"` via `write_text(encoding="utf-8")`. Idempotent by construction: subsequent calls overwrite with identical bytes.

Artifact row breakdown:
- READY: 1 row (`Коммерческое предложение_<spec>.xlsx`)
- SPLIT: 9 rows (cleaned_spec, classification.jsonl, annotated, rows_raw, rows_normalized, run_summary, unknown_rows, header_rows, run.log)
- AUDIT: 4 rows (annotated_audited per-spec, audit_report.json root, audit_summary.xlsx root, cluster_summary.xlsx root)
- Total: 14 rows — matches the v1.2 artifact set

### Task 2: Wire call in main.py

Two edits to `spec_classifier/main.py`:

1. Import line extended: `from src.diagnostics.run_manager import create_spec_folder, write_manifest`
2. Call inserted after output_dir resolution (line 284), before the batch/single dispatch: `write_manifest(output_dir)`

Placement ensures exactly one call per `main()` invocation regardless of batch vs. single-file mode. README.md is written before any per-spec work begins, so it is present even if classification fails partway through.

## Verification Results

All automated checks passed:

- `write_manifest: OK` — README.md created with 14 data rows, three bucket sections, Russian text confirmed
- Idempotency confirmed: second call produces byte-identical content
- `main.py wiring: OK` — exactly 1 `write_manifest(output_dir)` call, import line correct
- `import main` exits without ImportError
- `Total write_manifest occurrences: 2` (1 import + 1 call)
- Final smoke test: README.md length 1955 bytes; READY/SPLIT/AUDIT sections present; Russian text confirmed

## Deviations from Plan

None — plan executed exactly as written. The `output_root.mkdir(parents=True, exist_ok=True)` call was specified in the plan's implementation block and was included as written (belt-and-suspenders; not a deviation).

## Known Stubs

None. The manifest table is complete and fully populated with all 14 v1.2 artifact types. No placeholders, TODOs, or empty data sources.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns beyond what the plan's threat model covers. The write target is always `output_root / "README.md"` (fixed filename, not user-supplied). Content is a module-level constant, not interpolated from runtime data. All three T-09-04/05/06 threats are accepted per the plan's threat register.

## Self-Check

Files exist:
- `spec_classifier/src/diagnostics/run_manager.py` — FOUND (contains `_MANIFEST_CONTENT` and `def write_manifest`)
- `spec_classifier/main.py` — FOUND (contains `write_manifest` import and call)

Commits exist:
- `9d66e82` — FOUND (feat(09-02): add write_manifest helper to run_manager.py)
- `adfeda2` — FOUND (feat(09-02): wire write_manifest call in main.py)

## Self-Check: PASSED
