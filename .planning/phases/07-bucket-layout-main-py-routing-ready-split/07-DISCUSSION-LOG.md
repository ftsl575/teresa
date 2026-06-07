# Phase 7: Bucket layout & main.py routing (READY + SPLIT) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-07
**Phase:** 7-Bucket layout & main.py routing (READY + SPLIT)
**Areas discussed:** Re-run stale-file handling, AUDIT bucket scope, run_manager helper disposition, path-construction location

---

## Re-run stale-file handling (LAYOUT-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Wipe spec folder first | rmtree the `<vendor>/<spec>/` dir (in each bucket it writes) at run start, then write fresh — folder reflects exactly this run, no orphaned stale artifacts | ✓ |
| Overwrite file-by-file | Write each artifact over its prior copy; files not produced this run linger from the previous run | |

**User's choice:** Wipe spec folder first
**Notes:** Refined during wrap-up to "wipe only the buckets this process writes" — READY + SPLIT — and explicitly NOT AUDIT (Phase 8 lifecycle). Captured as D-04 / D-05.

---

## AUDIT bucket scope in Phase 7

| Option | Description | Selected |
|--------|-------------|----------|
| Create empty AUDIT/ now | main.py mkdir's all three buckets up-front each run, literally satisfying LAYOUT-01 within Phase 7 | |
| Defer AUDIT to Phase 8 | Phase 7 creates only READY+SPLIT; AUDIT appears when batch_audit runs in Phase 8; LAYOUT-01 satisfied across the milestone | ✓ |

**User's choice:** Defer AUDIT to Phase 8
**Notes:** Captured as D-06.

---

## run_manager.py helper disposition (ROUTE-05 + cleanup)

| Option | Description | Selected |
|--------|-------------|----------|
| Delete dead helpers | Remove copy_to_total + create_total_folder (ROUTE-05) and create_run_folder/get_session_stamp once unused; replace with new bucket helper | ✓ |
| Remove only what ROUTE-05 requires | Delete only copy_to_total + call site (+ create_total_folder); leave create_run_folder/get_session_stamp even if unused | |

**User's choice:** Delete dead helpers
**Notes:** Captured as D-09. Module docstring to be updated.

---

## Path-construction location

| Option | Description | Selected |
|--------|-------------|----------|
| New helper in run_manager.py | Add e.g. create_spec_folder(output_root, bucket, vendor, spec) replacing create_run_folder; path logic centralized + testable | ✓ |
| Inline in main.py | Build paths directly in _run_single with Path joins + mkdir | |

**User's choice:** New helper in run_manager.py
**Notes:** Captured as D-10. Exact signature/name left to Claude's discretion.

---

## Claude's Discretion

- Exact signature/name of the new path helper (`create_spec_folder` suggested).
- Batch-mode summary-line wording after TOTAL removal.
- Enumeration of which path/layout tests need realignment (TEST-01).

## Deferred Ideas

- AUDIT routing (batch_audit/cluster_audit read-from-SPLIT, write-to-AUDIT) — Phase 8 (ROUTE-03/04).
- output_root/README.md manifest + full-suite verification — Phase 9 (MANIFEST-01, TEST-01 final).
- Artifact content changes (column trimming, translation, new summary docs) — v1.3 (CONTENT-01..03).
